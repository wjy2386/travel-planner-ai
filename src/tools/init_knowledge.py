"""
知识库初始化脚本 - 导入旅行相关的基础知识
"""

import os
from coze_coding_dev_sdk import KnowledgeClient, Config, ChunkConfig
from coze_coding_dev_sdk.knowledge.models import KnowledgeDocument, DataSourceType
from coze_coding_utils.runtime_ctx.context import Context

# 旅行目的地知识库
TRAVEL_KNOWLEDGE = {
    "东京": """
东京旅游攻略指南

【最佳游览时间】
春季（3-5月）：樱花季（3月底-4月初），气候宜人，是东京最美的季节
夏季（6-8月）：炎热潮湿，6月梅雨季，7-8月有花火大会
秋季（9-11月）：红叶季（11月），凉爽舒适，适合游览
冬季（12-2月）：干燥寒冷，12月有圣诞和新年庆典

【必游景点】
浅草寺：东京最古老的寺庙，建议上午9点前到达避开人流，从雷门拍照最佳
东京塔：地标建筑，日落时分登塔可看到绝美城市夜景
新宿御苑：四季都有美景，春季樱花、秋季红叶，需要买票进入
明治神宫：安静的神社，适合体验日本传统文化，免费参观
涩谷十字路口：世界最繁忙的十字路口，人流过街时拍照最佳
秋叶原：动漫和电子产品圣地，适合购物和体验二次元文化

【美食推荐】
筑地市场：新鲜寿司和海鲜，建议早上7-8点前往
一兰拉面：著名的豚骨拉面，单人隔间设计
银座：高端餐厅聚集地，适合尝试怀石料理
浅草周边：传统小吃如人形烧、雷门饼

【交通建议】
购买Suica或Pasmo卡：方便乘坐地铁和公交
购买Tokyo Subway Ticket：72小时无限次乘坐东京Metro地铁
机场交通：成田机场可乘坐NEX特急或京成Skyliner

【住宿区域】
新宿：交通枢纽，购物餐饮便利
浅草：传统氛围，价格相对便宜
银座：高端住宿，适合商务和高端旅行
秋叶原：动漫主题酒店，适合年轻游客

【实用贴士】
便利店：7-11、全家、罗森随处可见，可以取现和购买日常用品
垃圾处理：东京垃圾分类严格，公共场所垃圾箱少，建议随身携带垃圾袋
小费文化：日本没有小费文化，无需给小费
礼仪文化：进入室内要脱鞋，电车手机静音，不要边走边吃
""",

    "京都": """
京都旅游攻略指南

【最佳游览时间】
春季（3-5月）：樱花季（3月底-4月初），哲学之道、圆山公园赏樱圣地
秋季（9-11月）：红叶季（11月中下旬），东福寺、清水寺、岚山最佳
夏季（6-8月）：祗园祭（7月）、大文字五山送火（8月16日）
冬季（12-2月）：游客较少，部分庭园雪景优美

【必游寺庙神社】
清水寺：世界遗产，春季樱花、秋季红叶绝美，清水舞台视野开阔
金阁寺：金箔覆盖的寺庙，倒映在镜湖池中是经典拍照点
银阁寺：枯山水庭园代表，体现了禅意美学
伏见稻荷大社：千本鸟居，建议清晨或傍晚前往避开人流
八坂神社：祗园地区中心，夜晚灯光下很美

【岚山区域】
竹林小径：两旁竹林，清晨光线最美
天龙寺：世界遗产，曹源池庭园四季景色不同
渡月桥：保津川上的桥梁，春季樱花、秋季红叶是最佳时节
小火车：嵯峨野观光小火车，欣赏保津川峡谷风光

【美食推荐】
怀石料理：京都传统料理，建议提前预订
抹茶甜品：宇治抹茶冰淇淋、抹茶冰淇淋
豆腐料理：南禅寺、清水寺附近豆腐料理店
祗园小吃：章鱼烧、鲷鱼烧等传统小吃

【交通建议】
购买京都巴士一日券：适合多个景点游览
购买地铁巴士一日券：使用范围更广
岚山方向：乘坐JR嵯峨野线或岚电

【住宿区域】
祗园/河原町：市中心，交通便利
岚山：环境安静，适合度假
京都站：交通枢纽，方便出行

【实用贴士】
寺庙礼仪：进入本殿前需要洗手（手水舍），拍摄佛像前确认是否允许
摄影时间：清晨和傍晚是最佳摄影时间，避开游客高峰
预约参观：部分寺庙和怀石料理店需要提前预约
""",
    
    "巴黎": """
巴黎旅游攻略指南

【最佳游览时间】
春季（4-6月）：气候温和，游客相对较少，适合户外活动
夏季（7-8月）：旅游旺季，天气温暖，有音乐节和沙滩节
秋季（9-11月）：天气凉爽，秋色宜人，艺术展览季
冬季（12-2月）：寒冷但浪漫，圣诞市场和新年庆典

【必游景点】
埃菲尔铁塔：巴黎地标，建议日落时分登塔，夜晚整点闪烁
卢浮宫：世界最大博物馆，建议至少预留4小时，提前在线购票
圣母院：哥特式建筑代表，目前正在修复中，可外观
凯旋门：香榭丽舍大街起点，顶部可俯瞰巴黎全景
蒙马特高地：艺术家聚集地，圣心大教堂可俯瞰巴黎
塞纳河游船：欣赏两岸风光，建议傍晚时分乘坐

【艺术殿堂】
奥赛博物馆：印象派作品，前身为火车站
蓬皮杜中心：现代艺术，外观设计独特
莫奈博物馆：莫奈睡莲系列原作
罗丹美术馆：雕塑作品，花园很美

【美食推荐】
法式面包：前往街角面包店购买新鲜法棍
法式甜品：马卡龙、闪电泡芙、千层酥
米其林餐厅：巴黎米其林餐厅众多，建议提前预订
咖啡馆文化：花神咖啡馆、双叟咖啡馆等文学咖啡馆

【交通建议】
购买Navigo周票：适合一周停留
购买Paris Museum Pass：博物馆通票，可免排队
地铁系统：巴黎地铁密集，但需注意安全和卫生

【住宿区域】
第一区（卢浮宫附近）：市中心，景点集中
第四区（玛黑区）：时尚区域，有很多精品店和咖啡馆
第七区（埃菲尔铁塔附近）：环境优雅，适合高端旅行
蒙马特区：艺术气息浓厚，有独特的波西米亚风情

【实用贴士】
小费文化：餐厅账单已含服务费，额外小费5-10%表示满意
礼仪文化：进入店铺要说Bonjour，离开要说Merci
安全提示：注意防范扒手，特别是在地铁和旅游热点
购物时间：多数商店周日休息，大型商场可能营业
""",
    
    "通用旅行建议": """
旅行规划通用建议和技巧

【行程规划原则】
节奏控制：每天安排3-5个景点为宜，避免过度疲劳
区域集中：按区域安排行程，减少交通时间
主题划分：每天设定主题，如文化日、自然日、美食日
预留弹性：每天预留1-2小时自由时间，应对突发情况

【住宿选择】
位置优先：优先选择交通枢纽附近或景点集中的区域
交通便利：地铁/公交步行10分钟内为佳
特色体验：选择有当地特色的住宿，如日式旅馆、法式公寓
安全第一：查看住宿评价，选择安全系数高的区域

【交通攻略】
提前研究：出发前了解目的地交通系统
购买通票：根据行程需要购买交通通票或旅游卡
路线规划：使用Google Maps或当地交通APP规划路线
备选方案：预留替代交通方式，应对交通延误

【美食探索】
本地推荐：向当地人询问推荐餐厅
街头美食：不要错过当地特色街头小吃
避开陷阱：避免选择旅游热点区域内的"游客餐厅"
尝试新事物：勇于尝试当地特色菜品

【安全注意事项】
证件备份：护照等重要证件拍照备份并上传云端
紧急联系：记录当地紧急电话和大使馆联系方式
保险购买：购买旅行保险，应对突发情况
财物安全：不携带大量现金，使用酒店保险箱

【文化礼仪】
提前了解：出发前了解目的地文化禁忌和礼仪
尊重当地：入乡随俗，尊重当地文化和习俗
语言准备：学习几句基本当地语言
礼貌待人：保持友好态度， locals更愿意帮助友善的游客

【环保旅行】
减少塑料：携带可重复使用的水瓶和购物袋
垃圾分类：遵守当地垃圾分类规定
低碳出行：尽量选择公共交通、步行或骑行
支持本地：购买当地产品和服务，支持当地经济
"""
}


