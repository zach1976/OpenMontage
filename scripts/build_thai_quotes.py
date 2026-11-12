#!/usr/bin/env python3
"""泰国人生小语（推广泰语千词）：一集 8–9 句泰语短句 + 中文，泰语女声逐句念，实拍空镜做底。

形式参照 2026-11 用户给的抖音「泰语人生语录」：大字泰语 + 中文、每句 2 秒上下、
泰国实拍空镜、末尾一句打气。文案是我们自己写的，不搬原片句子；
标 [词库] 的整句直接取自 thai1000 已校对例句。

    python3 scripts/build_thai_quotes.py            # 合成配音 + 生成 props（可续跑）
    python3 scripts/build_thai_quotes.py --render   # 再渲染
"""
from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import edge_tts

REPO = Path(__file__).resolve().parent.parent
LANG = "vi" if "--lang=vi" in sys.argv else "th"
CFG = {
    "th": dict(pid="thai-quotes-202611", voice="th-TH-PremwadeeNeural", rate="-12%", outro="泰语千词，在泰国生活够用了",
               column="泰国人生小语", brand="泰语千词", country="泰国", series_id=1, slug="thai_quotes",
               icon="app/app_icon.png", font="zen/fonts/Sarabun-Bold.ttf", tags="#泰语 #泰语学习 #学泰语 #泰国生活 #泰语千词",
               blurb="泰国人挂在嘴边的人生小语"),
    "vi": dict(pid="viet-quotes-202611", voice="vi-VN-HoaiMyNeural", rate="-15%", outro="越南语千词，在越南生活够用了",
               column="越南人生小语", brand="越南语千词", country="越南", series_id=2, slug="viet_quotes",
               icon="app/viet_app_icon.png", font="zen/fonts/BeVietnamPro-Bold.ttf", tags="#越南语 #越南语学习 #学越南语 #越南生活 #越南语千词",
               blurb="越南人挂在嘴边的人生小语"),
}[LANG]
PID = CFG["pid"]
PROJECT = REPO / "projects" / PID
PUBLIC = REPO / "remotion-composer" / "public"
MEDIA = f"series/{PID}"
TH_VOICE, TH_RATE = CFG["voice"], CFG["rate"]
ZH_VOICE, ZH_RATE = "zh-CN-XiaoxiaoNeural", "+0%"
OUTRO_ZH = CFG["outro"]
BGM_SRC = REPO / "projects" / "thai-zen-01-impermanence-v2" / "assets" / "music"
TITLE_RE = re.compile(r"^[一-鿿0-9]{6,16}$")

