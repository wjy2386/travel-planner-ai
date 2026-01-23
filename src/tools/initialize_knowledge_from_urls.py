"""
从官方网站URL批量导入旅行知识库

该脚本从权威旅游网站和景点官网批量导入内容到知识库，
为Agent提供高质量、可溯源的专业旅行信息。
"""

import time
from typing import List
from coze_coding_dev_sdk import KnowledgeClient, Config, ChunkConfig
from coze_coding_dev_sdk.knowledge.models import KnowledgeDocument, DataSourceType
from coze_coding_utils.runtime_ctx.context import new_context

# 知识库名称
KNOWLEDGE_BASE_NAME = "travel_knowledge"

# 官方网站URL列表 - 按地区分类
OFFICIAL_URLS = {
    "东京": [
        {
            "url": "https://www.gotokyo.org/",
            "description": "东京观光局官网 - 东京官方旅游指南"
        },
        {
            "url": "https://www.tokyotower.co.jp/",
            "description": "东京塔官网 - 地标建筑官方信息"
        },
        {
            "url": "https://www.japan.travel/spot/651/",
            "description": "浅草寺官方信息 - 日本国家旅游局"
        },
        {
            "url": "https://www.japan.travel/spot/657/",
            "description": "新宿御苑官方信息"
        },
        {
            "url": "https://www.japan-travel.go.jp/spot/663/",
            "description": "明治神宫官方信息"
        },
        {
            "url": "https://www.japan.travel/spot/1113/",
            "description": "涩谷区官方旅游信息"
        },
        {
            "url": "https://www.shinjukuku.or.jp/english/",
            "description": "新宿区官方英文网站"
        }
    ],
    "京都": [
        {
            "url": "https://kyoto.travel/",
            "description": "京都观光协会官网 - 京都官方旅游指南"
        },
        {
            "url": "https://www.kiyomizuyera.or.jp/",
            "description": "清水寺官方网站"
        },
        {
            "url": "https://www.kinkakuji.or.jp/",
            "description": "金阁寺官方网站"
        },
        {
            "url": "https://www.japan.travel/spot/1095/",
            "description": "伏见稻荷大社官方信息"
        },
        {
            "url": "https://www.arashiyama.or.jp/",
            "description": "岚山观光协会官网"
        },
        {
            "url": "https://www.japan.travel/spot/1094/",
            "description": "天龙寺官方信息"
        }
    ],
    "巴黎": [
        {
            "url": "https://www.parisinfo.com/",
            "description": "巴黎旅游局官网 - 巴黎官方旅游指南"
        },
        {
            "url": "https://www.toureiffel.paris/",
            "description": "埃菲尔铁塔官方网站"
        },
        {
            "url": "https://www.louvre.fr/",
            "description": "卢浮宫官方网站"
        },
        {
            "url": "https://www.musee-orsay.fr/",
            "description": "奥赛博物馆官方网站"
        },
        {
            "url": "https://www.centrepompidou.fr/",
            "description": "蓬皮杜中心官方网站"
        },
        {
            "url": "https://www.sacre-coeur-montmartre.com/",
            "description": "圣心大教堂官方网站"
        }
    ],
    "通用旅行": [
        {
            "url": "https://www.japan.travel/",
            "description": "日本国家旅游局官网 - 全日本旅游信息"
        },
        {
            "url": "https://www.france.fr/",
            "description": "法国旅游发展署官网"
        },
        {
            "url": "https://www.lonelyplanet.com/",
            "description": "Lonely Planet - 专业旅行指南"
        }
    ]
}


def create_client():
    """创建知识库客户端"""
    ctx = new_context(method="init_knowledge_from_urls")
    config = Config()
    return KnowledgeClient(config=config, ctx=ctx)