def initialize_knowledge_base():
    """初始化旅行知识库"""
    print("开始初始化旅行知识库...")
    
    # 初始化客户端
    from coze_coding_utils.runtime_ctx.context import new_context
    ctx = new_context(method="init_knowledge")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)
    
    # 配置文档分块
    chunk_config = ChunkConfig(
        separator="\n\n",
        max_tokens=1500,  # 每块1500 tokens
        remove_extra_spaces=True,
        remove_urls_emails=False
    )
    
    # 准备文档列表
    documents = []
    
    for destination, content in TRAVEL_KNOWLEDGE.items():
        doc = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=content,
            metadata={
                "destination": destination,
                "type": "travel_guide",
                "language": "zh-CN"
            }
        )
        documents.append(doc)
        print(f"✓ 准备导入: {destination}")
    
    # 批量导入知识库
    try:
        response = client.add_documents(
            documents=documents,
            table_name="travel_knowledge",
            chunk_config=chunk_config
        )
        
        if response.code == 0:
            print(f"\n✅ 成功导入 {len(response.doc_ids)} 篇旅游文档到知识库")
            print(f"文档ID: {response.doc_ids}")
            return True
        else:
            print(f"\n❌ 导入失败: {response.msg}")
            return False
            
    except Exception as e:
        print(f"\n❌ 导入过程出错: {str(e)}")
        return False


