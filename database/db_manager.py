"""Database manager for CRUD operations"""
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
import config
from database.schema import (
    Base, PortfolioModel, HoldingModel, PriceHistoryModel,
    PerformanceSnapshotModel, TransactionModel, OptionModel, init_database
)

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or config.DATABASE_URL
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        init_database()
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    # ============ Portfolio Operations ============
    
    def create_portfolio(self, name: str, description: str = None) -> PortfolioModel:
        """Create a new portfolio"""
        session = self.get_session()
        try:
            portfolio = PortfolioModel(name=name, description=description)
            session.add(portfolio)
            session.commit()
            return portfolio
        finally:
            session.close()
    
    def get_portfolio(self, portfolio_id: int) -> Optional[PortfolioModel]:
        """Get portfolio by ID"""
        session = self.get_session()
        try:
            return session.query(PortfolioModel).filter(
                PortfolioModel.id == portfolio_id
            ).first()
        finally:
            session.close()
    
    def get_all_portfolios(self, active_only: bool = True) -> List[PortfolioModel]:
        """Get all portfolios"""
        session = self.get_session()
        try:
            query = session.query(PortfolioModel)
            if active_only:
                query = query.filter(PortfolioModel.is_active == True)
            return query.all()
        finally:
            session.close()
    
    def update_portfolio(self, portfolio_id: int, **kwargs) -> Optional[PortfolioModel]:
        """Update portfolio"""
        session = self.get_session()
        try:
            portfolio = session.query(PortfolioModel).filter(
                PortfolioModel.id == portfolio_id
            ).first()
            if portfolio:
                for key, value in kwargs.items():
                    if hasattr(portfolio, key):
                        setattr(portfolio, key, value)
                portfolio.updated_at = datetime.utcnow()
                session.commit()
            return portfolio
        finally:
            session.close()
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Soft delete portfolio by setting is_active to False"""
        session = self.get_session()
        try:
            portfolio = session.query(PortfolioModel).filter(
                PortfolioModel.id == portfolio_id
            ).first()
            if portfolio:
                portfolio.is_active = False
                portfolio.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()

    # ============ Holding Operations ============

    def add_holding(self, portfolio_id: int, symbol: str, asset_type: str,
                   quantity: float, purchase_price: float, purchase_date: datetime,
                   current_price: float, market: str = "US", currency: str = "USD", notes: str = None) -> HoldingModel:
        """Add a new holding to portfolio"""
        session = self.get_session()
        try:
            holding = HoldingModel(
                portfolio_id=portfolio_id,
                symbol=symbol,
                asset_type=asset_type,
                quantity=quantity,
                purchase_price=purchase_price,
                purchase_date=purchase_date,
                current_price=current_price,
                market=market,
                currency=currency,
                notes=notes
            )
            session.add(holding)
            session.commit()
            return holding
        finally:
            session.close()
    
    def get_holdings(self, portfolio_id: int) -> List[HoldingModel]:
        """Get all holdings for a portfolio"""
        session = self.get_session()
        try:
            return session.query(HoldingModel).filter(
                HoldingModel.portfolio_id == portfolio_id
            ).all()
        finally:
            session.close()
    
    def update_holding(self, holding_id: int, **kwargs) -> Optional[HoldingModel]:
        """Update holding"""
        session = self.get_session()
        try:
            holding = session.query(HoldingModel).filter(
                HoldingModel.id == holding_id
            ).first()
            if holding:
                for key, value in kwargs.items():
                    if hasattr(holding, key):
                        setattr(holding, key, value)
                holding.price_updated_at = datetime.utcnow()
                session.commit()
            return holding
        finally:
            session.close()
    
    def delete_holding(self, holding_id: int) -> bool:
        """Delete holding"""
        session = self.get_session()
        try:
            holding = session.query(HoldingModel).filter(
                HoldingModel.id == holding_id
            ).first()
            if holding:
                session.delete(holding)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def adjust_holding_quantity(self, holding_id: int, new_quantity: float, new_price: float = None) -> Optional[HoldingModel]:
        """Adjust holding quantity (for selling or reducing position)"""
        session = self.get_session()
        try:
            holding = session.query(HoldingModel).filter(
                HoldingModel.id == holding_id
            ).first()
            if holding:
                holding.quantity = new_quantity
                if new_price is not None:
                    holding.current_price = new_price
                session.commit()
            return holding
        finally:
            session.close()
    
    # ============ Price History Operations ============
    
    def add_price_history(self, symbol: str, price: float, date: datetime, market: str = "US"):
        """Record price history"""
        session = self.get_session()
        try:
            price_record = PriceHistoryModel(
                symbol=symbol,
                price=price,
                date=date,
                market=market
            )
            session.add(price_record)
            session.commit()
        finally:
            session.close()
    
    def get_price_history(self, symbol: str, market: str = "US", limit: int = 100):
        """Get price history for a symbol"""
        session = self.get_session()
        try:
            return session.query(PriceHistoryModel).filter(
                PriceHistoryModel.symbol == symbol,
                PriceHistoryModel.market == market
            ).order_by(desc(PriceHistoryModel.date)).limit(limit).all()
        finally:
            session.close()
    
    # ============ Performance Snapshot Operations ============
    
    def record_performance_snapshot(self, portfolio_id: int, total_value: float,
                                   total_cost: float, total_unrealized_pl: float,
                                   total_realized_pl: float, total_pl: float,
                                   total_pl_percentage: float):
        """Record daily portfolio performance"""
        session = self.get_session()
        try:
            snapshot = PerformanceSnapshotModel(
                portfolio_id=portfolio_id,
                snapshot_date=datetime.utcnow(),
                total_value=total_value,
                total_cost=total_cost,
                total_unrealized_pl=total_unrealized_pl,
                total_realized_pl=total_realized_pl,
                total_pl=total_pl,
                total_pl_percentage=total_pl_percentage
            )
            session.add(snapshot)
            session.commit()
        finally:
            session.close()
    
    def get_performance_history(self, portfolio_id: int, limit: int = 365):
        """Get performance history"""
        session = self.get_session()
        try:
            return session.query(PerformanceSnapshotModel).filter(
                PerformanceSnapshotModel.portfolio_id == portfolio_id
            ).order_by(desc(PerformanceSnapshotModel.snapshot_date)).limit(limit).all()
        finally:
            session.close()
    
    # ============ Transaction History Operations ============
    
    def record_transaction(self, portfolio_id: int, symbol: str, transaction_type: str,
                          quantity: float, price: float, transaction_date: datetime,
                          realized_pl: float = 0.0, notes: str = None):
        """Record a buy/sell transaction"""
        session = self.get_session()
        try:
            transaction = TransactionModel(
                portfolio_id=portfolio_id,
                symbol=symbol,
                transaction_type=transaction_type,  # "BUY" or "SELL"
                quantity=quantity,
                price=price,
                transaction_date=transaction_date,
                realized_pl=realized_pl,
                notes=notes
            )
            session.add(transaction)
            session.commit()
        finally:
            session.close()
    
    def get_transaction_history(self, portfolio_id: int, limit: int = 100):
        """Get transaction history"""
        session = self.get_session()
        try:
            return session.query(TransactionModel).filter(
                TransactionModel.portfolio_id == portfolio_id
            ).order_by(desc(TransactionModel.transaction_date)).limit(limit).all()
        finally:
            session.close()
    
    # ============ Option Operations ============
    
    def add_option(self, portfolio_id: int, symbol: str, option_type: str,
                  strike: float, expiration: datetime, quantity: int,
                  premium: float, current_price: float, market: str = "US",
                  currency: str = "USD", notes: str = None) -> OptionModel:
        """Add a new option contract to portfolio"""
        session = self.get_session()
        try:
            option = OptionModel(
                portfolio_id=portfolio_id,
                symbol=symbol,
                option_type=option_type.upper(),  # CALL or PUT
                strike=strike,
                expiration=expiration,
                quantity=quantity,
                premium=premium,
                purchase_date=datetime.utcnow(),
                current_price=current_price,
                market=market,
                currency=currency,
                notes=notes
            )
            session.add(option)
            session.commit()
            return option
        finally:
            session.close()
    
    def get_options(self, portfolio_id: int) -> List[OptionModel]:
        """Get all option contracts for a portfolio"""
        session = self.get_session()
        try:
            return session.query(OptionModel).filter(
                OptionModel.portfolio_id == portfolio_id
            ).all()
        finally:
            session.close()
    
    def get_option(self, option_id: int) -> Optional[OptionModel]:
        """Get a specific option contract"""
        session = self.get_session()
        try:
            return session.query(OptionModel).filter(
                OptionModel.id == option_id
            ).first()
        finally:
            session.close()
    
    def update_option(self, option_id: int, **kwargs) -> Optional[OptionModel]:
        """Update option contract"""
        session = self.get_session()
        try:
            option = session.query(OptionModel).filter(
                OptionModel.id == option_id
            ).first()
            if option:
                for key, value in kwargs.items():
                    if hasattr(option, key):
                        setattr(option, key, value)
                option.price_updated_at = datetime.utcnow()
                session.commit()
            return option
        finally:
            session.close()
    
    def delete_option(self, option_id: int) -> bool:
        """Delete option contract"""
        session = self.get_session()
        try:
            option = session.query(OptionModel).filter(
                OptionModel.id == option_id
            ).first()
            if option:
                session.delete(option)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def close_option(self, option_id: int, close_price: float) -> Optional[OptionModel]:
        """Mark option as closed and record the close price"""
        return self.update_option(option_id, status="CLOSED", current_price=close_price)
    
    def expire_option(self, option_id: int) -> Optional[OptionModel]:
        """Mark option as expired"""
        return self.update_option(option_id, status="EXPIRED", current_price=0.0)

# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create global database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
