from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class DamageLog(Base):
    __tablename__ = "damage_logs"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    damage_type = Column(String, nullable=False)
    severity_level = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)