# (集, 标题, 封面上行, 封面下行, 主色, 入场动效, 空镜, 垫乐, [(泰语, 中文)])
TH_EPISODES = [
    ("ep01", "泰国人常说的没关系", "泰国人常说", "没关系", "#F4B740", "rise",
     ["scene_watarun", "scene_lake1", "scene_sunrise"], "warm_gtr.mp3", [
         ("ฝนตกก็ไม่เป็นไร", "下雨了，没关系"),
         ("รถติดก็ไม่เป็นไร", "堵车了，没关系"),
         ("พูดผิดก็ไม่เป็นไร", "说错了，没关系"),
         ("วันนี้ไม่ได้", "今天没做到"),
         ("พรุ่งนี้ลองใหม่", "明天再试一次"),
         ("ใจเย็นๆ", "别着急"),
         ("ยิ้มเข้าไว้", "多笑一笑"),
         ("ชีวิตไม่ต้องรีบ", "人生不用赶"),
         ("ไม่เป็นไรนะ", "没关系的"),
     ]),
    ("ep02", "泰国人的松弛感慢慢来", "泰国人的松弛感", "慢慢来", "#7FD8B2", "slide",
     ["scene_lake2", "scene_mountain", "scene_flowers"], "fresh_uku.mp3", [
         ("กินข้าว ค่อยๆ กิน", "饭，慢慢吃"),
         ("ทำงาน ค่อยๆ ทำ", "活，慢慢干"),
         ("เรียนภาษา ค่อยๆ เรียน", "语言，慢慢学"),
         ("ความรักไม่ต้องรีบ", "爱情不用急"),
         ("ไม่ต้องเก่งทุกเรื่อง", "不必样样都强"),
         ("ไม่ต้องเหมือนใคร", "不必和谁一样"),
         ("ช้าๆ ได้พร้าเล่มงาม", "慢工出细活"),
         ("ค่อยๆ ไป", "慢慢来"),
     ]),
    ("ep03", "泰国人这样给你打气", "泰国人这样", "给你打气", "#FF8F5E", "pop",
     ["scene_city", "scene_waterfall", "scene_sakura"], "fresh_guitar.mp3", [
         ("เหนื่อยก็พักก่อน", "累了就先歇歇"),
         ("พักแล้วค่อยไปต่อ", "歇好了再走"),
         ("ร้องไห้ได้", "可以哭"),
         ("แต่อย่ายอมแพ้", "但别认输"),
         ("วันนี้แย่", "今天很糟"),
         ("พรุ่งนี้ยังมี", "还有明天"),
         ("ทำเต็มที่ก็พอ", "尽力就够了"),
         ("เราทำได้", "我们做得到"),
         ("สู้ๆ นะ", "加油哦"),
     ]),
    ("ep04", "泰国人的活法开心就好", "泰国人的活法", "开心就好", "#FFD45C", "focus",
     ["scene_lantern2", "scene_flowers", "scene_lake1"], "fresh_folk.mp3", [
         ("กินอิ่ม นอนหลับ", "吃得饱，睡得香"),
         ("เขาจนแต่มีความสุข", "他虽穷，但快乐"),          # [词库] จน
         ("เพื่อนน้อยแต่จริงใจ", "朋友少，但真心"),
         ("บ้านเล็กแต่อบอุ่น", "家不大，但温暖"),
         ("ชีวิตสั้นมาก", "人生很短"),
         ("สนุกก็พอ", "开心就够了"),
         ("คนไทยชอบยิ้มให้กัน", "泰国人爱对彼此笑"),      # [词库] ยิ้ม
         ("สบายๆ", "放轻松"),
     ]),
    ("ep05", "泰国人眼里家最重要", "泰国人眼里", "家最重要", "#F59AB0", "wipe",
     ["scene_buddha", "scene_lantern1", "scene_sunrise"], "warm_piano.mp3", [
         ("เหนื่อยก็กลับบ้าน", "累了就回家"),
         ("ที่บ้านมีคนรอ", "家里有人等你"),
         ("โทรหาแม่บ้างนะ", "记得给妈妈打电话"),
         ("กินข้าวด้วยกัน", "一起吃顿饭"),
         ("พ่อแม่อยากเห็นเรายิ้ม", "爸妈只想看你笑"),
         ("เวลาผ่านไปไม่กลับมา", "时间过去不会回来"),
         ("ฉันรักครอบครัวของฉัน", "我爱我的家人"),      # [词库] รัก
         ("กลับบ้านกันเถอะ", "回家吧"),
     ]),
    ("ep06", "泰国人见面先问吃了吗", "泰国人见面", "先问吃了吗", "#FF9B54", "rise",
     ["scene_city", "scene_lantern2", "scene_flowers"], "fresh_uku.mp3", [
         ("กินข้าวหรือยัง", "吃饭了吗"),
         ("หิวก็กินก่อน", "饿了就先吃"),
         ("อิ่มแล้วค่อยคุย", "吃饱再聊"),
         ("อร่อยไหม", "好吃吗"),
         ("อร่อยมาก", "很好吃"),
         ("กินด้วยกันนะ", "一起吃吧"),
         ("เหนื่อยแค่ไหนก็ต้องกิน", "再累也要吃饭"),
         ("กินให้อิ่มนะ", "要吃饱哦"),
     ]),
    ("ep07", "泰国人这样对朋友说", "泰国人这样", "对朋友说", "#6FC3F2", "slide",
     ["scene_sakura", "scene_lake2", "scene_sunrise"], "warm_folk.mp3", [
         ("เพื่อนกันไม่ทิ้งกัน", "朋友不离不弃"),
         ("มีอะไรบอกนะ", "有事跟我说"),
         ("ไม่ต้องเกรงใจ", "别客气"),
         ("คิดถึงนะ", "想你了"),
         ("ไปเที่ยวกันไหม", "一起去玩吗"),
         ("ฉันอยู่ตรงนี้", "我就在这里"),
         ("ขอบคุณที่อยู่ด้วยกัน", "谢谢你一直在"),
         ("เพื่อนรัก", "好朋友"),
     ]),
    ("ep08", "泰国人的情话这样说", "泰国人的情话", "这样说", "#FF8FB1", "focus",
     ["scene_lantern1", "scene_lake1", "scene_sakura"], "warm_piano.mp3", [
         ("รักนะ", "爱你哦"),
         ("คิดถึงทุกวัน", "每天都想你"),
         ("กินข้าวยัง", "吃饭了没"),
         ("ถึงบ้านแล้วบอกนะ", "到家了说一声"),
         ("ฝันดีนะ", "晚安好梦"),
         ("เธอคือคนสำคัญ", "你是我最重要的人"),
         ("อยู่ด้วยกันตลอดไป", "要永远在一起"),
         ("รักเธอคนเดียว", "只爱你一个"),
     ]),
    ("ep09", "泰国上班族的口头禅", "泰国上班族", "口头禅", "#9BD36A", "pop",
     ["scene_city", "scene_mountain", "scene_sunrise"], "fresh_guitar.mp3", [
         ("ตื่นเช้าอีกแล้ว", "又要早起了"),
         ("กาแฟก่อน", "先来杯咖啡"),
         ("ทำงานไปยิ้มไป", "边上班边微笑"),
         ("เงินเดือนออกแล้ว", "发工资了"),
         ("วันศุกร์แล้ว", "终于星期五了"),
         ("พักบ้างนะ", "也要歇一歇"),
         ("ทำดีได้ดี", "好人有好报"),
         ("วันนี้เก่งมาก", "今天你很棒"),
     ]),
    ("ep10", "泰国人说走就走去旅行", "泰国人说走", "就走", "#4FD1C5", "wipe",
     ["coverr_island", "scene_waterfall", "scene_watarun"], "fresh_folk.mp3", [
         ("วันนี้อากาศดีมาก", "今天天气真好"),
         ("ออกไปเที่ยวกัน", "出去玩吧"),
         ("ทะเลรออยู่", "大海在等我们"),
         ("ถ่ายรูปกันหน่อย", "拍张照吧"),
         ("ชีวิตต้องมีวันหยุด", "人生要有假期"),
         ("ไม่ต้องคิดมาก", "别想太多"),
         ("สนุกให้เต็มที่", "尽情玩"),
         ("ไปกันเลย", "走吧"),
     ]),
]

