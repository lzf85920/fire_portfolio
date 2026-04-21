"""Database schema definition"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import config

Base = declarative_base()

class PortfolioModel(Base):
    """Portfolio table"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    total_realized_pl = Column(Float, default=0.0)  # 累計已實現損益
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    holdings = relationship("HoldingModel", back_populates="portfolio", cascade="all, delete-orphan")
    options = relationship("OptionModel", back_populates="portfolio", cascade="all, delete-orphan")

class HoldingModel(Base):
    """Holdings (positions) table"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    asset_type = Column(String(50), nullable=False)  # Stock - US, ETF - TW, etc.
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    current_price = Column(Float, nullable=False)
    price_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String(500))
    market = Column(String(10), default="US")  # US or TW
    currency = Column(String(5), default="USD")  # USD or NTD
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("PortfolioModel", back_populates="holdings")

class PriceHistoryModel(Base):
    """Price history table for tracking performance"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    market = Column(String(10), nullable=False)  # US or TW
    created_at = Column(DateTime, default=datetime.utcnow)

class OptionModel(Base):
    """Option contracts table"""
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)  # Underlying stock (e.g., TSLA)
    option_type = Column(String(10), nullable=False)  # CALL or PUT
    strike = Column(Float, nullable=False)  # Strike price
    expiration = Column(DateTime, nullable=False, index=True)  # Expiration date
    quantity = Column(Integer, nullable=False)  # Number of contracts (1 contract = 100 shares)
    premium = Column(Float, nullable=False)  # Price paid per share
    purchase_date = Column(DateTime, nullable=False)
    current_price = Column(Float, nullable=False)  # Current option price per share
    price_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, EXPIRED
    notes = Column(String(500))
    market = Column(String(10), default="US")  # US or TW
    currency = Column(String(5), default="USD")  # USD or NTD
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("PortfolioModel", back_populates="options")

class PerformanceSnapshotModel(Base):
    """Daily portfolio performance snapshot"""
    __tablename__ = "performance_snapshots"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    total_unrealized_pl = Column(Float, nullable=False)
    total_realized_pl = Column(Float, nullable=False)
    total_pl = Column(Float, nullable=False)
    total_pl_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TransactionModel(Base):
    """Transaction history for tracking buys/sells"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # "BUY" or "SELL"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    realized_pl = Column(Float, default=0.0)  # For sells only
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

def init_database():
    """Initialize database with schema"""
    engine = create_engine(config.DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine
