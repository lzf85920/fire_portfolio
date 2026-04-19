"""Data models for portfolio tracking"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AssetType(Enum):
    """Asset type enumeration"""
    STOCK_US = "Stock - US"
    STOCK_TW = "Stock - Taiwan"
    ETF_US = "ETF - US"
    ETF_TW = "ETF - Taiwan"
    CASH = "Cash"
    OTHER = "Other"

@dataclass
class Portfolio:
    """Portfolio model"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

@dataclass
class Holding:
    """Individual holding/position model"""
    id: int
    portfolio_id: int
    symbol: str
    asset_type: AssetType
    quantity: float
    purchase_price: float
    purchase_date: datetime
    current_price: float
    price_updated_at: datetime
    notes: Optional[str] = None
    market: str = "US"  # "US" or "TW"
    currency: str = "USD"  # "USD" or "NTD"

@dataclass
class PriceHistory:
    """Historical price data"""
    id: int
    symbol: str
    price: float
    date: datetime
    market: str  # "US" or "TW"

@dataclass
class PerformanceMetrics:
    """Portfolio performance metrics"""
    total_value: float
    total_cost: float
    total_realized_pl: float
    total_unrealized_pl: float
    total_pl: float
    return_percentage: float
    realized_return_percentage: float
    unrealized_return_percentage: float
    
@dataclass
class HoldingDetail:
    """Holding with calculated performance data"""
    symbol: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_price: float
    cost_basis: float
    current_value: float
    unrealized_pl: float
    unrealized_return_pct: float
    market: str
    currency: str  # "USD" or "NTD"
    last_updated: datetime