VI_EPISODES = [
    ("ep01", "越南人常说的没关系", "越南人常说", "没关系", "#F4B740", "rise",
     ["vn_market", "scene_lake1", "scene_sunrise"], "warm_gtr.mp3", [
         ("Trời mưa, không sao đâu", "下雨了，没关系"),
         ("Kẹt xe, không sao đâu", "堵车了，没关系"),
         ("Nói sai, không sao đâu", "说错了，没关系"),
         ("Hôm nay chưa được", "今天还没做到"),
         ("Ngày mai thử lại", "明天再试一次"),
         ("Bình tĩnh nhé", "别着急"),
         ("Cười lên nào", "笑一笑"),
         ("Không sao đâu", "没关系的"),
     ]),
    ("ep02", "越南人的松弛感慢慢来", "越南人的松弛感", "慢慢来", "#7FD8B2", "slide",
     ["scene_lake2", "scene_mountain", "coverr_road"], "fresh_uku.mp3", [
         ("Ăn cơm, từ từ ăn", "饭，慢慢吃"),
         ("Làm việc, từ từ làm", "活，慢慢干"),
         ("Học tiếng Việt, từ từ học", "越南语，慢慢学"),
         ("Yêu ai, đừng vội", "爱一个人，别着急"),
         ("Không cần giỏi mọi thứ", "不必样样都强"),
         ("Không cần giống ai", "不必和谁一样"),
         ("Chậm mà chắc", "慢慢来，更稳"),
         ("Từ từ thôi", "慢慢来"),
     ]),
    ("ep03", "越南人这样给你打气", "越南人这样", "给你打气", "#FF8F5E", "pop",
     ["coverr_road", "scene_waterfall", "scene_sunrise"], "fresh_guitar.mp3", [
         ("Mệt thì nghỉ một chút", "累了就歇一会"),
         ("Nghỉ xong rồi đi tiếp", "歇好了再走"),
         ("Khóc cũng được", "哭也可以"),
         ("Nhưng đừng bỏ cuộc", "但别放弃"),
         ("Hôm nay tệ quá", "今天很糟"),
         ("Vẫn còn ngày mai", "还有明天"),
         ("Cố hết sức là đủ", "尽力就够了"),
         ("Cố lên nhé", "加油哦"),
     ]),
    ("ep04", "越南人的活法开心就好", "越南人的活法", "开心就好", "#FFD45C", "focus",
     ["scene_lantern2", "vn_market", "scene_flowers"], "fresh_folk.mp3", [
         ("Ăn no, ngủ ngon", "吃得饱，睡得香"),
         ("Ít tiền vẫn vui", "钱少也开心"),
         ("Bạn ít nhưng thật lòng", "朋友少，但真心"),
         ("Nhà nhỏ nhưng ấm áp", "家不大，但温暖"),
         ("Cuộc đời ngắn lắm", "人生很短"),
         ("Cười nhiều lên", "多笑一笑"),
         ("Vui là được", "开心就好"),
     ]),
    ("ep05", "越南人眼里家最重要", "越南人眼里", "家最重要", "#F59AB0", "wipe",
     ["scene_lantern1", "coverr_island", "scene_sunrise"], "warm_piano.mp3", [
         ("Mệt thì về nhà", "累了就回家"),
         ("Ở nhà có người chờ", "家里有人等你"),
         ("Gọi cho mẹ nhé", "记得给妈妈打电话"),
         ("Cùng nhau ăn cơm", "一起吃顿饭"),
         ("Bố mẹ chỉ muốn con vui", "爸妈只想你开心"),
         ("Thời gian không quay lại", "时间不会回来"),
         ("Về nhà thôi", "回家吧"),
     ]),
]
EPISODES = VI_EPISODES if LANG == "vi" else TH_EPISODES

