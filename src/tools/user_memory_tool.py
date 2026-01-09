"""
用户记忆工具 - 用于长期记忆存储和查询
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from storage.database.db import get_session
from storage.database.traveler_manager import TravelerManager
from typing import List, Optional, Dict, Any
import json
import datetime


@tool
def save_user_preference(
    runtime: ToolRuntime,
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    tier: Optional[str] = None,
    preferences: Optional[List[str]] = None
) -> str:
    """
    保存用户偏好信息。
    
    Args:
        runtime: 运行时上下文
        user_id: 用户唯一标识（必填）
        name: 用户姓名（可选）
        email: 用户邮箱（可选）
        tier: 用户等级，可选值：standard(标准)/vip(高级)/platinum(白金)（可选）
        preferences: 用户偏好标签列表，例如：["历史文化", "美食", "动漫"]（可选）
        
    Returns:
        操作结果描述
    """
    try:
        from storage.database.traveler_manager import TravelerCreate, TravelerUpdate
        
        db = get_session()
        try:
            mgr = TravelerManager()
            
            # 构建更新数据
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                update_data["email"] = email
            if tier is not None:
                update_data["tier"] = tier
            if preferences is not None:
                update_data["preferences"] = preferences
            
            # 获取或创建用户
            traveler = mgr.get_traveler_by_user_id(db, user_id)
            if traveler:
                # 更新用户
                mgr.update_traveler(db, user_id, TravelerUpdate(**update_data))
                action = "更新"
            else:
                # 创建用户
                create_data = {"user_id": user_id, **update_data}
                mgr.create_traveler(db, TravelerCreate(**create_data))
                action = "创建"
            
            return f"成功{action}用户偏好信息，user_id: {user_id}"
            
        finally:
            db.close()
            
    except Exception as e:
        return f"保存用户偏好失败: {str(e)}"


@tool
def get_user_profile(
    runtime: ToolRuntime,
    user_id: str
) -> str:
    """
    获取用户画像信息，包括基本信息、偏好、历史行程等。
    
    Args:
        runtime: 运行时上下文
        user_id: 用户唯一标识（必填）
        
    Returns:
        用户画像的 JSON 字符串，包含：
        - user_id: 用户ID
        - name: 用户姓名
        - tier: 用户等级
        - preferences: 偏好标签列表
        - visited_destinations: 去过的目的地列表
        - itinerary_count: 历史行程数量
    """
    try:
        db = get_session()
        try:
            mgr = TravelerManager()
            profile = mgr.get_traveler_preferences(db, user_id)
            
            if profile is None:
                return f"未找到用户信息，user_id: {user_id}"
            
            return json.dumps(profile, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        return f"获取用户画像失败: {str(e)}"


@tool
def save_itinerary(
    runtime: ToolRuntime,
    user_id: str,
    destination: str,
    departure: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = None,
    travelers_count: Optional[int] = None,
    travel_tier: Optional[str] = None,
    preferences: Optional[List[str]] = None,
    itinerary_json: Optional[Dict[str, Any]] = None
) -> str:
    """
    保存历史行程记录。
    
    Args:
        runtime: 运行时上下文
        user_id: 用户唯一标识（必填）
        destination: 目的地（必填）
        departure: 出发地（可选）
        start_date: 开始日期，格式：YYYY-MM-DD（可选）
        end_date: 结束日期，格式：YYYY-MM-DD（可选）
        days: 天数（可选）
        travelers_count: 人数（可选）
        travel_tier: 旅行层级，可选值：大众/小资/深度/高端定制（可选）
        preferences: 本次行程偏好列表（可选）
        itinerary_json: 完整行程JSON数据（可选）
        
    Returns:
        操作结果描述
    """
    try:
        from storage.database.traveler_manager import ItineraryCreate, TravelerManager
        from datetime import datetime
        
        db = get_session()
        try:
            mgr = TravelerManager()
            
            # 获取或创建用户
            traveler = mgr.get_or_create_traveler(db, user_id)
            
            # 构建行程数据
            itinerary_data = {
                "traveler_id": traveler.id,
                "destination": destination,
                "departure": departure,
                "days": days,
                "travelers_count": travelers_count,
                "travel_tier": travel_tier,
                "preferences": preferences,
                "itinerary_json": itinerary_json
            }
            
            # 转换日期格式
            if start_date:
                itinerary_data["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                itinerary_data["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 创建行程
            mgr.create_itinerary(db, ItineraryCreate(**itinerary_data))
            
            return f"成功保存行程记录，user_id: {user_id}, destination: {destination}"
            
        finally:
            db.close()
            
    except Exception as e:
        return f"保存行程记录失败: {str(e)}"


@tool
def get_user_itineraries(
    runtime: ToolRuntime,
    user_id: str,
    destination: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    获取用户的历史行程记录。
    
    Args:
        runtime: 运行时上下文
        user_id: 用户唯一标识（必填）
        destination: 目的地筛选（可选，不填则返回所有）
        limit: 返回数量限制（可选，默认10）
        
    Returns:
        历史行程记录的 JSON 字符串
    """
    try:
        db = get_session()
        try:
            mgr = TravelerManager()
            itineraries = mgr.get_traveler_itineraries(db, user_id, destination, limit)
            
            if not itineraries:
                return f"未找到历史行程记录，user_id: {user_id}"
            
            # 格式化输出
            result = []
            for it in itineraries:
                result.append({
                    "destination": it.destination,
                    "departure": it.departure,
                    "start_date": it.start_date.strftime("%Y-%m-%d") if it.start_date else None,
                    "end_date": it.end_date.strftime("%Y-%m-%d") if it.end_date else None,
                    "days": it.days,
                    "travelers_count": it.travelers_count,
                    "travel_tier": it.travel_tier,
                    "preferences": it.preferences,
                    "status": it.status
                })
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        return f"获取历史行程失败: {str(e)}"


# 使用示例（仅供参考，不会被调用）
if __name__ == "__main__":
    # 测试工具
    class MockRuntime:
        context = None
    
    # 保存用户偏好
    result = save_user_preference(
        user_id="test_user_001",
        name="张三",
        email="zhangsan@example.com",
        tier="vip",
        preferences=["历史文化", "美食", "动漫"],
        runtime=MockRuntime()
    )
    print(result)
    
    # 获取用户画像
    result = get_user_profile(
        user_id="test_user_001",
        runtime=MockRuntime()
    )
    print(result)
