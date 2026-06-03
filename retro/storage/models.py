from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AttackEventModel(Base):
    __tablename__ = "attack_events"
    id = Column(String(12), primary_key=True)
    sensor = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)
    source_ip = Column(String(45), nullable=False)
    source_port = Column(Integer, nullable=True)
    dest_port = Column(Integer, nullable=True)
    protocol = Column(String(16), nullable=True)
    username = Column(String(128), nullable=True)
    password = Column(String(256), nullable=True)
    user_agent = Column(String(512), nullable=True)
    method = Column(String(16), nullable=True)
    path = Column(String(1024), nullable=True)
    payload = Column(Text, nullable=True)
    raw_data = Column(JSON, default=dict)
    threat_score = Column(Float, default=0.0)
    processed = Column(Boolean, default=False)
    investigation_id = Column(String(12), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AttackerModel(Base):
    __tablename__ = "attackers"
    ip = Column(String(45), primary_key=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_events = Column(Integer, default=1)
    event_types = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    osint_data = Column(JSON, default=dict)
    threat_score = Column(Float, default=0.0)
    blocked = Column(Boolean, default=False)
    reported = Column(Boolean, default=False)
    country = Column(String(4), nullable=True)
    isp = Column(String(256), nullable=True)


class CountermeasureModel(Base):
    __tablename__ = "countermeasures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(256), nullable=False)
    target_type = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    result = Column(JSON, default=dict)
    executed_at = Column(DateTime, default=datetime.utcnow)


class AlertModel(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(16), default="info")
    source_ip = Column(String(45), nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
