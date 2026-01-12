"""
票务预订工具 - 执行景点门票预订操作
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from typing import Optional
from datetime import datetime
import uuid

# 模拟订单存储（实际应使用数据库）
BOOKING_RECORDS = []


@tool
def book_ticket(
    runtime: ToolRuntime,
    attraction_name: str,
    city: str,
    visit_date: str,
    visitors: int,
    ticket_type: str,
    visitor_name: str = "",
    contact_phone: str = "",
    special_requests: str = ""
) -> str:
    """
    预订景点门票。
    
    Args:
        runtime: 运行时上下文
        attraction_name: 景点名称，例如："迪士尼乐园"、"浅草寺"
        city: 城市名称，例如："东京"
        visit_date: 参观日期，格式：YYYY-MM-DD
        visitors: 参观人数
        ticket_type: 票务类型，例如："一日票"、"快速通行证"
        visitor_name: 订票人姓名（可选）
        contact_phone: 联系电话（可选）
        special_requests: 特殊要求（可选）
        
    Returns:
        预订结果，包含订单ID、预订状态、票务信息等
    """
    try:
        # 生成唯一订单ID
        booking_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        # 构建订单信息
        booking_info = {
            "booking_id": booking_id,
            "type": "ticket",
            "attraction_name": attraction_name,
            "city": city,
            "visit_date": visit_date,
            "visitors": visitors,
            "ticket_type": ticket_type,
            "visitor_name": visitor_name,
            "contact_phone": contact_phone,
            "special_requests": special_requests,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到模拟数据库
        BOOKING_RECORDS.append(booking_info)
        
        # 格式化输出
        result = f"""✅ 门票预订成功

**订单信息**
- 订单号: {booking_id}
- 景点: {attraction_name}
- 城市: {city}
- 参观日期: {visit_date}
- 参观人数: {visitors}
- 票务类型: {ticket_type}
- 订票人姓名: {visitor_name}
- 联系电话: {contact_phone}

**预订状态**: 已确认
**预订时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ 请注意:
- 请在参观当天携带有效证件和电子票
- 建议提前30分钟到达景区入口
- 快速通行证需要与门票同时使用
- 如需取消或修改，请联系景区客服
- 特殊要求: {special_requests if special_requests else '无'}

💡 入场提示:
- 保存电子票二维码或订单号
- 部分景区需要实名验证
- 建议提前了解景区开放时间和注意事项
"""
        return result
        
    except Exception as e:
        return f"❌ 门票预订失败: {str(e)}"


@tool
def cancel_ticket_booking(
    runtime: ToolRuntime,
    booking_id: str,
    reason: str = ""
) -> str:
    """
    取消门票预订。
    
    Args:
        runtime: 运行时上下文
        booking_id: 订单号，例如："TKT-12345678"
        reason: 取消原因
        
    Returns:
        取消结果
    """
    try:
        # 查找订单
        booking = None
        for record in BOOKING_RECORDS:
            if record["booking_id"] == booking_id and record["type"] == "ticket":
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
        
        result = f"""✅ 门票预订已取消

**订单信息**
- 订单号: {booking_id}
- 景点: {booking['attraction_name']}
- 参观日期: {booking['visit_date']}
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
def query_ticket_booking(
    runtime: ToolRuntime,
    booking_id: str
) -> str:
    """
    查询门票预订详情。
    
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
            if record["booking_id"] == booking_id and record["type"] == "ticket":
                booking = record
                break
        
        if not booking:
            return f"❌ 未找到订单号: {booking_id}"
        
        status_map = {
            "confirmed": "✅ 已确认",
            "cancelled": "❌ 已取消",
            "pending": "⏳ 待处理"
        }
        
        result = f"""📋 门票预订详情

**订单信息**
- 订单号: {booking['booking_id']}
- 预订状态: {status_map.get(booking['status'], booking['status'])}
- 预订时间: {booking['created_at']}

**票务信息**
- 景点: {booking['attraction_name']}
- 城市: {booking['city']}
- 参观日期: {booking['visit_date']}
- 参观人数: {booking['visitors']}
- 票务类型: {booking['ticket_type']}

**订票人信息**
- 姓名: {booking['visitor_name']}
- 联系电话: {booking['contact_phone']}
- 特殊要求: {booking['special_requests'] if booking['special_requests'] else '无'}

{f"**取消信息**\\n- 取消时间: {booking['cancelled_at']}\\n- 取消原因: {booking['cancel_reason']}" if booking.get('cancelled_at') else ''}
"""
        return result
        
    except Exception as e:
        return f"❌ 查询预订失败: {str(e)}"
