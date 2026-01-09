"""
旅行者数据管理
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import datetime

from storage.database.shared.model import Traveler, Itinerary


# --- Pydantic Models ---
class TravelerCreate(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")
    name: Optional[str] = Field(None, description="用户姓名")
    email: Optional[str] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, description="用户手机号")
    tier: str = Field("standard", description="用户等级")
    preferences: Optional[List[str]] = Field(None, description="用户偏好标签")


class TravelerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: Optional[str] = None
    preferences: Optional[List[str]] = None


class ItineraryCreate(BaseModel):
    traveler_id: int = Field(..., description="旅行者ID")
    departure: Optional[str] = None
    destination: str = Field(..., description="目的地")
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    days: Optional[int] = None
    travelers_count: Optional[int] = None
    travel_tier: Optional[str] = None
    preferences: Optional[List[str]] = None
    itinerary_json: Optional[dict] = None
    feedback: Optional[str] = None
    satisfaction_score: Optional[float] = None
    status: str = Field("completed", description="状态")


# --- Manager Class ---
class TravelerManager:
    """旅行者和行程数据管理"""

    def create_traveler(self, db: Session, traveler_in: TravelerCreate) -> Traveler:
        """创建旅行者"""
        traveler_data = traveler_in.model_dump()
        db_traveler = Traveler(**traveler_data)
        db.add(db_traveler)
        try:
            db.commit()
            db.refresh(db_traveler)
            return db_traveler
        except Exception as e:
            db.rollback()
            raise e

    def get_traveler_by_user_id(self, db: Session, user_id: str) -> Optional[Traveler]:
        """根据 user_id 查询旅行者"""
        return db.query(Traveler).filter(Traveler.user_id == user_id).first()

    def get_or_create_traveler(self, db: Session, user_id: str, **kwargs) -> Traveler:
        """获取或创建旅行者（如果不存在）"""
        traveler = self.get_traveler_by_user_id(db, user_id)
        if not traveler:
            traveler_data = {"user_id": user_id, **kwargs}
            traveler = Traveler(**traveler_data)
            db.add(traveler)
            try:
                db.commit()
                db.refresh(traveler)
            except Exception as e:
                db.rollback()
                raise e
        return traveler

    def update_traveler(self, db: Session, user_id: str, traveler_in: TravelerUpdate) -> Optional[Traveler]:
        """更新旅行者信息"""
        db_traveler = self.get_traveler_by_user_id(db, user_id)
        if not db_traveler:
            return None
        update_data = traveler_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_traveler, field):
                setattr(db_traveler, field, value)
        db.add(db_traveler)
        try:
            db.commit()
            db.refresh(db_traveler)
            return db_traveler
        except Exception as e:
            db.rollback()
            raise e

    def create_itinerary(self, db: Session, itinerary_in: ItineraryCreate) -> Itinerary:
        """创建行程"""
        itinerary_data = itinerary_in.model_dump()
        db_itinerary = Itinerary(**itinerary_data)
        db.add(db_itinerary)
        try:
            db.commit()
            db.refresh(db_itinerary)
            return db_itinerary
        except Exception as e:
            db.rollback()
            raise e

    def get_traveler_itineraries(
        self,
        db: Session,
        user_id: str,
        destination: Optional[str] = None,
        limit: int = 10
    ) -> List[Itinerary]:
        """获取旅行者的历史行程"""
        traveler = self.get_traveler_by_user_id(db, user_id)
        if not traveler:
            return []
        
        query = db.query(Itinerary).filter(Itinerary.traveler_id == traveler.id)
        if destination:
            query = query.filter(Itinerary.destination == destination)
        
        return query.order_by(Itinerary.created_at.desc()).limit(limit).all()

    def get_traveler_preferences(self, db: Session, user_id: str) -> Optional[dict]:
        """获取旅行者画像（包括基本信息和偏好）"""
        traveler = self.get_traveler_by_user_id(db, user_id)
        if not traveler:
            return None
        
        # 获取历史行程
        itineraries = self.get_traveler_itineraries(db, user_id)
        
        # 统计偏好
        all_preferences = (traveler.preferences or []).copy()
        for itinerary in itineraries:
            if itinerary.preferences:
                all_preferences.extend(itinerary.preferences)
        
        # 统计去过的地方
        destinations = list(set([it.destination for it in itineraries]))
        
        return {
            "user_id": traveler.user_id,
            "name": traveler.name,
            "tier": traveler.tier,
            "preferences": list(set(all_preferences)),  # 去重
            "visited_destinations": destinations,
            "itinerary_count": len(itineraries)
        }
