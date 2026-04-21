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
    OPTION = "Option"
    OTHER = "Other"

class OptionType(Enum):
    """Option type enumeration"""
    CALL = "CALL"
    PUT = "PUT"

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
class OptionHolding:
    """Individual option contract holding"""
    id: int
    portfolio_id: int
    symbol: str  # Underlying stock symbol (e.g., TSLA)
    option_type: str  # CALL or PUT
    strike: float  # Strike price
    expiration: datetime  # Expiration date
    quantity: int  # Number of contracts (1 contract = 100 shares)
    premium: float  # Price paid per share (so actual cost = quantity * 100 * premium)
    purchase_date: datetime
    current_price: float  # Current option price per share
    price_updated_at: datetime
    status: str = "OPEN"  # OPEN, CLOSED, EXPIRED
    notes: Optional[str] = None
    market: str = "US"  # "US" or "TW"
    currency: str = "USD"

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

@dataclass
class OptionDetail:
    """Option contract with calculated performance data"""
    symbol: str  # Underlying stock
    option_type: str  # CALL or PUT
    strike: float
    expiration: datetime
    quantity: int  # Number of contracts
    premium: float  # Price paid per share
    current_price: float  # Current option price per share
    cost_basis: float  # quantity * 100 * premium
    current_value: float  # quantity * 100 * current_price
    unrealized_pl: float  # current_value - cost_basis
    unrealized_return_pct: float  # (unrealized_pl / cost_basis) * 100 if cost_basis > 0
    status: str  # OPEN, CLOSED, EXPIRED
    market: str
    currency: str
    last_updated: datetime
