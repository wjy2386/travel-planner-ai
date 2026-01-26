"""
测试产品经理模式的核心工具
"""

import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.user_tier_detector import detect_user_tier, get_premium_mode_config
from tools.risk_assessment import assess_experience_risk, generate_fallback_plan
import json

def test_user_tier_detector():
    """测试用户层级识别工具"""
    print("=" * 50)
    print("测试1: 用户层级识别工具")
    print("=" * 50)
    
    # 测试用例1: 标准用户
    result1 = detect_user_tier.invoke({"user_input": "我想去东京旅游3天"})
    print(f"\n测试1.1: 标准用户")
    print(f"输入: '我想去东京旅游3天'")
    print(f"输出: {result1}")
    print(f"预期: 'standard'")
    print(f"结果: {'✅ 通过' if result1 == 'standard' else '❌ 失败'}")
    
    # 测试用例2: 高端用户
    result2 = detect_user_tier.invoke({"user_input": "我想要一个史诗级的阿尔卑斯之旅，体验独特的秘境和定制服务"})
    print(f"\n测试1.2: 高端用户")
    print(f"输入: '我想要一个史诗级的阿尔卑斯之旅，体验独特的秘境和定制服务'")
    print(f"输出: {result2}")
    print(f"预期: 'premium (matched: [...])'")
    print(f"结果: {'✅ 通过' if result2.startswith('premium') else '❌ 失败'}")
    
    # 测试用例3: 接近高端（只有1个关键词）
    result3 = detect_user_tier.invoke({"user_input": "我想要一个高端的旅行体验"})
    print(f"\n测试1.3: 接近高端（只有1个关键词）")
    print(f"输入: '我想要一个高端的旅行体验'")
    print(f"输出: {result3}")
    print(f"预期: 'standard'")
    print(f"结果: {'✅ 通过' if result3 == 'standard' else '❌ 失败'}")
    
    print("\n" + "=" * 50)
    print("用户层级识别工具测试完成")
    print("=" * 50)

def test_risk_assessment():
    """测试风险评估工具"""
    print("\n" + "=" * 50)
    print("测试2: 风险评估工具")
    print("=" * 50)
    
    # 测试用例1: 低风险体验（室内博物馆）
    result1 = assess_experience_risk.invoke({
        "experience_type": "室内博物馆",
        "weather_dependency": "低",
        "booking_required": False,
        "physical_demand": "低",
        "location": "东京"
    })
    print(f"\n测试2.1: 低风险体验（室内博物馆）")
    print(f"输入: experience_type='室内博物馆', weather_dependency='低', booking_required=False, physical_demand='低'")
    assessment1 = json.loads(result1)
    print(f"输出: {json.dumps(assessment1, ensure_ascii=False, indent=2)}")
    print(f"风险评分: {assessment1['risk_score']}")
    print(f"风险等级: {assessment1['risk_level']}")
    print(f"责任分级: {assessment1['responsibility']}")
    print(f"结果: {'✅ 通过' if assessment1['risk_score'] >= 90 else '❌ 失败'}")
    
    # 测试用例2: 高风险体验（高山云海观景）
    result2 = assess_experience_risk.invoke({
        "experience_type": "户外观景",
        "weather_dependency": "高",
        "booking_required": True,
        "physical_demand": "中",
        "location": "阿尔卑斯山"
    })
    print(f"\n测试2.2: 高风险体验（高山云海观景）")
    print(f"输入: experience_type='户外观景', weather_dependency='高', booking_required=True, physical_demand='中'")
    assessment2 = json.loads(result2)
    print(f"输出: {json.dumps(assessment2, ensure_ascii=False, indent=2)}")
    print(f"风险评分: {assessment2['risk_score']}")
    print(f"风险等级: {assessment2['risk_level']}")
    print(f"责任分级: {assessment2['responsibility']}")
    print(f"结果: {'✅ 通过' if assessment2['risk_score'] < 70 else '❌ 失败'}")
    
    print("\n" + "=" * 50)
    print("风险评估工具测试完成")
    print("=" * 50)

def test_fallback_plan():
    """测试Fallback方案生成工具"""
    print("\n" + "=" * 50)
    print("测试3: Fallback方案生成工具")
    print("=" * 50)
    
    # 测试用例1: 天气和预约风险
    result1 = generate_fallback_plan.invoke({
        "original_experience": "阿尔卑斯云海观景",
        "risk_factors": ["天气", "预约"]
    })
    print(f"\n测试3.1: 天气和预约风险")
    print(f"输入: original_experience='阿尔卑斯云海观景', risk_factors=['天气', '预约']")
    print(f"输出: {result1}")
    print(f"结果: {'✅ 通过' if 'Plan A' in result1 and 'Plan B' in result1 else '❌ 失败'}")
    
    # 测试用例2: 体力风险
    result2 = generate_fallback_plan.invoke({
        "original_experience": "高山徒步",
        "risk_factors": ["体力"]
    })
    print(f"\n测试3.2: 体力风险")
    print(f"输入: original_experience='高山徒步', risk_factors=['体力']")
    print(f"输出: {result2}")
    print(f"结果: {'✅ 通过' if 'Plan A' in result2 else '❌ 失败'}")
    
    print("\n" + "=" * 50)
    print("Fallback方案生成工具测试完成")
    print("=" * 50)

def test_product_manager_config():
    """测试产品经理模式配置"""
    print("\n" + "=" * 50)
    print("测试4: 产品经理模式配置")
    print("=" * 50)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agent_llm_config_pm.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n配置文件路径: {config_path}")
        print(f"模型: {config['config']['model']}")
        print(f"Temperature: {config['config']['temperature']}")
        print(f"Max tokens: {config['config']['max_completion_tokens']}")
        print(f"工具列表: {config['tools']}")
        
        # 验证必需字段
        required_tools = ["detect_user_tier", "assess_experience_risk", "generate_fallback_plan"]
        missing_tools = [tool for tool in required_tools if tool not in config['tools']]
        
        print(f"\n验证工具列表: {'✅ 通过' if not missing_tools else '❌ 失败 - 缺少: ' + ', '.join(missing_tools)}")
        
        # 验证系统提示词长度
        sp_length = len(config['sp'])
        print(f"系统提示词长度: {sp_length} 字符")
        print(f"结果: {'✅ 通过' if sp_length > 1000 else '❌ 失败'}")
    else:
        print(f"\n❌ 配置文件不存在: {config_path}")
    
    print("\n" + "=" * 50)
    print("产品经理模式配置测试完成")
    print("=" * 50)

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("产品经理模式核心工具测试")
    print("=" * 50)
    
    try:
        test_user_tier_detector()
        test_risk_assessment()
        test_fallback_plan()
        test_product_manager_config()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
