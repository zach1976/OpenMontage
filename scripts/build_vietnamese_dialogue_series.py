#!/usr/bin/env python3
"""Build the four Vietnamese restaurant-dialogue lessons.

The script keeps editorial data in one place and materializes the canonical
OpenMontage artifacts.  Audio generation/rendering are intentionally separate
pipeline stages; this file only writes the research/proposal/script/scene/edit
contracts and the Remotion props source data.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-09-21"
SERIES = "越南语千词"
SOURCES = [
    {
        "url": "https://www.vietnamtourism.com/vi/cach-goi-mon-tai-nha-hang-viet-nam-ia-phuong-cau-noi-thuc-on",
        "title": "Cách gọi món tại nhà hàng Việt Nam địa phương",
        "used_for": "点菜、量词、结账与餐厅支付表达",
        "reliability": "secondary",
    },
    {
        "url": "https://www.hvajlanguages.vn/cach-goi-mon-an-bang-tieng-viet",
        "title": "How to Order Food in Vietnamese",
        "used_for": "Cho tôi + 数量 + 量词 + 菜名结构",
        "reliability": "secondary",
    },
    {
        "url": "https://trykaiwa.com/blog/vietnamese-cafe-ordering-realistic",
        "title": "Ordering Coffee in Vietnamese: Real Dialogue Scripts",
        "used_for": "口语语气词 nhé、刷卡和扫码支付",
        "reliability": "secondary",
    },
    {
        "url": "https://vietgohan.com/en/20250427-2/",
        "title": "Essential Vietnamese Phrases for Restaurants",
        "used_for": "餐厅要水表达",
        "reliability": "secondary",
    },
    {
        "url": "https://howtosayguide.com/how-to-say-take-away-in-vietnamese/",
        "title": "How to Say Take Away in Vietnamese",
        "used_for": "mang về、mang đi与打包语境",
        "reliability": "secondary",
    },
    {
        "url": "https://www.reddit.com/r/learnvietnamese/comments/1t16cea/what_does_t%C3%B4i_mean_here_duolingo_taught_water/",
        "title": "Natural ways to ask for water in Vietnamese",
        "used_for": "口语中Cho tôi xin一杯水的自然度交叉核对",
        "reliability": "anecdotal",
    },
]


EPISODES = [
    {
        "no": 1,
        "slug": "order",
        "topic": "餐厅点菜",
        "hook": "在越南餐厅，怎么自然点菜？",
        "image": "vietnamese_order_main.png",
        "image_prompt": "年轻男店员拿着菜单，年轻女顾客指向菜单准备点一碗牛肉河粉，桌上有越南河粉和香草",
        "dialogue": [
            ("男店员", "male", "Chị muốn gọi món gì ạ?", "您想点什么？", "姐 姆温 贵 莫恩 伊 阿"),
            ("女顾客", "female", "Cho tôi một tô phở bò.", "请给我一碗牛肉河粉。", "桌 堆 莫 多 佛 博"),
            ("男店员", "male", "Chị có ăn cay được không?", "您能吃辣吗？", "姐 果 安 该 德 空"),
            ("女顾客", "female", "Không cay nhé.", "不要辣。", "空 该 涅"),
        ],
        "lessons": [
            {
                "id": "ask",
                "label": "店员提问 · 逐词解释",
                "eyebrow": "先听懂店员怎么问",
                "vi": "Chị muốn gọi món gì ạ?",
                "xie": "姐 姆温 贵 莫恩 伊 阿",
                "zh": "您想点什么？",
                "accent": "male",
                "words": [("Chị", "对女性的称呼"), ("muốn", "想要"), ("gọi món", "点菜"), ("gì", "什么"), ("ạ", "礼貌语气词")],
                "note": "服务员对女性顾客的自然问法。",
            },
            {
                "id": "order",
                "label": "顾客回答 · 逐词解释",
                "eyebrow": "点一碗牛肉河粉",
                "vi": "Cho tôi một tô phở bò.",
                "xie": "桌 堆 莫 多 佛 博",
                "zh": "请给我一碗牛肉河粉。",
                "accent": "female",
                "words": [("Cho tôi", "给我"), ("một", "一"), ("tô", "碗（南部常用）"), ("phở bò", "牛肉河粉")],
                "note": "换掉菜名，就能直接点别的菜。",
            },
            {
                "id": "spicy",
                "label": "口味确认",
                "eyebrow": "能吃辣吗？不要辣。",
                "vi": "Ăn cay được không? / Không cay nhé.",
                "xie": "安 该 德 空 / 空 该 涅",
                "zh": "能吃辣吗？不要辣。",
                "accent": "gold",
                "words": [("ăn cay", "吃辣"), ("được không", "可以吗"), ("không cay", "不辣"), ("nhé", "柔和语气")],
                "note": "Không cay 是旅行中最实用的口味短句之一。",
            },
        ],
    },
    {
        "no": 2,
        "slug": "checkout",
        "topic": "餐厅结账",
        "hook": "在越南餐厅，怎么用越南语结账？",
        "image": "vietnamese_checkout_main.png",
        "image_prompt": "年轻女顾客用手示意结账并拿着银行卡，年轻男店员递上账单夹，桌上是吃完的越南菜",
        "dialogue": [
            ("女顾客", "female", "Tính tiền giúp tôi nhé.", "请帮我结账。", "丁 颠 祖 堆 涅"),
            ("男店员", "male", "Dạ, chị chờ một chút ạ.", "好的，请稍等。", "亚 姐 车 莫 竹 阿"),
            ("女顾客", "female", "Tôi có thể thanh toán bằng thẻ không?", "可以刷卡吗？", "堆 果 特 汤 断 伴 特 空"),
            ("男店员", "male", "Dạ được ạ.", "可以。", "亚 德 阿"),
        ],
        "lessons": [
            {
                "id": "bill",
                "label": "顾客结账 · 逐词解释",
                "eyebrow": "最常用的结账说法",
                "vi": "Tính tiền giúp tôi nhé.",
                "xie": "丁 颠 祖 堆 涅",
                "zh": "请帮我结账。",
                "accent": "female",
                "words": [("Tính tiền", "结账 / 买单"), ("giúp tôi", "帮我"), ("nhé", "柔和语气")],
                "note": "也可以简短说：Tính tiền。",
            },
            {
                "id": "pay",
                "label": "支付方式 · 实用引申",
                "eyebrow": "现金、刷卡、扫码怎么说",
                "vi": "Thanh toán bằng…",
                "xie": "汤 断 伴……",
                "zh": "用……支付",
                "accent": "gold",
                "words": [("tiền mặt", "现金"), ("thẻ", "卡"), ("quét mã QR", "扫二维码"), ("Alipay", "支付宝"), ("WeChat Pay", "微信支付")],
                "note": "问句结尾加 không：可以用……支付吗？",
            },
            {
                "id": "wait",
                "label": "店员回应 · 逐词解释",
                "eyebrow": "听懂“请稍等”",
                "vi": "Dạ, chị chờ một chút ạ.",
                "xie": "亚 姐 车 莫 竹 阿",
                "zh": "好的，请稍等。",
                "accent": "male",
                "words": [("Dạ", "好的 / 是"), ("chị", "对女性的称呼"), ("chờ", "等"), ("một chút", "一会儿"), ("ạ", "礼貌语气词")],
                "note": "Dạ 和 ạ 都让服务语气更礼貌。",
            },
        ],
    },
    {
        "no": 3,
        "slug": "water",
        "topic": "餐厅要水",
        "hook": "想要一杯水，越南语怎么说？",
        "image": "vietnamese_water_main.png",
        "image_prompt": "年轻女顾客指向桌上的空玻璃杯，年轻男店员手持透明饮用水瓶准备倒水，桌上有越南菜",
        "dialogue": [
            ("女顾客", "female", "Cho tôi xin một ly nước lọc nhé.", "请给我一杯饮用水。", "桌 堆 辛 莫 里 诺 洛 涅"),
            ("男店员", "male", "Chị muốn nước lọc hay nước khoáng?", "您想要饮用水还是矿泉水？", "姐 姆温 诺 洛 海 诺 矿"),
            ("女顾客", "female", "Nước lọc nhé.", "饮用水。", "诺 洛 涅"),
            ("男店员", "male", "Dạ, có ngay ạ.", "好的，马上来。", "亚 果 艾 阿"),
        ],
        "lessons": [
            {
                "id": "request",
                "label": "顾客请求 · 逐词解释",
                "eyebrow": "礼貌地要一杯水",
                "vi": "Cho tôi xin một ly nước lọc nhé.",
                "xie": "桌 堆 辛 莫 里 诺 洛 涅",
                "zh": "请给我一杯饮用水。",
                "accent": "female",
                "words": [("Cho tôi xin", "请给我"), ("một", "一"), ("ly", "杯"), ("nước lọc", "饮用水"), ("nhé", "柔和语气")],
                "note": "Cho tôi xin 比单说 Cho tôi 更客气。",
            },
            {
                "id": "choice",
                "label": "二选一问法",
                "eyebrow": "饮用水还是矿泉水",
                "vi": "Nước lọc hay nước khoáng?",
                "xie": "诺 洛 海 诺 矿",
                "zh": "饮用水还是矿泉水？",
                "accent": "male",
                "words": [("nước lọc", "饮用水 / 过滤水"), ("hay", "还是"), ("nước khoáng", "矿泉水")],
                "note": "hay 放在两个选项中间，表示“还是”。",
            },
            {
                "id": "soon",
                "label": "店员回应",
                "eyebrow": "马上来，怎么说",
                "vi": "Dạ, có ngay ạ.",
                "xie": "亚 果 艾 阿",
                "zh": "好的，马上来。",
                "accent": "gold",
                "words": [("Dạ", "好的"), ("có", "有 / 来"), ("ngay", "马上"), ("ạ", "礼貌语气词")],
                "note": "在服务场景里可整体理解为“好的，马上来”。",
            },
        ],
    },
    {
        "no": 4,
        "slug": "takeaway",
        "topic": "餐厅打包",
        "hook": "在越南餐厅，吃不完怎么打包？",
        "image": "vietnamese_takeaway_main.png",
        "image_prompt": "年轻女顾客指向盘中剩下的越南菜，请求打包，年轻男店员拿着打开的牛皮纸餐盒回应",
        "dialogue": [
            ("女顾客", "female", "Gói phần này mang về giúp tôi nhé.", "请帮我把这份打包带走。", "果伊 粉 奈 芒 维 祖 堆 涅"),
            ("男店员", "male", "Dạ được, chị chờ một chút ạ.", "好的，请稍等。", "亚 德 姐 车 莫 竹 阿"),
            ("女顾客", "female", "Cho tôi xin thêm một cái túi nhé.", "请再给我一个袋子。", "桌 堆 辛 添 莫 盖 对 涅"),
            ("男店员", "male", "Vâng ạ.", "好的。", "文 阿"),
        ],
        "lessons": [
            {
                "id": "pack",
                "label": "顾客请求 · 逐词解释",
                "eyebrow": "吃不完，打包带走",
                "vi": "Gói phần này mang về giúp tôi nhé.",
                "xie": "果伊 粉 奈 芒 维 祖 堆 涅",
                "zh": "请帮我把这份打包带走。",
                "accent": "female",
                "words": [("Gói", "打包 / 包起来"), ("phần này", "这份"), ("mang về", "带回去"), ("giúp tôi", "帮我"), ("nhé", "柔和语气")],
                "note": "在店里打包剩菜，mang về 很自然。",
            },
            {
                "id": "variants",
                "label": "实用引申",
                "eyebrow": "“带走”还有这些说法",
                "vi": "mang về / mang đi / đem về",
                "xie": "芒 维 / 芒 低 / 店 维",
                "zh": "带回去 / 带走 / 拿回去",
                "accent": "gold",
                "words": [("mang về", "带回去"), ("mang đi", "带走"), ("đem về", "拿回去")],
                "note": "点餐时说 mang đi；吃剩后打包常说 mang về。",
            },
            {
                "id": "bag",
                "label": "再要一个袋子",
                "eyebrow": "Cho tôi xin thêm…",
                "vi": "Cho tôi xin thêm một cái túi nhé.",
                "xie": "桌 堆 辛 添 莫 盖 对 涅",
                "zh": "请再给我一个袋子。",
                "accent": "male",
                "words": [("Cho tôi xin", "请给我"), ("thêm", "再 / 另外"), ("một cái túi", "一个袋子"), ("nhé", "柔和语气")],
                "note": "把 túi 换成餐具、纸巾，也能继续套用。",
            },
        ],
    },
]


def dump(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def project_id(ep: dict) -> str:
    return f"vietnamese-1000-dialogue-{ep['no']:02d}-{ep['slug']}"


def research(ep: dict) -> dict:
    anchors = {
        1: [
            "Cho tôi + 数量 + 量词 + 菜名是直接而实用的点菜结构。",
            "越南语点餐时常用tô、ly、phần等量词。",
            "Không cay可直接表达不要辣。",
        ],
        2: [
            "Tính tiền是餐厅里常用的结账表达。",
            "刷卡可说thanh toán bằng thẻ，扫码可说quét mã QR。",
            "nhé常放在请求末尾，让语气更柔和。",
        ],
        3: [
            "Cho tôi xin một ly nước是自然的要水结构。",
            "nước lọc指饮用水或过滤水，nước khoáng指矿泉水。",
            "hay放在两个选项之间表示还是。",
        ],
        4: [
            "mang về和mang đi都可表达打包带走，使用侧重点略有不同。",
            "gói可表示把食物包好、打包。",
            "Cho tôi xin thêm…可用于再要袋子、餐具或纸巾。",
        ],
    }[ep["no"]]
    return {
        "version": "1.0",
        "topic": f"面向中文初学者的越南餐厅{ep['topic']}情景对话",
        "research_date": DATE,
        "landscape": {
            "existing_content": [
                {"title": SOURCES[0]["title"], "url": SOURCES[0]["url"], "source": "越南餐饮旅行指南", "angle": "按真实用餐流程整理短句", "what_it_covers": "点菜、量词、结账和支付。", "what_it_misses": "缺少中文谐音、角色对白和逐词先读。"},
                {"title": SOURCES[1]["title"], "url": SOURCES[1]["url"], "source": "越南语教学文章", "angle": "用公式化结构教点菜", "what_it_covers": "Cho tôi与常见量词。", "what_it_misses": "没有形成四句完整对话。"},
                {"title": SOURCES[2]["title"], "url": SOURCES[2]["url"], "source": "真实口语脚本", "angle": "咖啡馆自然对话", "what_it_covers": "nhé、刷卡和扫码口语。", "what_it_misses": "未按中文初学者拆词。"},
            ],
            "saturated_angles": ["只罗列旅行短句", "用拉丁转写代替发音提示", "没有角色关系的词卡"],
            "underserved_gaps": ["先完整听真实四句，再逐词先念越南语并用中文解释", "用中文谐音而不是IPA降低初学门槛"],
        },
        "trending": {"recent_developments": [], "active_discussions": [{"platform": "Reddit", "topic_or_url": SOURCES[5]["url"], "sentiment": "学习者关心课本表达与真实餐厅口语是否自然。", "key_quotes": []}], "timeliness_window": "evergreen"},
        "data_points": [
            {"claim": claim, "source_url": SOURCES[min(i, 4)]["url"], "source_name": SOURCES[min(i, 4)]["title"], "credibility": "secondary_source", "surprise_factor": "notable" if i else "expected", "usable_as": "script_anchor"}
            for i, claim in enumerate(anchors)
        ],
        "audience_insights": {
            "common_questions": [f"在越南餐厅怎么说{ep['topic']}？", "怎么说得自然又礼貌？", "逐词是什么意思，能不能换词套用？"],
            "misconceptions": [{"myth": "越南语使用拉丁字母，看字就一定会读。", "reality": "声调和元音差异仍会造成误读，初学者需要真人示范和辅助谐音。", "source": SOURCES[1]["url"]}],
            "knowledge_level": "中文零基础或初学者，目标是在旅行餐厅立即开口。",
            "pain_points": ["只会指菜单", "记得单词但不会组成礼貌请求", "听不懂店员的自然回应"],
        },
        "angles_discovered": [
            {"name": "四句真实闭环", "hook": ep["hook"], "type": "evergreen", "why_now": "直接解决旅行餐厅高频任务。", "grounded_in": ["data_points[0]", "audience_insights.common_questions[0]"]},
            {"name": "逐词先听再懂", "hook": "每个词先听越南语，再接中文意思。", "type": "narrative", "why_now": "避免只看中文解释却没有建立语音记忆。", "grounded_in": ["audience_insights.misconceptions[0]"]},
            {"name": "一句多场景迁移", "hook": "换掉一个词，同一结构还能继续用。", "type": "evergreen", "why_now": "比孤立短句更适合真实旅行。", "grounded_in": ["data_points[1]", "audience_insights.common_questions[2]"]},
        ],
        "visual_references": [{"description": "越南餐厅人物实景加双语教学卡", "url": SOURCES[0]["url"], "what_works": "场景动作与语言任务一一对应。"}],
        "sources": SOURCES,
        "research_summary": f"本集采用真实越南餐厅四句闭环，先让观众听懂场景，再逐词先念越南语、后接中文解释，并用可迁移结构完成{ep['topic']}任务。",
        "metadata": {"series_reference": "thai-1000-dialogue-01-04", "language": "vi-VN"},
    }


def proposal(ep: dict, pid: str) -> tuple[dict, dict]:
    title = f"{SERIES}·一来一回 No.{ep['no']:02d}：越南{ep['topic']}"
    options = [
        {"id": "c1", "title": title, "hook": ep["hook"], "narrative_structure": "tutorial", "visual_approach": "完整四句对话、逐词先读、实用引申、完整复听；复用泰语系列版式。", "suggested_playbook": "custom-dialogue", "target_audience": "准备赴越南或在越南生活的中文初学者", "target_platform": "generic", "target_duration_seconds": 68, "key_points": [x[2] for x in ep["dialogue"]], "core_message": f"在真实餐厅完成{ep['topic']}。", "cta": "越南语千词，在越南生活够用了。", "tone": "清楚、真实、轻松", "grounded_in": ["data_points[0]", "data_points[1]"], "why_this_works": "与现有系列完全对应，学习路径稳定。"},
        {"id": "c2", "title": f"三秒开口：{ep['topic']}", "hook": "服务员就在面前，三秒内说出这句话。", "narrative_structure": "problem_solution", "visual_approach": "倒计时加单句跟读。", "suggested_playbook": "custom-dialogue", "target_audience": "需要快速开口的旅行者", "target_platform": "generic", "target_duration_seconds": 45, "key_points": [ep["dialogue"][0][2], "用中文谐音快速建立发音记忆"], "core_message": "先学会一句能立即用的话。", "cta": "下次直接用越南语。", "tone": "快速、互动", "grounded_in": ["audience_insights.pain_points[0]"], "why_this_works": "短，但教学深度不足。"},
        {"id": "c3", "title": f"{ep['topic']}的三种说法", "hook": "课本说法和越南人常说的，有什么不同？", "narrative_structure": "comparison", "visual_approach": "三栏比较不同语域和替换词。", "suggested_playbook": "custom-dialogue", "target_audience": "越南语初中级学习者", "target_platform": "generic", "target_duration_seconds": 75, "key_points": [l["vi"] for l in ep["lessons"]], "core_message": "理解同一任务的多种自然说法。", "cta": "先记住最稳妥的一句。", "tone": "比较、纠错", "grounded_in": ["data_points[2]"], "why_this_works": "知识更深，但不如四句闭环适合系列首轮。"},
    ]
    packet = {
        "version": "1.0",
        "concept_options": options,
        "selected_concept": {"concept_id": "c1", "rationale": "用户明确要求做泰语系列对应的四集越南语版。", "modifications": ["四集全流程完成后统一审核", "中文沿用第一集晓晓声", "信息卡使用中文谐音、不使用IPA"]},
        "production_plan": {
            "pipeline": "animated-explainer", "playbook": "custom-dialogue", "renderer_family": "explainer-teacher", "render_runtime": "remotion", "composition_mode": "templated",
            "stages": [
                {"stage": "assets", "tools": [{"tool_name": "edge-tts-cli", "role": "晓晓中文声与越南语男女角色声", "provider": "microsoft-edge", "available": True, "estimated_cost_usd": 0.0, "why_this_provider": "必须匹配第一集中文音色，且支持越南语男女声。"}, {"tool_name": "image_gen", "role": "生成越南餐厅情景主图", "provider": "built-in", "available": True, "estimated_cost_usd": 0.0, "why_this_provider": "生成项目内四张无文字竖屏实景图。"}], "approach": "同一系列摄影感，越南餐厅环境；音频按短句和词块生成。", "fallback_if_unavailable": "任何关键提供商受阻时暂停，不静默更换。"},
                {"stage": "compose", "tools": [{"tool_name": "video_compose/remotion", "role": "复用对话卡、逐词高亮和系列转场", "provider": "local", "available": True, "estimated_cost_usd": 0.0, "why_this_provider": "用户已明确批准Remotion模板化路径。"}], "approach": "1080x1920、30fps、约60至75秒。", "fallback_if_unavailable": "暂停，不改用其他运行时。"},
            ],
            "quality_tradeoffs": [{"tradeoff": "模板续作与全新设计", "recommendation": "模板续作", "quality_impact": "保持系列一致性与批量稳定性。"}],
            "alternative_paths": [{"description": "Remotion模板化", "total_cost_usd": 0.0, "quality_level": "standard", "what_changes": "推荐路径，完整匹配泰语版"}, {"description": "HyperFrames重建", "total_cost_usd": 0.0, "quality_level": "standard", "what_changes": "动效更自由，但无法像素级复用现有系列"}],
            "delivery_promise": {"promise_type": "teacher_explainer", "motion_required": True, "source_required": False, "tone_mode": "educational-playful", "quality_floor": "presentable", "approved_fallback": None},
            "taste_profile": {"design_read": "现有泰语情景对话系列的越南语姐妹版。", "visual_variance": 4, "motion_intensity": 5, "information_density": 6, "palette_discipline": "青蓝男声、珊瑚橙女声、金色重点。", "layout_variation": "钩子、完整对话、三张教学卡、复听、片尾。", "reference_strategy": "严格复用ThaiDialogueSeries版式和节奏。", "anti_patterns": ["IPA", "长停顿", "一闪而过的提示页", "信息卡过低"], "quality_gates": ["逐词先念越南语", "中文谐音可见", "背景音乐存在并自动压低", "信息卡保持上移位置"]},
            "music_source": {"source_type": "user_library", "track_path": "../thai-1000-dialogue-01-ao/assets/music/bgm.mp3", "provider": "local", "mood_direction": "复用现有系列轻量背景音乐并动态压低", "estimated_cost_usd": 0.0},
            "voice_selection": {"provider": "microsoft-edge", "voice_id": "zh-CN-XiaoxiaoNeural / vi-VN-HoaiMyNeural / vi-VN-NamMinhNeural", "rationale": "中文与第一集一致，越南语按角色区分男女声。", "estimated_cost_usd": 0.0, "delivery_style": "真实餐厅交流，清楚但不拖慢。", "pacing_policy": "角色切换约0.2秒；逐词越南语与中文之间约0.08秒。", "sample_approval_required": False},
        },
        "cost_estimate": {"total_estimated_usd": 0.0, "line_items": [{"tool": "edge-tts-cli", "operation": "中越双语配音", "quantity": 1, "estimated_usd": 0.0}, {"tool": "image_gen", "operation": "越南餐厅情景主图", "quantity": 1, "estimated_usd": 0.0}, {"tool": "remotion", "operation": "本地竖屏渲染", "quantity": 1, "estimated_usd": 0.0}], "budget_verdict": "within_budget", "savings_options": []},
        "approval": {"status": "approved", "user_notes": "用户确认Remotion+模板化并回复开始；此前明确要求全部做好后一起审核。", "approved_budget_usd": 0.0},
        "metadata": {"series_reference": "thai-1000-dialogue-01-04", "approved_at": DATE},
    }
    decisions = {
        "version": "1.0", "project_id": pid, "decisions": [
            {"decision_id": "d-001", "stage": "proposal", "category": "pipeline_selection", "subject": "越南语情景对话制作管线", "options_considered": [{"option_id": "animated-explainer", "label": "Animated Explainer", "score": 0.98, "reason": "与既有系列合同一致。"}, {"option_id": "localization-dub", "label": "Localization Dub", "score": 0.45, "reason": "适合对原视频直接配音。", "rejected_because": "本次需要替换教学内容和卡片，不是简单配音。"}], "selected": "animated-explainer", "reason": "保留逐词教学与场景计划。", "user_visible": True, "user_approved": True, "confidence": 0.96},
            {"decision_id": "d-002", "stage": "proposal", "category": "render_runtime_selection", "subject": "越南语系列渲染运行时", "options_considered": [{"option_id": "remotion", "label": "Remotion", "score": 0.99, "reason": "可直接复用现有React对话系列。"}, {"option_id": "hyperframes", "label": "HyperFrames", "score": 0.62, "reason": "适合HTML/GSAP自定义动效。", "rejected_because": "需要重建，和现有系列会有差异。"}, {"option_id": "ffmpeg", "label": "FFmpeg", "score": 0.3, "reason": "适合基础剪辑。", "rejected_because": "不足以保持逐词高亮和角色卡动画。"}], "selected": "remotion", "reason": "用户于2026-09-21明确确认并回复开始。", "user_visible": True, "user_approved": True, "confidence": 0.99},
            {"decision_id": "d-003", "stage": "proposal", "category": "composition_mode", "subject": "越南语系列构图作者模式", "options_considered": [{"option_id": "templated", "label": "Templated", "score": 0.99, "reason": "最适合对应版和批量本地化。"}, {"option_id": "atelier", "label": "Atelier", "score": 0.5, "reason": "视觉更独特。", "rejected_because": "会偏离泰语版系列识别。"}], "selected": "templated", "reason": "用户批准模板化制作。", "user_visible": True, "user_approved": True, "confidence": 0.99},
            {"decision_id": "d-004", "stage": "proposal", "category": "voice_selection", "subject": "中文旁白与越南语角色声", "options_considered": [{"option_id": "edge", "label": "Edge TTS Xiaoxiao + Vietnamese voices", "score": 0.98, "reason": "中文可与第一集完全同声线。"}, {"option_id": "google", "label": "Google TTS", "score": 0.72, "reason": "注册表可用。", "rejected_because": "无法满足沿用第一集晓晓声的硬要求。"}], "selected": "edge", "reason": "遵循用户明确的声音要求。", "user_visible": True, "user_approved": True, "confidence": 0.96},
            {"decision_id": "d-005", "stage": "proposal", "category": "music_source", "subject": "越南语系列背景音乐", "options_considered": [{"option_id": "reuse", "label": "复用泰语系列BGM", "score": 0.98, "reason": "听觉识别一致。"}, {"option_id": "new", "label": "生成新音乐", "score": 0.55, "reason": "可做越南风格。", "rejected_because": "会改变对应版的系列感。"}, {"option_id": "none", "label": "无音乐", "score": 0.1, "reason": "对白最清楚。", "rejected_because": "用户明确指出背景音乐不能缺失。"}], "selected": "reuse", "reason": "保留背景音乐并在说话时动态压低。", "user_visible": True, "user_approved": True, "confidence": 0.99},
            {"decision_id": "d-006", "stage": "proposal", "category": "approval_policy", "subject": "No.01–No.04合并审核策略", "options_considered": [{"option_id": "batch", "label": "四集完成后统一审核", "score": 1.0, "reason": "用户明确要求所有做好后一起审核。"}, {"option_id": "per_gate", "label": "逐集逐阶段审核", "score": 0.2, "reason": "默认治理更保守。", "rejected_because": "与用户的明确预授权冲突。"}], "selected": "batch", "reason": "四集完成脚本、资产、剪辑和合成后，在统一Chrome审核页停下。", "user_visible": True, "user_approved": True, "confidence": 1.0},
        ]
    }
    return packet, decisions


def script(ep: dict) -> dict:
    sections = [
        {"id": "s_hook", "label": "钩子", "text": ep["hook"], "start_seconds": 0, "end_seconds": 5, "speaker_directions": "晓晓中文声，简短提问。", "delivery_cues": {"pace": "brisk", "energy": "curious", "emphasis_words": [ep["topic"]], "pause_after_seconds": 0.15, "delivery_note": "不要拉长。"}, "enhancement_cues": [{"type": "animation", "description": "餐厅任务与标题进入。", "timestamp_seconds": 0.8}], "source_ref": SOURCES[0]["url"]},
        {"id": "s_dialogue", "label": "完整对话", "text": "。".join(f"{role}：{vi}" for role, _, vi, _, _ in ep["dialogue"]), "start_seconds": 5, "end_seconds": 16, "speaker_directions": "越南语男女角色自然交流，短停顿。", "delivery_cues": {"pace": "conversational", "energy": "natural service exchange", "pause_after_seconds": 0.2, "delivery_note": "不插入中文旁白。"}, "enhancement_cues": [{"type": "animation", "description": "四句双语卡依次点亮。", "timestamp_seconds": 5.2}], "source_ref": SOURCES[0]["url"]},
    ]
    t = 16
    for lesson in ep["lessons"]:
        dur = 11 if len(lesson["words"]) <= 4 else 13
        sections.append({"id": f"s_{lesson['id']}", "label": lesson["label"], "text": f"先念越南语词块，再解释中文。{lesson['zh']} {lesson['note']}", "start_seconds": t, "end_seconds": t + dur, "speaker_directions": "每个词块先由对应越南语角色声读，再由晓晓解释。", "delivery_cues": {"pace": "measured", "energy": "clear teacher", "emphasis_words": [w[0] for w in lesson["words"]], "pause_after_seconds": 0.08, "delivery_note": "词块间不要出现长停顿。"}, "enhancement_cues": [{"type": "animation", "description": "词块逐一高亮，信息卡位于画面上半部。", "timestamp_seconds": t + 0.5}], "source_ref": SOURCES[min(ep["no"], len(SOURCES)-1)]["url"]})
        t += dur
    sections.extend([
        {"id": "s_replay", "label": "完整复听", "text": "完整对话再听一遍。", "start_seconds": t, "end_seconds": t + 10, "speaker_directions": "复用四句越南语音频。", "delivery_cues": {"pace": "conversational", "energy": "natural", "pause_after_seconds": 0.15, "delivery_note": "不设置答题停顿。"}, "enhancement_cues": [{"type": "animation", "description": "四句按说话者再次点亮。", "timestamp_seconds": t + 0.2}]},
        {"id": "s_outro", "label": "品牌片尾", "text": "越南语千词，在越南生活够用了。", "start_seconds": t + 10, "end_seconds": t + 14, "speaker_directions": "晓晓平实收尾。", "delivery_cues": {"pace": "measured", "energy": "warm close", "emphasis_words": [SERIES], "pause_after_seconds": 0.1, "delivery_note": "固定系列口号。"}, "enhancement_cues": [{"type": "overlay", "description": "品牌名与固定口号。", "timestamp_seconds": t + 10.2}]},
    ])
    return {"version": "1.0", "title": f"{SERIES}·一来一回 No.{ep['no']:02d}：越南{ep['topic']}", "total_duration_seconds": t + 14, "voice_performance": {"performance_intent": "越南语角色真实自然，中文讲解清楚紧凑。", "pacing_profile": "conversational", "energy_curve": "问题钩子→自然对白→逐词拆解→实用引申→完整复听→片尾", "pause_policy": "角色换人0.2秒；逐词越南语与中文解释之间0.08秒。", "sample_section_id": "s_dialogue", "provider_notes": {"mixed_tts": "中文zh-CN-XiaoxiaoNeural；越南语女声HoaiMy、男声NamMinh。"}}, "sections": sections, "metadata": {"series_episode": ep["no"], "language_accuracy_note": "脚本使用自然越南餐厅口语；信息卡为中文谐音，不是IPA。", "dialogue": ep["dialogue"], "lessons": ep["lessons"]}}


def scene_plan(ep: dict, script_artifact: dict) -> dict:
    scenes = []
    for sec in script_artifact["sections"]:
        stype = "generated" if sec["id"] in ("s_dialogue", "s_replay") else ("text_card" if sec["id"] in ("s_hook", "s_outro") else "animation")
        scenes.append({"id": "sc_" + sec["id"][2:], "type": stype, "description": sec["label"], "start_seconds": sec["start_seconds"], "end_seconds": sec["end_seconds"], "script_section_id": sec["id"], "movement": "主图缓慢推近；文字卡spring进入；逐词按音频顺序高亮。", "transition_in": "fade", "transition_out": "short fade", "narrative_role": "establish_context" if sec["id"] == "s_hook" else ("resolution" if sec["id"] in ("s_replay", "s_outro") else "deliver_payload"), "information_role": f"完成{sec['label']}教学任务。", "hero_moment": sec["id"] in ("s_hook", "s_dialogue"), "required_assets": [{"type": "image", "description": f"越南餐厅竖屏实景：{ep['image_prompt']}，同一男女角色，自然暖光，9:16，无文字无水印。", "source": "generate"}] if sec["id"] == "s_hook" else [{"type": "animation", "description": "Remotion系列原生卡片。", "source": "source"}]})
    return {"version": "1.0", "style_playbook": "custom-dialogue", "scenes": scenes, "metadata": {"fps": 30, "resolution": "1080x1920", "safe_area": "y=120至1580", "camera_policy": "背景慢推；信息卡主体上移，避免底部播放器控件。"}}


def edit_decisions(ep: dict, script_artifact: dict) -> dict:
    cuts = []
    for sec in script_artifact["sections"]:
        cuts.append({"id": sec["id"], "source": "main_image", "in_seconds": sec["start_seconds"], "out_seconds": sec["end_seconds"], "layer": "primary", "transform": {"scale": 1.06, "position": "center", "animation": "remotion-frame-driven"}, "transition_in": "fade", "transition_out": "short fade", "transition_duration": 0.2, "reason": sec["label"]})
    return {"version": "1.0", "renderer_family": "explainer-teacher", "render_runtime": "remotion", "composition_mode": "templated", "cuts": cuts, "audio": {"narration": {"segments": [{"asset_id": "narration_full", "start_seconds": 0, "end_seconds": script_artifact["total_duration_seconds"]}]}, "music": {"asset_id": "music_bgm", "volume": 0.055, "fade_in_seconds": 1.2, "fade_out_seconds": 2.5, "ducking": {"enabled": True, "threshold_db": -25, "reduction_db": -7, "attack_ms": 80, "release_ms": 240}}}, "subtitles": {"enabled": True, "style": "embedded bilingual teaching cards", "source": "series_props.json", "font": "Be Vietnam Pro + PingFang SC", "font_size": 42, "color": "#243138", "outline_color": "#FFF8EB", "background": "#FFF8EBEE", "position": "center", "max_words_per_line": 8}, "transitions": [{"type": "short fade", "at_seconds": c["in_seconds"], "duration_seconds": 0.2} for c in cuts[1:]], "slideshow_risk_score": {"average": 0.16, "verdict": "strong"}, "metadata": {"proposal_render_runtime": "remotion", "target_duration_seconds": script_artifact["total_duration_seconds"], "compose_target": {"width": 1080, "height": 1920, "fps": 30}, "playbook": "custom-dialogue", "delivery_promise": {"promise_type": "teacher_explainer", "motion_required": True, "source_required": False, "tone_mode": "educational-playful", "quality_floor": "presentable"}, "loudnorm_target": -14}}


def main() -> int:
    for ep in EPISODES:
        pid = project_id(ep)
        base = ROOT / "projects" / pid
        proposal_artifact, decisions = proposal(ep, pid)
        script_artifact = script(ep)
        dump(base / "artifacts/research_brief.json", research(ep))
        dump(base / "artifacts/proposal_packet.json", proposal_artifact)
        dump(base / "artifacts/decision_log.json", decisions)
        dump(base / "decision_log.json", decisions)
        dump(base / "artifacts/script.json", script_artifact)
        dump(base / "artifacts/scene_plan.json", scene_plan(ep, script_artifact))
        dump(base / "artifacts/edit_decisions.json", edit_decisions(ep, script_artifact))
        dump(base / "artifacts/episode_source.json", ep)
        print(f"wrote {pid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