COVER_HOLD = 1.0      # 第 0 帧就是封面，停 1 秒再进第一句
LEAD = 0.18           # 句子先上屏，再出声
GAP = 0.62            # 每句念完后的留白
OUTRO_LEN = 3.6


def dur(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


async def _save(text: str, voice: str, rate: str, out: Path) -> None:
    await asyncio.wait_for(edge_tts.Communicate(text, voice, rate=rate).save(str(out)), 60)


def tts(text: str, voice: str, rate: str, out: Path) -> None:
    """edge-tts 合成；带语速时某些句子会稳定 NoAudioReceived —— 兜底用 +0% 合成再 atempo 放慢（不变调）。"""
    if out.exists() and out.stat().st_size > 2000:
        return
    tempo = 1 + int(rate.rstrip("%")) / 100
    for attempt in range(10):  # 串行 + 退避，不并发（会被限流）
        use_rate = rate if attempt % 2 == 0 else "+0%"
        tmp = out.with_suffix(".tmp.mp3")
        try:
            asyncio.run(_save(text, voice, use_rate, tmp))
            if tmp.stat().st_size > 2000:
                if use_rate == "+0%" and abs(tempo - 1) > 1e-6:
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af", f"atempo={tempo:.3f}",
                                    "-b:a", "96k", str(out)], check=True)
                    tmp.unlink()
                else:
                    tmp.rename(out)
                return
        except Exception as e:  # noqa: BLE001
            print(f"    · 重试 {attempt + 1}（{use_rate}）: {type(e).__name__}", flush=True)
        time.sleep(4 + attempt * 6)
    raise RuntimeError(f"TTS 失败：{text}")


