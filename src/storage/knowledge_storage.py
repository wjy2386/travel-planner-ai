"""
知识库存储模块

职责：
- 存储结构化数据到数据库
- 建立索引
- 支持查询和更新
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, JSON, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os


Base = declarative_base()


class KnowledgeRecord(Base):
    """知识库记录表"""
    __tablename__ = 'knowledge_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), unique=True, nullable=False, index=True)  # 文档唯一ID
    schema_type = Column(String(50), nullable=False, index=True)  # Schema类型
    name = Column(String(200), nullable=False, index=True)  # 名称
    destination = Column(String(100), nullable=False, index=True)  # 目的地
    data = Column(JSON, nullable=False)  # 结构化数据（JSON类型，兼容SQLite和PostgreSQL）
    content_text = Column(Text, nullable=True)  # 用于向量检索的文本内容
    source_url = Column(String(500), nullable=False)  # 来源URL
    source_publisher = Column(String(200), nullable=False)  # 发布机构
    crawl_date = Column(DateTime, nullable=False)  # 抓取时间
    is_valid = Column(Boolean, default=True, nullable=False)  # 是否有效
    needs_review = Column(Boolean, default=False, index=True)  # 是否需要审核
    review_errors = Column(JSON, nullable=True)  # 审核错误信息
    version = Column(Integer, default=1, nullable=False)  # 版本号
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # 更新时间
    
    # 创建索引
    __table_args__ = (
        Index('idx_destination_type', 'destination', 'schema_type'),
        Index('idx_name_destination', 'name', 'destination'),
    )


class KnowledgeStorage:
    """知识库存储管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            database_url: 数据库连接URL，如果为None则从环境变量读取
        """
        if not database_url:
            # 从环境变量或配置文件读取数据库URL
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://postgres:postgres@localhost:5432/travel_knowledge'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(self.engine)
    
    def _generate_doc_id(self, data: Dict[str, Any]) -> str:
        """
        生成文档唯一ID
        
        使用URL、名称、目的地等关键信息生成唯一ID
        
        Args:
            data: 数据字典
        
        Returns:
            文档ID
        """
        key_parts = [
            data.get('source', {}).get('url', ''),
            data.get('name', ''),
            data.get('destination', ''),
            data.get('type', '')
        ]
        
        key_string = '|'.join(key_parts)
        doc_id = hashlib.sha256(key_string.encode('utf-8')).hexdigest()[:64]
        
        return doc_id
    
    def save(self, data: Dict[str, Any], needs_review: bool = False, errors: List[str] = None) -> Dict[str, Any]:
        """
        保存知识数据
        
        Args:
            data: 待保存的数据字典
            needs_review: 是否需要人工审核
            errors: 错误信息列表
        
        Returns:
            保存结果，包含doc_id等信息
        """
        session = self.SessionLocal()
        try:
            # 生成文档ID
            doc_id = self._generate_doc_id(data)
            
            # 检查是否已存在
            existing = session.query(KnowledgeRecord).filter_by(doc_id=doc_id).first()
            
            if existing:
                # 更新现有记录
                existing.data = data
                existing.content_text = self._extract_content_text(data)
                existing.updated_at = datetime.utcnow()
                existing.version += 1
                existing.needs_review = needs_review
                existing.review_errors = errors if errors else None
                
                if not needs_review:
                    existing.is_valid = True
                
                session.commit()
                
                return {
                    "status": "updated",
                    "doc_id": doc_id,
                    "version": existing.version,
                    "action": "updated"
                }
            else:
                # 创建新记录
                record = KnowledgeRecord(
                    doc_id=doc_id,
                    schema_type=data.get('type'),
                    name=data.get('name'),
                    destination=data.get('destination'),
                    data=data,
                    content_text=self._extract_content_text(data),
                    source_url=data.get('source', {}).get('url'),
                    source_publisher=data.get('source', {}).get('publisher'),
                    crawl_date=datetime.fromisoformat(data.get('source', {}).get('crawl_date', datetime.utcnow().isoformat())),
                    is_valid=not needs_review,
                    needs_review=needs_review,
                    review_errors=errors if errors else None,
                    version=1
                )
                
                session.add(record)
                session.commit()
                
                return {
                    "status": "created",
                    "doc_id": doc_id,
                    "version": 1,
                    "action": "created"
                }
        
        except Exception as e:
            session.rollback()
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            session.close()
    
    def _extract_content_text(self, data: Dict[str, Any]) -> str:
        """
        提取文本内容用于向量检索
        
        Args:
            data: 数据字典
        
        Returns:
            文本内容
        """
        text_parts = []
        
        # 添加基本信息
        text_parts.append(f"名称: {data.get('name', '')}")
        text_parts.append(f"目的地: {data.get('destination', '')}")
        text_parts.append(f"类型: {data.get('type', '')}")
        
        # 添加描述
        if data.get('description'):
            text_parts.append(f"描述: {data['description']}")
        if data.get('official_description'):
            text_parts.append(f"官方描述: {data['official_description']}")
        
        # 添加位置信息
        if data.get('location') and data['location'].get('address'):
            text_parts.append(f"地址: {data['location']['address']}")
        
        # 添加提示信息
        if data.get('official_tips'):
            text_parts.append(f"提示: {'; '.join(data['official_tips'])}")
        
        # 添加特色信息（根据类型）
        if data.get('type') == 'restaurant' and data.get('special_dishes'):
            text_parts.append(f"特色菜品: {', '.join(data['special_dishes'])}")
        
        if data.get('type') == 'accommodation' and data.get('room_types'):
            text_parts.append(f"房型: {', '.join(data['room_types'])}")
        
        if data.get('type') == 'attraction' and data.get('best_season'):
            text_parts.append(f"最佳季节: {', '.join(data['best_season'])}")
        
        return '\n'.join(text_parts)
    
    def query_by_destination(self, destination: str, schema_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        按目的地查询
        
        Args:
            destination: 目的地名称
            schema_type: 可选，Schema类型过滤
        
        Returns:
            查询结果列表
        """
        session = self.SessionLocal()
        try:
            query = session.query(KnowledgeRecord).filter(
                KnowledgeRecord.destination == destination,
                KnowledgeRecord.is_valid == True
            )
            
            if schema_type:
                query = query.filter(KnowledgeRecord.schema_type == schema_type)
            
            records = query.all()
            
            return [record.data for record in records]
        
        finally:
            session.close()
    
    def query_by_name(self, name: str, destination: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        按名称查询
        
        Args:
            name: 名称
            destination: 可选，目的地名称
        
        Returns:
            查询结果
        """
        session = self.SessionLocal()
        try:
            query = session.query(KnowledgeRecord).filter(
                KnowledgeRecord.name == name,
                KnowledgeRecord.is_valid == True
            )
            
            if destination:
                query = query.filter(KnowledgeRecord.destination == destination)
            
            record = query.first()
            
            return record.data if record else None
        
        finally:
            session.close()
    
    def get_pending_review(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取待审核记录
        
        Args:
            limit: 返回数量限制
        
        Returns:
            待审核记录列表
        """
        session = self.SessionLocal()
        try:
            records = session.query(KnowledgeRecord).filter(
                KnowledgeRecord.needs_review == True
            ).limit(limit).all()
            
            return [
                {
                    "doc_id": record.doc_id,
                    "schema_type": record.schema_type,
                    "name": record.name,
                    "destination": record.destination,
                    "data": record.data,
                    "review_errors": record.review_errors
                }
                for record in records
            ]
        
        finally:
            session.close()
    
    def approve_review(self, doc_id: str) -> bool:
        """
        审核通过
        
        Args:
            doc_id: 文档ID
        
        Returns:
            是否成功
        """
        session = self.SessionLocal()
        try:
            record = session.query(KnowledgeRecord).filter_by(doc_id=doc_id).first()
            if record:
                record.needs_review = False
                record.is_valid = True
                record.review_errors = None
                session.commit()
                return True
            return False
        
        finally:
            session.close()
    
    def reject_review(self, doc_id: str, reason: str) -> bool:
        """
        审核拒绝
        
        Args:
            doc_id: 文档ID
            reason: 拒绝原因
        
        Returns:
            是否成功
        """
        session = self.SessionLocal()
        try:
            record = session.query(KnowledgeRecord).filter_by(doc_id=doc_id).first()
            if record:
                record.is_valid = False
                record.needs_review = False
                record.review_errors = {"rejection_reason": reason}
                session.commit()
                return True
            return False
        
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        session = self.SessionLocal()
        try:
            total = session.query(KnowledgeRecord).count()
            valid = session.query(KnowledgeRecord).filter(KnowledgeRecord.is_valid == True).count()
            pending = session.query(KnowledgeRecord).filter(KnowledgeRecord.needs_review == True).count()
            
            # 按类型统计
            type_stats = {}
            for schema_type in ['attraction', 'accommodation', 'restaurant', 'transport', 'activity']:
                count = session.query(KnowledgeRecord).filter(
                    KnowledgeRecord.schema_type == schema_type,
                    KnowledgeRecord.is_valid == True
                ).count()
                type_stats[schema_type] = count
            
            return {
                "total": total,
                "valid": valid,
                "pending_review": pending,
                "by_type": type_stats
            }
        
        finally:
            session.close()
