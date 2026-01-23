"""
目的地知识采集 Schema 定义

严格按照设计规范，只包含从官方网站提取的权威信息。
不包含价格、评分等UGC或商业字段。
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SchemaType(Enum):
    """Schema 类型枚举"""
    ATTRACTION = "attraction"
    ACCOMMODATION = "accommodation"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    ACTIVITY = "activity"


@dataclass
class Source:
    """数据来源信息"""
    url: str  # 来源URL
    publisher: str  # 发布机构
    crawl_date: str  # 抓取时间（ISO格式）
    
    def __post_init__(self):
        """自动设置抓取时间"""
        if not self.crawl_date:
            self.crawl_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "url": self.url,
            "publisher": self.publisher,
            "crawl_date": self.crawl_date
        }


@dataclass
class Location:
    """位置信息"""
    address: str  # 详细地址
    lat: Optional[float] = None  # 纬度（如果有官方提供）
    lng: Optional[float] = None  # 经度（如果有官方提供）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "address": self.address,
            "lat": self.lat,
            "lng": self.lng
        }


@dataclass
class AttractionSchema:
    """
    景点 Schema
    
    只包含从官方网站提取的权威信息
    不包含价格、评分等UGC字段
    """
    type: str = "attraction"
    name: str = ""  # 景点名称（必须）
    destination: str = ""  # 所属目的地（必须）
    description: str = ""  # 官方描述
    location: Optional[Location] = None  # 位置信息
    opening_hours: str = ""  # 开放时间
    recommended_duration: str = ""  # 官方推荐游览时长
    best_season: List[str] = field(default_factory=list)  # 最佳游览季节
    ticket_info: str = ""  # 门票信息（官方信息，不含价格）
    official_tips: List[str] = field(default_factory=list)  # 官方提示/注意事项
    source: Optional[Source] = None  # 数据来源（必须）
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        校验数据完整性
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 必填字段
        if not self.name:
            errors.append("景点名称不能为空")
        if not self.destination:
            errors.append("目的地不能为空")
        if not self.source:
            errors.append("数据来源不能为空")
        elif not self.source.url:
            errors.append("来源URL不能为空")
        elif not self.source.publisher:
            errors.append("发布机构不能为空")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON字典"""
        data = {
            "type": self.type,
            "name": self.name,
            "destination": self.destination,
            "description": self.description,
            "location": self.location.to_dict() if self.location else None,
            "opening_hours": self.opening_hours,
            "recommended_duration": self.recommended_duration,
            "best_season": self.best_season,
            "ticket_info": self.ticket_info,
            "official_tips": self.official_tips,
            "source": self.source.to_dict() if self.source else None
        }
        return data


@dataclass
class AccommodationSchema:
    """
    住宿 Schema
    
    只包含从官方网站提取的权威信息
    不包含价格、评分等UGC字段
    """
    type: str = "accommodation"
    name: str = ""  # 住宿名称（必须）
    destination: str = ""  # 所属目的地（必须）
    category: str = ""  # 住宿类型（酒店、民宿、旅馆等）
    location: Optional[Location] = None  # 位置信息
    room_types: List[str] = field(default_factory=list)  # 房型列表
    check_in_out: str = ""  # 入住/退房时间
    transport_access: str = ""  # 交通方式（官方描述）
    official_description: str = ""  # 官方描述
    source: Optional[Source] = None  # 数据来源（必须）
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        校验数据完整性
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 必填字段
        if not self.name:
            errors.append("住宿名称不能为空")
        if not self.destination:
            errors.append("目的地不能为空")
        if not self.source:
            errors.append("数据来源不能为空")
        elif not self.source.url:
            errors.append("来源URL不能为空")
        elif not self.source.publisher:
            errors.append("发布机构不能为空")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON字典"""
        data = {
            "type": self.type,
            "name": self.name,
            "destination": self.destination,
            "category": self.category,
            "location": self.location.to_dict() if self.location else None,
            "room_types": self.room_types,
            "check_in_out": self.check_in_out,
            "transport_access": self.transport_access,
            "official_description": self.official_description,
            "source": self.source.to_dict() if self.source else None
        }
        return data


@dataclass
class RestaurantSchema:
    """
    餐饮 Schema
    
    只包含从官方网站提取的权威信息
    不包含价格、评分等UGC字段
    """
    type: str = "restaurant"
    name: str = ""  # 餐厅名称（必须）
    destination: str = ""  # 所属目的地（必须）
    category: str = ""  # 餐厅类型（日料、法餐、中餐等）
    cuisine: str = ""  # 菜系特色
    location: Optional[Location] = None  # 位置信息
    opening_hours: str = ""  # 营业时间
    special_dishes: List[str] = field(default_factory=list)  # 特色菜品（官方推荐）
    reservation_info: str = ""  # 预约信息
    official_description: str = ""  # 官方描述
    source: Optional[Source] = None  # 数据来源（必须）
    
    def validate(self) -> tuple[bool, List[str]]:
        """校验数据完整性"""
        errors = []
        
        if not self.name:
            errors.append("餐厅名称不能为空")
        if not self.destination:
            errors.append("目的地不能为空")
        if not self.source:
            errors.append("数据来源不能为空")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON字典"""
        data = {
            "type": self.type,
            "name": self.name,
            "destination": self.destination,
            "category": self.category,
            "cuisine": self.cuisine,
            "location": self.location.to_dict() if self.location else None,
            "opening_hours": self.opening_hours,
            "special_dishes": self.special_dishes,
            "reservation_info": self.reservation_info,
            "official_description": self.official_description,
            "source": self.source.to_dict() if self.source else None
        }
        return data