def bgm_for(name: str, out: Path) -> None:
    """垫乐先归一到 −13.8dB 再用（各曲原始电平差十几 dB）。"""
    if out.exists():
        return
    src = BGM_SRC / name
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    mean = float(re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr).group(1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", f"volume={-13.8 - mean:.2f}dB",
                    "-ar", "44100", str(out)], check=True)


def build_episode(ep) -> dict:
    eid, title, t1, t2, accent, motion, scenes, bgm, lines = ep
    assert TITLE_RE.match(title), title
    assert len(t1) + len(t2) <= 12, (t1, t2)
    for th, zh in lines:
        assert len(zh.replace("，", "")) <= 14, zh
    media_dir = PUBLIC / MEDIA / eid
    media_dir.mkdir(parents=True, exist_ok=True)

    t = COVER_HOLD
    items, speech, mix_inputs = [], [], []
    for i, (th, zh) in enumerate(lines):
        mp3 = media_dir / f"l{i:02d}.mp3"
        tts(th, TH_VOICE, TH_RATE, mp3)
        d = dur(mp3)
        a0 = t + LEAD
        items.append({"thai": th, "chinese": zh, "start": round(t, 3), "end": round(a0 + d + GAP, 3),
                      "audioAt": round(a0, 3)})
        speech.append({"start": round(a0, 3), "end": round(a0 + d, 3)})
        mix_inputs.append((mp3, a0))
        t = a0 + d + GAP
    outro_start = t
    zh_mp3 = media_dir / "outro.mp3"
    tts(OUTRO_ZH, ZH_VOICE, ZH_RATE, zh_mp3)
    oa = outro_start + 0.35
    speech.append({"start": round(oa, 3), "end": round(oa + dur(zh_mp3), 3)})
    mix_inputs.append((zh_mp3, oa))
    total = max(outro_start + OUTRO_LEN, oa + dur(zh_mp3) + 0.8)

    # 纯人声轨：给 Remotion 播，也给有声自查用
    wav = media_dir / "narration.wav"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for f, _ in mix_inputs:
        cmd += ["-i", str(f)]
    chains = [f"[{k}:a]aresample=44100,adelay={int(at * 1000)}|{int(at * 1000)}[a{k}]" for k, (_, at) in enumerate(mix_inputs)]
    cmd += ["-filter_complex", ";".join(chains) + ";" + "".join(f"[a{k}]" for k in range(len(mix_inputs)))
            + f"amix=inputs={len(mix_inputs)}:normalize=0,apad=whole_dur={total:.3f}[out]",
            "-map", "[out]", "-ac", "2", "-ar", "44100", str(wav)]
    subprocess.run(cmd, check=True)
    bgm_for(bgm, media_dir / "bgm.mp3")

    seg = total / len(scenes)
    props = {
        "episode": eid, "coverT1": t1, "coverT2": t2, "accent": accent, "motion": motion,
        "column": CFG["column"], "brand": CFG["brand"], "country": CFG["country"], "fontFile": CFG["font"], "durationSeconds": round(total, 3), "outroStart": round(outro_start, 3),
        "coverHold": COVER_HOLD, "items": items, "speechRanges": speech,
        "narrationSrc": f"{MEDIA}/{eid}/narration.wav", "bgmSrc": f"{MEDIA}/{eid}/bgm.mp3", "bgmGain": 0.1,
        "scenes": [{"src": f"zen/scenes/{s}.mp4", "start": round(k * seg, 3), "end": round((k + 1) * seg, 3),
                    "srcDur": round(dur(PUBLIC / "zen" / "scenes" / f"{s}.mp4"), 3)} for k, s in enumerate(scenes)],
        "appIconSrc": CFG["icon"],
    }
    comp = PROJECT / "composition" / eid
    comp.mkdir(parents=True, exist_ok=True)
    (comp / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=1))
    return {"episode_id": eid, "title": title, "lines": [{"thai": a, "chinese": b} for a, b in lines],
            "cover": [t1, t2], "duration": round(total, 1), "props": props}