def import_url(url: str, description: str = "", client: KnowledgeClient = None) -> bool:
    """
    导入单个URL到知识库
    
    Args:
        url: 要导入的网址
        description: 网站描述（用于元数据）
        client: 知识库客户端
    
    Returns:
        是否成功
    """
    try:
        if client is None:
            client = create_client()
        
        # 创建文档
        doc = KnowledgeDocument(
            source=DataSourceType.URL,
            url=url
        )
        
        # 配置分块策略
        chunk_config = ChunkConfig(
            separator="\n\n",
            max_tokens=1500,
            remove_extra_spaces=True
        )
        
        # 导入文档
        response = client.add_documents(
            documents=[doc],
            table_name=KNOWLEDGE_BASE_NAME,
            chunk_config=chunk_config
        )
        
        if response.code == 0:
            print(f"✓ 成功导入: {url}")
            if description:
                print(f"  描述: {description}")
            return True
        else:
            print(f"✗ 导入失败: {url}")
            print(f"  错误: {response.msg}")
            return False
            
    except Exception as e:
        print(f"✗ 导入异常: {url}")
        print(f"  异常: {str(e)}")
        return False


def import_region_urls(region: str, urls: List[dict], client: KnowledgeClient = None) -> dict:
    """
    批量导入某个地区的URL
    
    Args:
        region: 地区名称
        urls: URL列表，每项包含url和description
        client: 知识库客户端
    
    Returns:
        导入统计
    """
    print(f"\n{'='*60}")
    print(f"开始导入 {region} 的官方网站内容")
    print(f"{'='*60}")
    
    if client is None:
        client = create_client()
    
    success_count = 0
    fail_count = 0
    
    for item in urls:
        url = item.get("url")
        description = item.get("description", "")
        
        if import_url(url, description, client):
            success_count += 1
        else:
            fail_count += 1
        
        # 避免请求过快，每次导入间隔1秒
        time.sleep(1)
    
    print(f"\n{region} 导入完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    return {
        "region": region,
        "success": success_count,
        "fail": fail_count,
        "total": len(urls)
    }


def initialize_knowledge_base(regions: List[str] = None):
    """
    初始化知识库，批量导入官方网站内容
    
    Args:
        regions: 要导入的地区列表，如 ["东京", "京都", "巴黎"]
                 如果为None，则导入所有地区
    """
    print("="*60)
    print("旅行知识库初始化 - 从官方网站批量导入")
    print("="*60)
    
    # 确定要导入的地区
    if regions is None:
        regions = list(OFFICIAL_URLS.keys())
    
    print(f"计划导入的地区: {', '.join(regions)}")
    print(f"知识库名称: {KNOWLEDGE_BASE_NAME}")
    print()
    
    # 创建客户端
    client = create_client()
    
    # 统计结果
    stats = []
    
    # 逐个地区导入
    for region in regions:
        if region in OFFICIAL_URLS:
            result = import_region_urls(region, OFFICIAL_URLS[region], client)
            stats.append(result)
        else:
            print(f"⚠ 警告: 未找到地区 '{region}' 的URL列表")
    
    # 打印总统计
    print(f"\n{'='*60}")
    print("导入完成 - 总体统计")
    print(f"{'='*60}")
    print(f"地区数: {len(stats)}")
    total_success = sum(s['success'] for s in stats)
    total_fail = sum(s['fail'] for s in stats)
    total_urls = sum(s['total'] for s in stats)
    print(f"URL总数: {total_urls}")
    print(f"成功: {total_success}")
    print(f"失败: {total_fail}")
    print(f"成功率: {total_success/total_urls*100:.1f}%" if total_urls > 0 else "成功率: 0%")
    print()
    
    return {
        "regions": stats,
        "total_success": total_success,
        "total_fail": total_fail,
        "total_urls": total_urls
    }


if __name__ == "__main__":
    # 示例1: 导入所有地区
    print("示例1: 导入所有地区")
    initialize_knowledge_base()
    
    # 示例2: 只导入东京和京都
    # print("\n示例2: 只导入东京和京都")
    # initialize_knowledge_base(["东京", "京都"])
    
    # 示例3: 只导入单个地区
    # print("\n示例3: 只导入东京")
    # initialize_knowledge_base(["东京"])