@dataclass
class TransportSchema:
    """
    交通 Schema
    
    只包含从官方网站提取的权威信息
    """
    type: str = "transport"
    name: str = ""  # 交通方式名称（必须）
    destination: str = ""  # 所属目的地（必须）
    transport_type: str = ""  # 交通类型（地铁、公交、火车、机场快线等）
    route_info: str = ""  # 路线信息
    schedule: str = ""  # 班次/运营时间
    fare_info: str = ""  # 票价信息（官方信息，不含具体价格）
    access_info: str = ""  # 接驳信息
    official_description: str = ""  # 官方描述
    source: Optional[Source] = None  # 数据来源（必须）
    
    def validate(self) -> tuple[bool, List[str]]:
        """校验数据完整性"""
        errors = []
        
        if not self.name:
            errors.append("交通方式名称不能为空")
        if not self.destination:
            errors.append("目的地不能为空")
        if not self.source:
            errors.append("数据来源不能为空")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON字典"""
        data = {
            "type": self.type,
            "name": self.name,
            "destination": self.destination,
            "transport_type": self.transport_type,
            "route_info": self.route_info,
            "schedule": self.schedule,
            "fare_info": self.fare_info,
            "access_info": self.access_info,
            "official_description": self.official_description,
            "source": self.source.to_dict() if self.source else None
        }
        return data


@dataclass
class ActivitySchema:
    """
    活动 Schema
    
    只包含从官方网站提取的权威信息
    """
    type: str = "activity"
    name: str = ""  # 活动名称（必须）
    destination: str = ""  # 所属目的地（必须）
    category: str = ""  # 活动类型（节日、展览、演出等）
    date_range: str = ""  # 活动日期范围
    location: Optional[Location] = None  # 位置信息
    official_description: str = ""  # 官方描述
    official_tips: List[str] = field(default_factory=list)  # 官方提示
    source: Optional[Source] = None  # 数据来源（必须）
    
    def validate(self) -> tuple[bool, List[str]]:
        """校验数据完整性"""
        errors = []
        
        if not self.name:
            errors.append("活动名称不能为空")
        if not self.destination:
            errors.append("目的地不能为空")
        if not self.source:
            errors.append("数据来源不能为空")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为JSON字典"""
        data = {
            "type": self.type,
            "name": self.name,
            "destination": self.destination,
            "category": self.category,
            "date_range": self.date_range,
            "location": self.location.to_dict() if self.location else None,
            "official_description": self.official_description,
            "official_tips": self.official_tips,
            "source": self.source.to_dict() if self.source else None
        }
        return data


def get_schema_by_type(schema_type: str) -> Any:
    """
    根据类型获取对应的Schema类
    
    Args:
        schema_type: Schema类型（attraction/accommodation/restaurant/transport/activity）
    
    Returns:
        对应的Schema类
    """
    schema_map = {
        "attraction": AttractionSchema,
        "accommodation": AccommodationSchema,
        "restaurant": RestaurantSchema,
        "transport": TransportSchema,
        "activity": ActivitySchema
    }
    
    return schema_map.get(schema_type.lower())
