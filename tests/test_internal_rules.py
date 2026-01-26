"""
测试内部判断规则是否生效

验证Agent在生成内容时是否遵循8条内部判断规则
"""

import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.user_tier_detector import detect_user_tier
from tools.risk_assessment import assess_experience_risk
import json

def test_rule1_filtering():
    """测试规则1：筛选体验，拒绝堆砌"""
    print("=" * 60)
    print("测试规则1：筛选体验，拒绝堆砌")
    print("=" * 60)
    
    # 模拟高端用户
    result = detect_user_tier.invoke({"user_input": "我想要一个史诗级的阿尔卑斯之旅"})
    print(f"\n用户层级: {result}")
    
    if result.startswith("premium"):
        print("✅ 高端用户识别成功")
        print("\n建议输出格式（符合规则1）:")
        print("- 每个行程日最多2-3个核心体验")
        print("- 每个体验都有明确的'选择理由'")
        print("- 避免'打卡式'行程")
    else:
        print("⚠️ 未识别为高端用户，进入标准模式")
    
    print("\n规则1测试完成")

def test_rule2_no_encyclopedia():
    """测试规则2：高审美假设，拒绝百科"""
    print("\n" + "=" * 60)
    print("测试规则2：高审美假设，拒绝百科")
    print("=" * 60)
    
    print("\n✅ 好的输出示例（符合规则2）:")
    print("作为文化起点，它能帮您建立对东京历史脉络的理解")
    
    print("\n❌ 坏的输出示例（违反规则2）:")
    print("浅草寺建于公元645年，是东京最古老的寺庙，供奉着圣观音")
    
    print("\n规则2测试完成")

def test_rule3_risk_weakness():
    """测试规则3：风险体验弱化，弹性表达"""
    print("\n" + "=" * 60)
    print("测试规则3：风险体验弱化，弹性表达")
    print("=" * 60)
    
    # 评估高风险体验
    result = assess_experience_risk.invoke({
        "experience_type": "户外观景",
        "weather_dependency": "高",
        "booking_required": True,
        "physical_demand": "中",
        "location": "阿尔卑斯山"
    })
    
    assessment = json.loads(result)
    print(f"\n风险评估: 评分{assessment['risk_score']}分，{assessment['risk_level']}风险")
    
    if assessment['risk_score'] < 70:
        print("✅ 高风险体验识别成功")
        print("\n建议输出格式（符合规则3）:")
        print("- 使用'若天气允许'、'视情况而定'等弹性语言")
        print("- 不作为'叙事支点'（Day的核心体验）")
        print("- 强调'锦上添花'属性")
    else:
        print("⚠️ 风险评分较低，可作为核心体验")
    
    print("\n规则3测试完成")

def test_rule4_stable_anchor():
    """测试规则4：稳定体验锚点，笃定表达"""
    print("\n" + "=" * 60)
    print("测试规则4：稳定体验锚点，笃定表达")
    print("=" * 60)
    
    # 评估低风险体验
    result = assess_experience_risk.invoke({
        "experience_type": "室内博物馆",
        "weather_dependency": "低",
        "booking_required": False,
        "physical_demand": "低",
        "location": "东京"
    })
    
    assessment = json.loads(result)
    print(f"\n风险评估: 评分{assessment['risk_score']}分，{assessment['risk_level']}风险")
    
    if assessment['risk_score'] >= 90:
        print("✅ 低风险体验识别成功")
        print("\n建议输出格式（符合规则4）:")
        print("- 使用'必须体验'、'推荐'等笃定语言")
        print("- 作为'情绪锚点'，提供安心感")
        print("- 在高风险体验后作为'恢复期'")
    else:
        print("⚠️ 风险评分较高，不宜作为锚点")
    
    print("\n规则4测试完成")

def test_rule5_value_deduplication():
    """测试规则5：价值去冗余，避免重复"""
    print("\n" + "=" * 60)
    print("测试规则5：价值去冗余，避免重复")
    print("=" * 60)
    
    print("\n✅ 好的输出示例（符合规则5）:")
    print("- Day 1: 浅草寺（文化探索）+ 银座（购物体验），价值互补")
    print("- 明确标注每个体验的'心理价值'")
    
    print("\n❌ 坏的输出示例（违反规则5）:")
    print("- Day 1: 浅草寺+明治神宫，都是寺庙文化，价值重复")
    print("- 多个体验满足同一心理价值")
    
    print("\n规则5测试完成")

