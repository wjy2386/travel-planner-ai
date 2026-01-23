"""
知识库校验模块

职责：
- 自动校验采集的数据
- 必填字段检查
- 数据一致性验证
- 标记需要人工审核的数据
"""

from typing import Dict, Any, List, Tuple
from storage.knowledge_schemas import (
    AttractionSchema, AccommodationSchema, RestaurantSchema,
    TransportSchema, ActivitySchema, get_schema_by_type
)


class KnowledgeValidator:
    """知识数据校验器"""
    
    def __init__(self):
        self.required_fields = {
            "attraction": ["name", "destination", "source"],
            "accommodation": ["name", "destination", "source"],
            "restaurant": ["name", "destination", "source"],
            "transport": ["name", "destination", "source"],
            "activity": ["name", "destination", "source"]
        }
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str], bool]:
        """
        校验数据
        
        Args:
            data: 待校验的数据字典
        
        Returns:
            (是否通过校验, 错误信息列表, 是否需要人工审核)
        """
        errors = []
        needs_review = False
        
        # 检查数据类型
        schema_type = data.get("type")
        if not schema_type:
            errors.append("缺少type字段")
            return False, errors, True
        
        # 检查必填字段
        required = self.required_fields.get(schema_type, [])
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"必填字段 '{field}' 缺失或为空")
        
        # 特殊校验：source字段
        if "source" in data and data["source"]:
            source = data["source"]
            if not source.get("url"):
                errors.append("source.url 不能为空")
            if not source.get("publisher"):
                errors.append("source.publisher 不能为空")
        else:
            errors.append("source 字段缺失")
        
        # 数据一致性校验
        if "name" in data and data["name"]:
            # 检查名称长度
            if len(data["name"]) < 2:
                errors.append(f"名称 '{data['name']}' 过短")
            if len(data["name"]) > 200:
                errors.append(f"名称 '{data['name']}' 过长")
        
        # 检查destination
        if "destination" in data and data["destination"]:
            if len(data["destination"]) < 2:
                errors.append(f"目的地 '{data['destination']}' 无效")
        
        # 检查location
        if "location" in data and data["location"]:
            location = data["location"]
            if not location.get("address"):
                errors.append("location.address 缺失")
            else:
                if len(location["address"]) > 500:
                    errors.append("地址过长")
            
            # 检查坐标范围
            if location.get("lat"):
                lat = location["lat"]
                if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
                    errors.append(f"纬度 {lat} 超出有效范围")
                    needs_review = True
            
            if location.get("lng"):
                lng = location["lng"]
                if not isinstance(lng, (int, float)) or not (-180 <= lng <= 180):
                    errors.append(f"经度 {lng} 超出有效范围")
                    needs_review = True
        
        # 根据类型进行特殊校验
        if schema_type == "attraction":
            needs_review = needs_review or self._validate_attraction(data, errors)
        elif schema_type == "accommodation":
            needs_review = needs_review or self._validate_accommodation(data, errors)
        elif schema_type == "restaurant":
            needs_review = needs_review or self._validate_restaurant(data, errors)
        elif schema_type == "transport":
            needs_review = needs_review or self._validate_transport(data, errors)
        elif schema_type == "activity":
            needs_review = needs_review or self._validate_activity(data, errors)
        
        # 如果有错误，标记需要审核
        if errors:
            needs_review = True
        
        return len(errors) == 0, errors, needs_review
    
    def _validate_attraction(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """校验景点数据"""
        needs_review = False
        
        # 检查opening_hours格式
        if data.get("opening_hours"):
            hours = data["opening_hours"]
            if len(hours) > 100:
                errors.append("开放时间描述过长")
                needs_review = True
        
        # 检查best_season
        if data.get("best_season"):
            seasons = data["best_season"]
            if not isinstance(seasons, list):
                errors.append("best_season 应该是列表")
                needs_review = True
            elif len(seasons) > 10:
                errors.append("best_season 元素过多")
                needs_review = True
        
        return needs_review
    
    def _validate_accommodation(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """校验住宿数据"""
        needs_review = False
        
        # 检查room_types
        if data.get("room_types"):
            rooms = data["room_types"]
            if not isinstance(rooms, list):
                errors.append("room_types 应该是列表")
                needs_review = True
            elif len(rooms) > 20:
                errors.append("room_types 元素过多")
                needs_review = True
        
        return needs_review
    
    def _validate_restaurant(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """校验餐厅数据"""
        needs_review = False
        
        # 检查special_dishes
        if data.get("special_dishes"):
            dishes = data["special_dishes"]
            if not isinstance(dishes, list):
                errors.append("special_dishes 应该是列表")
                needs_review = True
            elif len(dishes) > 20:
                errors.append("special_dishes 元素过多")
                needs_review = True
        
        return needs_review
    
    def _validate_transport(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """校验交通数据"""
        needs_review = False
        # 交通数据校验逻辑
        return needs_review
    
    def _validate_activity(self, data: Dict[str, Any], errors: List[str]) -> bool:
        """校验活动数据"""
        needs_review = False
        
        # 检查date_range
        if data.get("date_range"):
            date_range = data["date_range"]
            if len(date_range) > 100:
                errors.append("日期范围描述过长")
                needs_review = True
        
        return needs_review


def validate_data(data: Dict[str, Any]) -> Tuple[bool, List[str], bool]:
    """
    便捷函数：校验数据
    
    Args:
        data: 待校验的数据字典
    
    Returns:
        (是否通过校验, 错误信息列表, 是否需要人工审核)
    """
    validator = KnowledgeValidator()
    return validator.validate(data)