def publish_meta(ep, built) -> dict:
    eid, title = ep[0], ep[1]
    body = "\n".join(f"{x['thai']}  {x['chinese']}" for x in built["lines"])
    copy = (f"{title}\n{CFG['blurb']}，听一遍、跟一句，慢慢就会说了。\n\n{body}\n\n{CFG['tags']}")
    return {"episode_id": eid, "series_id": CFG["series_id"], "sub_series": CFG["column"], "slug": f"{CFG['slug']}_{eid}",
            "title": title, "publish_copy": copy, "video_path": f"renders/{eid}.mp4",
            "cover_path": f"renders/{eid}_cover.jpg", "idea_notes": f"参照抖音「泰语人生语录」形式，文案自写；推广{CFG['brand']}"}


def corpus_check() -> None:
    """列出每句里命中的 app 词条（越长越先），方便人工核对实词都在词库里。"""
    f = sorted((Path.home() / "projects/lang1000/backups/sync_words").glob("thai1000_*_all.json"))[-1]
    words = sorted({w["target_text"] for w in json.loads(f.read_text())}, key=len, reverse=True)
    for ep in EPISODES:
        for th, _ in ep[8]:
            s, hits = th.replace(" ", ""), []
            for w in words:
                if len(w) > 1 and w in s:
                    hits.append(w)
                    s = s.replace(w, "·")
            print(f"  {ep[0]} {th:24} 词条: {' / '.join(hits)}   剩: {s.replace('·', '')}")


def main() -> int:
    if "--check" in sys.argv:
        corpus_check()
        return 0
    (PROJECT / "artifacts").mkdir(parents=True, exist_ok=True)
    built, metas = [], []
    for ep in EPISODES:
        print(f"· {ep[0]} {ep[1]}", flush=True)
        b = build_episode(ep)
        built.append({k: v for k, v in b.items() if k != "props"})
        metas.append(publish_meta(ep, b))
        print(f"  {b['duration']}s", flush=True)
    (PROJECT / "artifacts" / "script.json").write_text(json.dumps({"episodes": built}, ensure_ascii=False, indent=1))
    (PROJECT / "artifacts" / "publish_batch.json").write_text(json.dumps({"episodes": metas}, ensure_ascii=False, indent=1))
    if "--render" in sys.argv:
        (PROJECT / "renders").mkdir(exist_ok=True)
        for ep in EPISODES:
            out = PROJECT / "renders" / f"{ep[0]}.mp4"
            if out.exists() and "--force" not in sys.argv:
                continue
            props = (PROJECT / "composition" / ep[0] / "props.json").read_text()
            print(f"RENDER {ep[0]}", flush=True)
            subprocess.run(["npx", "remotion", "render", "src/index.tsx", "ThaiQuotes", str(out), "--props",
                            json.dumps(json.loads(props), ensure_ascii=False), "--codec", "h264", "--crf", "20",
                            "--pixel-format", "yuv420p", "--audio-codec", "aac", "--concurrency", "4",
                            "--timeout=120000"], cwd=REPO / "remotion-composer", check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