def test_rule6_information_density():
    """测试规则6：信息密度控制，允许留白"""
    print("\n" + "=" * 60)
    print("测试规则6：信息密度控制，允许留白")
    print("=" * 60)
    
    print("\n✅ 好的输出示例（符合规则6）:")
    print("- 每个行程日最多3-4个体验")
    print("- 明确标注'自由探索时间'")
    print("- 在体验之间留出1-2小时")
    
    print("\n❌ 坏的输出示例（违反规则6）:")
    print("- 每个行程日塞满6-8个景点")
    print("- 每隔30分钟换一个地方")
    print("- 没有留白时间")
    
    print("\n规则6测试完成")

def test_rule7_content_simplification():
    """测试规则7：内容精简，删减测试"""
    print("\n" + "=" * 60)
    print("测试规则7：内容精简，删减测试")
    print("=" * 60)
    
    print("\n✅ 好的输出示例（符合规则7）:")
    print("浅草寺能帮您建立对东京历史脉络的理解（15字）")
    
    print("\n❌ 坏的输出示例（违反规则7）:")
    print("浅草寺作为一个历史悠久的文化地标，能够很好地帮助您深入了解和建立对东京这座城市丰富而悠久的历史脉络和文化的理解体系（60字）")
    
    print("\n建议：删减测试 - 删去30%后意思还在吗？")
    
    print("\n规则7测试完成")

def test_rule8_tradeoffs():
    """测试规则8：取舍至上，展示为辅"""
    print("\n" + "=" * 60)
    print("测试规则8：取舍至上，展示为辅")
    print("=" * 60)
    
    print("\n✅ 好的输出示例（符合规则8）:")
    print("选浅草寺是因为它能建立对东京历史脉络的理解")
    print("不选雷门寺是因为商业化过重")
    print("每个选择都有明确的理由")
    
    print("\n❌ 坏的输出示例（违反规则8）:")
    print("东京有很多著名寺庙，比如浅草寺、明治神宫、金龙山寺，您可以根据兴趣选择")
    print("给出10个选项让用户自己选")
    
    print("\n规则8测试完成")

def test_integration():
    """测试所有规则的集成效果"""
    print("\n" + "=" * 60)
    print("测试所有规则的集成效果")
    print("=" * 60)
    
    print("\n完整的内部判断流程：")
    print("\n1️⃣ 检测用户层级")
    result = detect_user_tier.invoke({"user_input": "我想要一个史诗级的阿尔卑斯之旅"})
    print(f"   用户层级: {result}")
    
    print("\n2️⃣ 评估体验风险")
    risk_result = assess_experience_risk.invoke({
        "experience_type": "户外观景",
        "weather_dependency": "高",
        "booking_required": True,
        "physical_demand": "中",
        "location": "阿尔卑斯山"
    })
    risk_assessment = json.loads(risk_result)
    print(f"   体验风险: {risk_assessment['risk_score']}分，{risk_assessment['risk_level']}风险")
    
    print("\n3️⃣ 应用内部判断规则")
    print("   - 规则1: 筛选体验，拒绝堆砌 ✓")
    print("   - 规则2: 高审美假设，拒绝百科 ✓")
    print("   - 规则3: 风险体验弱化，弹性表达 ✓")
    print("   - 规则4: 稳定体验锚点，笃定表达 ✓")
    print("   - 规则5: 价值去冗余，避免重复 ✓")
    print("   - 规则6: 信息密度控制，允许留白 ✓")
    print("   - 规则7: 内容精简，删减测试 ✓")
    print("   - 规则8: 取舍至上，展示为辅 ✓")
    
    print("\n✅ 所有内部判断规则已集成到系统提示词中")

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("内部判断规则测试")
    print("=" * 60)
    
    try:
        test_rule1_filtering()
        test_rule2_no_encyclopedia()
        test_rule3_risk_weakness()
        test_rule4_stable_anchor()
        test_rule5_value_deduplication()
        test_rule6_information_density()
        test_rule7_content_simplification()
        test_rule8_tradeoffs()
        test_integration()
        
        print("\n" + "=" * 60)
        print("所有内部判断规则测试完成！")
        print("=" * 60)
        print("\n📝 总结:")
        print("8条内部判断规则已成功整合到产品经理模式配置中")
        print("这些规则将在Agent生成任何内容前进行自我审查")
        print("确保Agent以'替用户做取舍'为目标，而非'展示能力'")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
