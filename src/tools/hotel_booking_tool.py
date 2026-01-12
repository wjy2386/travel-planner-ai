"""
酒店预订工具 - 执行酒店预订操作
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from typing import Optional
import json
from datetime import datetime
import uuid

# 模拟订单存储（实际应使用数据库）
BOOKING_RECORDS = []


@tool
def book_hotel(
    runtime: ToolRuntime,
    hotel_name: str,
    city: str,
    check_in_date: str,
    check_out_date: str,
    guests: int,
    room_type: str = "",
    guest_name: str = "",
    contact_phone: str = "",
    special_requests: str = ""
) -> str:
    """
    预订酒店。
    
    Args:
        runtime: 运行时上下文
        hotel_name: 酒店名称，例如："浅草华盛顿酒店"
        city: 城市名称，例如："东京"
        check_in_date: 入住日期，格式：YYYY-MM-DD
        check_out_date: 退房日期，格式：YYYY-MM-DD
        guests: 客人数量
        room_type: 房间类型，例如："双床房"、"大床房"
        guest_name: 客人姓名（可选）
        contact_phone: 联系电话（可选）
        special_requests: 特殊要求（可选）
        
    Returns:
        预订结果，包含订单ID、预订状态、酒店信息等
    """
    try:
        # 生成唯一订单ID
        booking_id = f"HTL-{uuid.uuid4().hex[:8].upper()}"
        
        # 构建订单信息
        booking_info = {
            "booking_id": booking_id,
            "type": "hotel",
            "hotel_name": hotel_name,
            "city": city,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "guests": guests,
            "room_type": room_type,
            "guest_name": guest_name,
            "contact_phone": contact_phone,
            "special_requests": special_requests,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到模拟数据库
        BOOKING_RECORDS.append(booking_info)
        
        # 格式化输出
        result = f"""✅ 酒店预订成功

**订单信息**
- 订单号: {booking_id}
- 酒店: {hotel_name}
- 城市: {city}
- 入住日期: {check_in_date}
- 退房日期: {check_out_date}
- 客人数: {guests}
- 房间类型: {room_type}
- 客人姓名: {guest_name}
- 联系电话: {contact_phone}

**预订状态**: 已确认
**预订时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ 请注意:
- 请在入住当天携带有效证件
- 建议提前1小时到达办理入住
- 如需取消或修改，请联系酒店前台
- 特殊要求: {special_requests if special_requests else '无'}
"""
        return result
        
    except Exception as e:
        return f"❌ 酒店预订失败: {str(e)}"


@tool
def cancel_hotel_booking(
    runtime: ToolRuntime,
    booking_id: str,
    reason: str = ""
) -> str:
    """
    取消酒店预订。
    
    Args:
        runtime: 运行时上下文
        booking_id: 订单号，例如："HTL-12345678"
        reason: 取消原因
        
    Returns:
        取消结果
    """
    try:
        # 查找订单
        booking = None
        for record in BOOKING_RECORDS:
            if record["booking_id"] == booking_id and record["type"] == "hotel":
                booking = record
                break
        
        if not booking:
            return f"❌ 未找到订单号: {booking_id}"
        
        if booking["status"] == "cancelled":
            return f"⚠️ 订单 {booking_id} 已取消，无需重复操作"
        
        # 更新订单状态
        booking["status"] = "cancelled"
        booking["cancelled_at"] = datetime.now().isoformat()
        booking["cancel_reason"] = reason
        
        result = f"""✅ 酒店预订已取消

**订单信息**
- 订单号: {booking_id}
- 酒店: {booking['hotel_name']}
- 取消时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 取消原因: {reason if reason else '用户主动取消'}

❗️ 温馨提示:
- 取消操作不可恢复
- 如需重新预订，请重新发起预订请求
"""
        return result
        
    except Exception as e:
        return f"❌ 取消预订失败: {str(e)}"


@tool
def query_hotel_booking(
    runtime: ToolRuntime,
    booking_id: str
) -> str:
    """
    查询酒店预订详情。
    
    Args:
        runtime: 运行时上下文
        booking_id: 订单号
        
    Returns:
        预订详情
    """
    try:
        # 查找订单
        booking = None
        for record in BOOKING_RECORDS:
            if record["booking_id"] == booking_id and record["type"] == "hotel":
                booking = record
                break
        
        if not booking:
            return f"❌ 未找到订单号: {booking_id}"
        
        status_map = {
            "confirmed": "✅ 已确认",
            "cancelled": "❌ 已取消",
            "pending": "⏳ 待处理"
        }
        
        result = f"""📋 酒店预订详情

**订单信息**
- 订单号: {booking['booking_id']}
- 预订状态: {status_map.get(booking['status'], booking['status'])}
- 预订时间: {booking['created_at']}

**酒店信息**
- 酒店: {booking['hotel_name']}
- 城市: {booking['city']}
- 入住日期: {booking['check_in_date']}
- 退房日期: {booking['check_out_date']}
- 客人数: {booking['guests']}
- 房间类型: {booking['room_type']}

**客人信息**
- 姓名: {booking['guest_name']}
- 联系电话: {booking['contact_phone']}
- 特殊要求: {booking['special_requests'] if booking['special_requests'] else '无'}

{f"**取消信息**\\n- 取消时间: {booking['cancelled_at']}\\n- 取消原因: {booking['cancel_reason']}" if booking.get('cancelled_at') else ''}
"""
        return result
        
    except Exception as e:
        return f"❌ 查询预订失败: {str(e)}"
