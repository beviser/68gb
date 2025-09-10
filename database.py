"""
Database models and initialization
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GameResult(Base):
    """Game result model"""
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(String(50), nullable=False, index=True)  # tai_xiu, ban_do
    session_id = Column(String(100), nullable=False, index=True)
    result_md5 = Column(String(32), nullable=False)
    result_data = Column(Text)  # JSON string of full result
    timestamp = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    
class GameSession(Base):
    """Game session model"""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    game_type = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default="active")  # active, completed, cancelled
    total_results = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Notification(Base):
    """Notification log model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String(50), nullable=False)  # telegram, email, webhook
    recipient = Column(String(255))
    subject = Column(String(255))
    message = Column(Text)
    status = Column(String(20), default="pending")  # pending, sent, failed
    game_result_id = Column(Integer)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    error_message = Column(Text)

class APILog(Base):
    """API access log model"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    response_status = Column(Integer)
    response_time = Column(Float)  # in seconds
    timestamp = Column(DateTime, default=func.now(), index=True)

async def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utility functions
async def save_game_result(game_type: str, session_id: str, result_md5: str, result_data: str):
    """Save game result to database"""
    db = SessionLocal()
    try:
        result = GameResult(
            game_type=game_type,
            session_id=session_id,
            result_md5=result_md5,
            result_data=result_data
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    finally:
        db.close()

async def get_latest_results(game_type: str = None, limit: int = 10):
    """Get latest game results"""
    db = SessionLocal()
    try:
        query = db.query(GameResult)
        if game_type:
            query = query.filter(GameResult.game_type == game_type)
        results = query.order_by(GameResult.timestamp.desc()).limit(limit).all()
        return results
    finally:
        db.close()

async def log_api_request(endpoint: str, method: str, ip_address: str, user_agent: str, 
                         response_status: int, response_time: float):
    """Log API request"""
    db = SessionLocal()
    try:
        log_entry = APILog(
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=response_status,
            response_time=response_time
        )
        db.add(log_entry)
        db.commit()
    finally:
        db.close()
