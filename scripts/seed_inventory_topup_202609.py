#!/usr/bin/env python3
"""Seed the approved Thai/Vietnamese ready-queue top-up batch."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MUSIC = "projects/thai-1000-dialogue-01-ao/assets/music/bgm.mp3"

COVER_TITLES = {
    ("th", "听力测验", 14): "餐厅词听力", ("th", "场景短句", 21): "泰国寄快递",
    ("th", "怎么称呼", 6): "商店里面如何称呼店员", ("th", "情景对话", 5): "咖啡少甜少冰",
    ("th", "情景对话", 6): "酒店延迟退房", ("th", "招牌识字", 18): "泰国提示牌",
    ("th", "泰国人的英文名", 6): "英文名泰式读法",
    ("vi", "听力测验", 17): "越南美食听力", ("vi", "听力测验", 18): "越南交通听力",
    ("vi", "听力测验", 19): "越南酒店听力", ("vi", "场景短句", 19): "越南寄快递",
    ("vi", "情景对话", 5): "越南咖啡点单", ("vi", "情景对话", 6): "越南酒店退房",
    ("vi", "数数", 20): "越南日期时间", ("vi", "禅意一句", 8): "累了就休息",
    ("vi", "禅意一句", 9): "慢慢走", ("vi", "禅意一句", 10): "学会放下",
    ("vi", "紧急应急", 14): "被困电梯", ("vi", "经典口头禅", 12): "约朋友怎么说",
    ("vi", "经典口头禅", 13): "委婉拒绝", ("vi", "越南名字", 8): "越南名字Anh",
    ("vi", "越南称呼", 7): "餐厅怎么叫人", ("vi", "越南美食", 10): "越南甜汤",
}


def items(*rows: tuple[str, str, str]) -> list[dict]:
    return [{"thai": a, "homophone": b, "chinese": c} for a, b, c in rows]


COFFEE_ANALYSIS = items(
    ("หวาน + น้อย", "万 + 诺伊", "หวาน是甜，น้อย是少，合起来就是少甜"),
    ("ไม่ใส่ + น้ำตาล", "麦 赛 + 南丹", "ไม่ใส่是不放，น้ำตาล是糖"),
    ("น้ำ + แข็ง", "南 + 康", "น้ำ是水，แข็ง是硬，合起来就是冰"),
    ("เอา + กลับบ้าน", "奥 + 格拉 班", "เอา是要，กลับบ้าน是回家，点单时表示打包带走"),
    ("จ่ายด้วย + บัตร", "柴 对 + 巴", "จ่ายด้วย是用来支付，บัตร是卡"),
)
for row, spoken in zip(COFFEE_ANALYSIS, (
    "第一个词是甜，第二个词是少，合起来就是少甜。",
    "前半句是不放，后面的词是糖，合起来就是不加糖。",
    "第一个词是水，第二个词是硬，合起来就是冰。",
    "前面是要，后面是回家，点单时表示打包带走。",
    "前半句表示用来支付，后面的词是卡，合起来就是用卡支付。",
)):
    row["spoken_chinese"] = spoken

ENGLISH_NAME_ANALYSIS = items(
    ("เจมส์ / ไมค์", "静音符", "์ 标记的辅音通常不发音"),
    ("เกรซ", "尾音规则", "词尾 ซ 常收成短促的 t 音"),
    ("มาร์ค", "长音收尾", "า 拉长，末尾 ค 短促收音"),
    ("ฟิล์ม", "鼻音收尾", "末尾收 m 音，ล์ 中的 ล 不读"),
)
for row, spoken in zip(ENGLISH_NAME_ANALYSIS, (
    "看到字母上方的静音符，被标记的辅音通常不发音。所以杰姆斯和麦克的结尾，不会完整读出来。",
    "泰语尾音按自己的规则收音。这个词结尾的ซ，常收成短促的t音，不会完全照英语的z来读。",
    "这个名字中间的า要拉长，末尾的ค短促收音，所以听起来更像马克。",
    "泰语常保留自然的鼻音收尾。这个名字最后收m音，ล上方有静音符，所以ล不读。",
)):
    row["spoken_chinese"] = spoken


TH = [
    ("听力测验", 14, "餐厅词听力测验", "听发音，猜中这5个餐厅词", "#3566A8", "#F3C95F", items(
        ("เมนู", "梅努", "菜单"), ("ช้อน", "乔恩", "勺子"), ("ส้อม", "所姆", "叉子"), ("จาน", "占", "盘子"), ("เช็กบิล", "切克宾", "结账"))),
    ("场景短句", 21, "在泰国寄快递", "在泰国寄快递，最常用的5句话", "#178879", "#FFD36F", items(
        ("อยากส่งพัสดุ", "雅 送 帕萨都", "想寄包裹"), ("ส่งไปจีน", "送 拜 金", "寄到中国"), ("ค่าส่งเท่าไหร่", "卡 送 套来", "运费多少"), ("ใช้เวลากี่วัน", "柴 威拉 给 万", "要几天"), ("มีเลขติดตามไหม", "米 雷克 迪达 麦", "有追踪单号吗"))),
    ("怎么称呼", 6, "在店里怎么称呼别人", "在泰国店里叫人，别只会说你好", "#7B5AA6", "#F0C76A", items(
        ("พี่", "披", "哥哥姐姐、称呼年长者"), ("น้อง", "农", "弟弟妹妹、称呼年幼者"), ("คุณ", "坤", "您、礼貌称呼"), ("เจ้าของร้าน", "早 孔 兰", "店主"), ("พนักงาน", "帕那安", "店员"))),
    ("情景对话", 5, "咖啡少甜怎么说", "在泰国咖啡店，少甜少冰这样说", "#168493", "#F5C45A", items(
        ("หวานน้อย", "万 诺伊", "少甜"), ("ไม่ใส่น้ำตาล", "麦 赛 南丹", "不加糖"), ("ใส่น้ำแข็งน้อย", "赛 南康 诺伊", "少冰"), ("เอากลับบ้าน", "奥 格拉 班", "打包带走"), ("จ่ายด้วยบัตรได้ไหม", "柴 对 巴 达 麦", "可以刷卡吗"))),
    ("情景对话", 6, "酒店延迟退房", "在泰国酒店，延迟退房这样说", "#168493", "#F5C45A", items(
        ("เช็กเอาต์กี่โมง", "切克奥 给 蒙", "几点退房"), ("ขอเช็กเอาต์ช้าได้ไหม", "考 切克奥 查 戴 麦", "可以延迟退房吗"), ("ฝากกระเป๋าได้ไหม", "发 格包 戴 麦", "可以寄存行李吗"), ("ห้องมีปัญหา", "洪 米 班哈", "房间有问题"), ("ช่วยเรียกแท็กซี่ให้หน่อย", "处艾 里亚 泰克西 海 诺伊", "请帮我叫出租车"))),
    ("招牌识字", 18, "常见提示牌", "在泰国看到这5块牌，马上看懂", "#C9473B", "#F4C95D", items(
        ("รับเฉพาะเงินสด", "拉 查泡 恩索", "只收现金"), ("เงินสดเท่านั้น", "恩索 套南", "仅限现金"), ("งดใช้ลิฟต์", "诺 柴 利", "暂停使用电梯"), ("กรุณาปิดประตู", "嘎如那 毕 巴度", "请关门"), ("ระวังขั้นบันได", "拉旺 坎 班代", "小心台阶"))),
    ("泰国人的英文名", 6, "英文名的泰式读法", "这些英文名，泰国人会这样念", "#A45C7C", "#F1C66A", items(
        ("เจมส์", "占", "James"), ("เกรซ", "格雷", "Grace"), ("ไมค์", "麦", "Mike"), ("มาร์ค", "马克", "Mark"), ("ฟิล์ม", "Film", "Film（泰国常见昵称）"))),
]

for sign_item, image_name in zip(TH[5][6], (
    "sign_cash_only_cafe.png", "sign_cash_only_shop.png", "sign_elevator.png",
    "sign_close_door.png", "sign_stairs.png",
)):
    sign_item["imageSrc"] = f"series/thai-inventory-topup-202609/ep06/{image_name}"

VI = [
    ("听力测验", 17, "美食词听力测验", "听发音，猜中这5个越南美食词", "#3066A6", "#F3C95F", items(("cơm", "哥姆", "米饭"), ("phở", "佛", "河粉"), ("bánh mì", "班米", "越式法包"), ("cà phê", "嘎啡", "咖啡"), ("nước", "诺克", "水"))),
    ("听力测验", 18, "交通词听力测验", "听发音，猜中这5个越南交通词", "#3066A6", "#F3C95F", items(("xe máy", "塞 麦", "摩托车"), ("ô tô", "欧多", "汽车"), ("xe buýt", "塞 比特", "公交车"), ("tàu hỏa", "道 火", "火车"), ("máy bay", "麦 拜", "飞机"))),
    ("听力测验", 19, "酒店词听力测验", "听发音，猜中这5个越南酒店词", "#3066A6", "#F3C95F", items(("phòng", "房", "房间"), ("chìa khóa", "匙呀 跨", "钥匙"), ("lễ tân", "礼 新", "前台"), ("thang máy", "汤 麦", "电梯"), ("hành lý", "行 李", "行李"))),
    ("场景短句", 19, "在越南寄快递", "在越南寄快递，这5句先学会", "#168A80", "#FFD36F", items(("Tôi muốn gửi bưu kiện", "多伊 木恩 贵 不件", "我想寄包裹"), ("Gửi sang Trung Quốc", "贵 桑 中郭", "寄到中国"), ("Phí gửi bao nhiêu", "费 贵 包妞", "运费多少"), ("Mất bao lâu", "马 包捞", "要多久"), ("Có mã theo dõi không", "果 马 特奥 佐伊 空", "有追踪单号吗"))),
    ("情景对话", 5, "越南咖啡店点单", "在越南咖啡店，少糖打包这样说", "#157E91", "#F5C45A", items(("Cho tôi một cà phê sữa", "召 多伊 木 嘎啡 丝呀", "给我一杯越南奶咖"), ("Ít đường thôi", "一特 堂 托伊", "少糖"), ("Không đá", "空 打", "不加冰"), ("Mang đi", "芒 低", "打包带走"), ("Thanh toán bằng thẻ được không", "汤 算 崩 特 得 空", "可以刷卡吗"))),
    ("情景对话", 6, "越南酒店退房", "在越南酒店，延迟退房这样说", "#157E91", "#F5C45A", items(("Mấy giờ trả phòng", "美 约 茶 房", "几点退房"), ("Tôi trả phòng muộn được không", "多伊 茶 房 木恩 得 空", "可以延迟退房吗"), ("Gửi hành lý được không", "贵 行 李 得 空", "可以寄存行李吗"), ("Phòng có vấn đề", "房 果 问 得", "房间有问题"), ("Gọi taxi giúp tôi", "戈伊 taxi 族 多伊", "请帮我叫出租车"))),
    ("数数", 20, "日期时间怎么说", "越南语日期时间，这5句最常用", "#6B5AB5", "#F2C65E", items(("Hôm nay ngày mấy", "home nay ngai may", "今天几号"), ("Ngày mai là ngày bao nhiêu", "ngai mai la ngai bao nyew", "明天几号"), ("Mấy giờ rồi", "may yaw zoi", "几点了"), ("Bảy giờ rưỡi", "百 约 吕", "七点半"), ("Mười lăm phút", "木易 兰 福", "十五分钟"))),
    ("禅意一句", 8, "累了就休息", "累了可以休息，但别放弃", "#3D7465", "#F0C76A", items(("Mệt thì nghỉ", "麦 提 尼", "累了就休息"), ("Đừng bỏ cuộc", "等 博 郭", "不要放弃"), ("Chậm một chút cũng được", "沾 木 竹 共 得", "慢一点也可以"), ("Nghỉ xong đi tiếp", "尼 松 低 接", "休息完继续走"), ("Bạn đã cố gắng rồi", "半 打 固 岗 若伊", "你已经很努力了"))),
    ("禅意一句", 9, "慢慢走也算前进", "不必快，只要不停", "#3D7465", "#F0C76A", items(("Không cần nhanh", "空 根 宁", "不必快"), ("Chỉ cần không dừng", "几 根 空 用", "只要不停"), ("Mỗi ngày một chút", "美 艾 木 竹", "每天一点点"), ("Đi chậm vẫn là đi", "低 沾 文 拉 低", "慢慢走也是走"), ("Cứ tiếp tục nhé", "格 接 俗 涅", "继续走吧"))),
    ("禅意一句", 10, "学会放下", "放下以后，心会更轻松", "#3D7465", "#F0C76A", items(("Bình yên", "平 安", "平静"), ("Buông bỏ", "波翁 博", "放下"), ("Không giữ mãi", "空 字 买", "不一直抓住"), ("Tha thứ cho mình", "他 次 召 明", "原谅自己"), ("Nhẹ lòng hơn", "涅 隆 韩", "心里更轻松"))),
    ("紧急应急", 14, "被困电梯怎么说", "在越南被困电梯，这8句能救急", "#B84444", "#F0C76A", items(("Tôi bị kẹt trong thang máy", "多伊 比 给 仲 汤 麦", "我被困在电梯里"), ("Cửa không mở", "古呀 空 摸", "门打不开"), ("Mất điện", "马 甸", "停电了"), ("Tôi đang ở tầng...", "多伊 当 额 汤", "我在……楼"), ("Có ai không", "果 艾 空", "有人吗"), ("Gọi cứu hộ", "戈伊 救 护", "叫救援"), ("Tôi khó thở", "多伊 扣 特", "我呼吸困难"), ("Xin nhanh lên", "辛 宁 连", "请快一点"))),
    ("经典口头禅", 12, "约人常用口头禅", "越南人约朋友，天天挂嘴边的8句", "#9A5A8B", "#F1C66A", items(("Đi không", "低 空", "去不去"), ("Rảnh không", "软 空", "有空吗"), ("Đi cùng nhé", "低 工 涅", "一起去吧"), ("Tùy bạn", "随 半", "随你"), ("Sao cũng được", "sao 共 得", "都可以"), ("Nhắn tôi nhé", "念 多伊 涅", "给我发消息"), ("Gặp sau nhé", "嘎 扫 涅", "回头见"), ("Chốt nhé", "竹 涅", "就这么定"))),
    ("经典口头禅", 13, "委婉拒绝口头禅", "越南人委婉拒绝，常说这8句", "#9A5A8B", "#F1C66A", items(("Chắc là không được", "甲 拉 空 得", "可能不行"), ("Để tôi xem đã", "得 多伊 森 打", "我先看看"), ("Hơi khó đấy", "黑 扣 得", "有点难"), ("Lần sau nhé", "兰 扫 涅", "下次吧"), ("Tôi bận rồi", "多伊 本 若伊", "我有事了"), ("Không tiện lắm", "空 便 兰", "不太方便"), ("Xin lỗi nhé", "辛 罗伊 涅", "不好意思"), ("Cảm ơn đã rủ", "感 恩 打 如", "谢谢邀请"))),
    ("越南名字", 8, "名字Anh怎么理解", "越南名字Anh，不只是一种意思", "#A46838", "#F1C66A", items(("Anh", "安", "Anh（名字，也能表示哥哥）"), ("Hùng", "红", "Hùng（雄）"), ("Dũng", "勇", "Dũng（勇）"), ("Minh", "明", "Minh（明）"), ("Phúc", "福", "Phúc（福）"))),
    ("越南称呼", 7, "餐厅里怎么叫人", "在越南餐厅，叫服务员这样说", "#5072A6", "#F2C65E", items(("Bạn ơi", "半 额", "朋友、请问"), ("Anh ơi", "安 额", "哥、先生"), ("Chị ơi", "姐 额", "姐、女士"), ("Em ơi", "em 额", "妹、年轻店员"), ("Cô ơi", "哥 额", "阿姨、女士"))),
    ("越南美食", 10, "越南甜汤怎么点", "去越南吃甜品，这8个词先收藏", "#C95F2E", "#F4C95D", items(("chè", "遮", "越南甜汤"), ("chè ba màu", "遮 巴 猫", "三色甜汤"), ("chè đậu xanh", "遮 道 生", "绿豆甜汤"), ("bánh flan", "班 flan", "焦糖布丁"), ("sữa chua", "丝呀 朱呀", "酸奶"), ("sữa chua nếp cẩm", "丝呀 朱呀 内 根", "紫米酸奶"), ("nước cốt dừa", "诺克 郭 椰", "椰浆"), ("đá bào", "打 包", "刨冰"))),
]


def seed(project_id: str, lang: str, rows: list[tuple]) -> None:
    project = REPO / "projects" / project_id
    episode_dir = project / "artifacts" / "episodes"
    episode_dir.mkdir(parents=True, exist_ok=True)
    for folder in ("assets/audio", "assets/music", "composition", "renders"):
        (project / folder).mkdir(parents=True, exist_ok=True)
    project_meta = {"version": "1.0", "created_at": datetime.now(timezone.utc).isoformat(), "project_id": project_id,
                    "title": ("泰语" if lang == "th" else "越南语") + "待发布库存补齐 · 2026-09", "pipeline_type": "animated-explainer"}
    (project / "project.json").write_text(json.dumps(project_meta, ensure_ascii=False, indent=2) + "\n")
    publish = []
    prefix = "thai" if lang == "th" else "viet"
    brand = "泰语千词" if lang == "th" else "越南语千词"
    for ix, (sub, no, title, hook, accent, accent2, card_items) in enumerate(rows, 1):
        eid = f"ep{ix:02d}"
        safe = {"听力测验":"quiz", "场景短句":"scene", "怎么称呼":"address", "情景对话":"dialogue", "招牌识字":"signboard", "泰国人的英文名":"engname", "数数":"numbers", "禅意一句":"zen", "紧急应急":"emergency", "经典口头禅":"catchphrase", "越南名字":"name", "越南称呼":"address", "越南美食":"food"}[sub]
        slug = f"{prefix}_{safe}_ep{no:02d}"
        episode = {
            "id": eid, "target_lang": lang, "series_title": f"{brand} · 待发布库存补齐", "title": title,
            "voice_energy": "medium-high", "items": card_items,
            "render_config": {"series_name": f"{brand} · {sub}", "episode": f"NO.{no:02d}", "topic": title,
                              "hook": hook, "cover_title": COVER_TITLES[(lang, sub, no)], "accent": accent, "accent2": accent2, "mode": "cards", "cover_end": 2.4,
                              "language_gap": 0.16, "minimum_card_seconds": 3.5, "tail_gap": 0.32,
                              "outro_seconds": 3.5, "music_source": MUSIC}}
        if lang == "th" and sub == "情景对话" and no == 5:
            episode["render_config"]["spoken_hook"] = "在泰国咖啡店，少甜，冰少一点，这样说"
            episode["analysis_items"] = COFFEE_ANALYSIS
        if lang == "th" and sub == "泰国人的英文名" and no == 6:
            episode["analysis_items"] = ENGLISH_NAME_ANALYSIS
        (episode_dir / f"{eid}.json").write_text(json.dumps(episode, ensure_ascii=False, indent=2) + "\n")
        caption = f"{hook}。先听{('泰语' if lang == 'th' else '越南语')}，再看中文和谐音，收藏起来慢慢练。"
        publish.append({"episode_id": eid, "series_id": 1 if lang == "th" else 2, "sub_series": sub, "slug": slug,
                        "title": f"{title}｜{brand}", "publish_copy": caption + f" #{brand} #{sub} #语言学习",
                        "wechat_copy": caption, "video_path": f"renders/{eid}.mp4",
                        "cover_path": f"renders/{eid}_cover.jpg", "cover_landscape_path": f"renders/{eid}_cover_landscape.jpg"})
    (project / "artifacts" / "publish_batch.json").write_text(json.dumps({"version":"1.0", "episodes":publish}, ensure_ascii=False, indent=2) + "\n")
    print(project_id, len(rows))


def main() -> None:
    seed("thai-inventory-topup-202609", "th", TH)
    seed("viet-inventory-topup-202609", "vi", VI)


if __name__ == "__main__":
    main()
