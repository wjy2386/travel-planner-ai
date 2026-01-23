"""
知识采集系统测试

测试完整的知识采集流程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
from tools.page_reader_tool import extract_webpage_content
from agents.knowledge_harvester_agent import build_harvester_agent
from storage.knowledge_schemas import AttractionSchema, AccommodationSchema, Source


def test_schema_validation():
    """测试Schema数据模型"""
    print("\n" + "="*60)
    print("测试1: Schema数据模型")
    print("="*60)
    
    test_passed = True
    
    # 测试景点Schema
    attraction = AttractionSchema(
        name="浅草寺",
        destination="东京",
        description="东京最古老的寺庙",
        source=Source(
            url="https://example.com",
            publisher="东京都台东区",
            crawl_date="2024-01-01T00:00:00"
        )
    )
    
    is_valid, errors = attraction.validate()
    
    if is_valid:
        print("✓ 景点Schema校验通过")
        print(f"  名称: {attraction.name}")
        print(f"  目的地: {attraction.destination}")
    else:
        print(f"✗ 景点Schema校验失败: {errors}")
        test_passed = False
    
    # 测试缺少必填字段的情况
    invalid_attraction = AttractionSchema(
        name="测试景点",
        destination=""
    )
    
    is_valid, errors = invalid_attraction.validate()
    
    if not is_valid:
        print("✓ 正确识别缺少必填字段")
        print(f"  错误: {errors}")
    else:
        print("✗ 未能识别缺少必填字段")
        test_passed = False
    
    return test_passed


def test_page_extraction():
    """测试页面内容提取"""
    print("\n" + "="*60)
    print("测试2: 页面内容提取")
    print("="*60)
    
    # 使用一个测试URL
    test_url = "https://www.gotokyo.org/"
    
    try:
        result = extract_webpage_content.func(test_url, None)
        
        if "skip" in result:
            print(f"✗ 页面提取失败: {result}")
            return False
        
        data = json.loads(result)
        
        if data.get("status") == "success":
            print("✓ 页面提取成功")
            print(f"  标题: {data.get('metadata', {}).get('title', '')}")
            print(f"  内容长度: {len(data.get('content', ''))} 字符")
            print(f"  发布机构: {data.get('metadata', {}).get('publisher', '')}")
            return True
        else:
            print(f"✗ 页面提取返回失败状态: {data.get('status')}")
            return False
    
    except Exception as e:
        print(f"✗ 页面提取异常: {str(e)}")
        return False


def test_agent_creation():
    """测试Agent创建"""
    print("\n" + "="*60)
    print("测试3: Agent创建")
    print("="*60)
    
    try:
        agent = build_harvester_agent()
        print("✓ 知识采集Agent创建成功")
        print(f"  Agent类型: {type(agent)}")
        return True
    except Exception as e:
        print(f"✗ Agent创建失败: {str(e)}")
        return False


def test_data_validator():
    """测试数据校验器"""
    print("\n" + "="*60)
    print("测试4: 数据校验器")
    print("="*60)
    
    from storage.knowledge_validator import validate_data
    
    # 测试有效数据
    valid_data = {
        "type": "attraction",
        "name": "测试景点",
        "destination": "东京",
        "description": "这是一个测试景点",
        "source": {
            "url": "https://example.com",
            "publisher": "测试机构",
            "crawl_date": "2024-01-01T00:00:00"
        }
    }
    
    is_valid, errors, needs_review = validate_data(valid_data)
    
    if is_valid:
        print("✓ 有效数据校验通过")
    else:
        print(f"✗ 有效数据校验失败: {errors}")
    
    # 测试无效数据
    invalid_data = {
        "type": "attraction",
        "name": "",
        "destination": ""
    }
    
    is_valid, errors, needs_review = validate_data(invalid_data)
    
    if not is_valid:
        print("✓ 正确识别无效数据")
        print(f"  错误数量: {len(errors)}")
    else:
        print("✗ 未能识别无效数据")
    
    return True


def test_workflow_creation():
    """测试工作流创建"""
    print("\n" + "="*60)
    print("测试5: 工作流创建")
    print("="*60)
    
    try:
        from tools.knowledge_harvest_workflow import KnowledgeHarvestWorkflow
        
        # 创建工作流（不连接数据库）
        workflow = KnowledgeHarvestWorkflow(database_url="sqlite:///test.db")
        print("✓ 工作流创建成功")
        return True
    except Exception as e:
        print(f"✗ 工作流创建失败: {str(e)}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "█"*60)
    print("知识采集系统测试套件")
    print("█"*60)
    
    results = []
    
    # 运行测试
    results.append(("Schema数据模型", test_schema_validation()))
    results.append(("页面内容提取", test_page_extraction()))
    results.append(("Agent创建", test_agent_creation()))
    results.append(("数据校验器", test_data_validator()))
    results.append(("工作流创建", test_workflow_creation()))
    
    # 打印总结
    print("\n" + "█"*60)
    print("测试总结")
    print("█"*60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