def add_custom_knowledge(content: str, destination: str = None):
    """
    添加自定义知识到知识库
    
    Args:
        content: 知识内容
        destination: 可选，关联的目的地
    """
    from coze_coding_utils.runtime_ctx.context import new_context
    ctx = new_context(method="add_custom_knowledge")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)
    
    doc = KnowledgeDocument(
        source=DataSourceType.TEXT,
        raw_data=content,
        metadata={
            "destination": destination,
            "type": "custom_knowledge",
            "language": "zh-CN"
        }
    )
    
    try:
        response = client.add_documents(
            documents=[doc],
            table_name="travel_knowledge"
        )
        
        if response.code == 0:
            print(f"✅ 成功添加自定义知识，文档ID: {response.doc_ids}")
            return response.doc_ids[0]
        else:
            print(f"❌ 添加失败: {response.msg}")
            return None
            
    except Exception as e:
        print(f"❌ 添加过程出错: {str(e)}")
        return None


if __name__ == "__main__":
    # 初始化知识库
    success = initialize_knowledge_base()
    
    if success:
        print("\n🎉 知识库初始化完成！")
        print("\n你可以通过以下方式使用知识库：")
        print("1. Agent将自动调用知识搜索工具")
        print("2. 可以使用CLI搜索：coze-coding-ai knowledge search --query '东京美食' --top-k 3")
        print("3. 添加自定义知识：python -c \"from tools.init_knowledge import add_custom_knowledge; add_custom_knowledge('你的内容', '目的地')\"")
    else:
        print("\n⚠️ 知识库初始化失败，请检查网络连接和配置")
