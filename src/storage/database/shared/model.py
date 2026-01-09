from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime


class Base(DeclarativeBase):
    pass


class Traveler(Base):
    """旅行者基本信息表"""
    __tablename__ = "travelers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="旅行者ID")
    user_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="用户唯一标识")
    name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="用户姓名")
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="用户邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, comment="用户手机号")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否激活")
    tier: Mapped[str] = mapped_column(String(32), nullable=False, default="standard", comment="用户等级：standard(标准)/vip(高级)/platinum(白金)")
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="用户偏好标签，例如：['历史文化', '美食', '动漫']")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    itineraries: Mapped[list["Itinerary"]] = relationship("Itinerary", back_populates="traveler", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("ix_travelers_user_id", "user_id"),
        Index("ix_travelers_tier", "tier"),
    )


class Itinerary(Base):
    """历史行程表"""
    __tablename__ = "itineraries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="行程ID")
    traveler_id: Mapped[int] = mapped_column(ForeignKey("travelers.id", ondelete="CASCADE"), nullable=False, comment="旅行者ID")
    departure: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="出发地")
    destination: Mapped[str] = mapped_column(String(128), nullable=False, comment="目的地")
    start_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="开始日期")
    end_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="结束日期")
    days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="天数")
    travelers_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="人数")
    travel_tier: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, comment="旅行层级：大众/小资/深度/高端定制")
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="本次行程偏好")
    itinerary_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="完整行程JSON数据")
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="用户反馈")
    satisfaction_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="满意度评分(0-5)")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed", comment="状态：draft(草稿)/completed(已完成)/cancelled(已取消)")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 关系
    traveler: Mapped["Traveler"] = relationship("Traveler", back_populates="itineraries")
    
    # 索引
    __table_args__ = (
        Index("ix_itineraries_traveler_id", "traveler_id"),
        Index("ix_itineraries_destination", "destination"),
        Index("ix_itineraries_start_date", "start_date"),
        Index("ix_itineraries_status", "status"),
    )


class PreferenceTag(Base):
    """偏好标签表（用于统计分析）"""
    __tablename__ = "preference_tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="标签ID")
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="标签名称，例如：历史文化、美食、动漫")
    category: Mapped[str] = mapped_column(String(32), nullable=False, comment="标签分类：interest(兴趣)/style(风格)/budget(预算)")
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="使用次数")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index("ix_preference_tags_name", "name"),
        Index("ix_preference_tags_category", "category"),
    )
