"""Portfolio management operations"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from backend.data_fetcher import DataFetcher
from backend.calculator import PortfolioCalculator, PortfolioAnalyzer
from backend.models import HoldingDetail, PerformanceMetrics, OptionDetail, OptionHolding
from database.db_manager import DatabaseManager, get_db_manager
import logging

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Manages portfolio operations"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or get_db_manager()
    
    def refresh_prices(self, portfolio_id: int):
        """Refresh all prices for holdings in a portfolio"""
        holdings = self.db.get_holdings(portfolio_id)
        
        for holding in holdings:
            try:
                current_price = DataFetcher.get_price(holding.symbol, holding.market)
                if current_price:
                    self.db.update_holding(holding.id, current_price=current_price)
                    # Record price history
                    self.db.add_price_history(holding.symbol, current_price, datetime.utcnow(), holding.market)
                    logger.info(f"已更新 {holding.symbol}: ${current_price}")
            except Exception as e:
                logger.error(f"Error updating price for {holding.symbol}: {e}")
        
        # Also refresh option prices
        self.refresh_option_prices(portfolio_id)
    
    def refresh_option_prices(self, portfolio_id: int):
        """Refresh all option prices for a portfolio"""
        options = self.db.get_options(portfolio_id)
        
        for option in options:
            try:
                # Skip expired options
                if option.status == "EXPIRED":
                    logger.info(f"跳過已過期的選擇權 {option.symbol} {option.option_type} {option.strike} {option.expiration}")
                    continue
                
                # Get current price for the option
                expiration_str = option.expiration.strftime("%Y-%m-%d")
                current_price = DataFetcher.get_option_price(
                    option.symbol, 
                    expiration_str, 
                    option.strike, 
                    option.option_type
                )
                
                if current_price is not None:
                    self.db.update_option(option.id, current_price=current_price)
                    logger.info(f"已更新選擇權 {option.symbol} {option.option_type} {option.strike} @ {option.expiration.strftime('%Y-%m-%d')}: ${current_price}")
                else:
                    logger.warning(f"無法取得選擇權 {option.symbol} {option.option_type} {option.strike} @ {option.expiration.strftime('%Y-%m-%d')} 的價格")
            except Exception as e:
                logger.error(f"Error updating option price for {option.symbol} {option.option_type} {option.strike}: {e}")
    
    def get_portfolio_performance(self, portfolio_id: int) -> tuple[PerformanceMetrics, List[HoldingDetail], Dict]:
        """Get complete portfolio performance data"""
        holdings = self.db.get_holdings(portfolio_id)
        portfolio = self.db.get_portfolio(portfolio_id)
        
        holdings_details = []
        for holding in holdings:
            detail = PortfolioCalculator.calculate_holding_performance(
                symbol=holding.symbol,
                quantity=holding.quantity,
                purchase_price=holding.purchase_price,
                current_price=holding.current_price,
                purchase_date=holding.purchase_date,
                asset_type=holding.asset_type,
                market=holding.market,
                currency=getattr(holding, 'currency', 'USD')
            )
            holdings_details.append(detail)
        
        total_realized_pl = portfolio.total_realized_pl if portfolio else 0.0
        metrics = PortfolioCalculator.calculate_portfolio_metrics(
            holdings_details,
            total_realized_pl=total_realized_pl
        )
        distribution = PortfolioCalculator.calculate_asset_distribution(holdings_details)
        
        return metrics, holdings_details, distribution
    
    def get_portfolio_analysis(self, portfolio_id: int) -> Dict:
        """Get advanced analysis for portfolio"""
        metrics, holdings_details, distribution = self.get_portfolio_performance(portfolio_id)
        
        market_exposure = PortfolioAnalyzer.get_market_exposure(holdings_details)
        top_performers = PortfolioAnalyzer.get_top_performers(holdings_details, top_n=5)
        worst_performers = PortfolioAnalyzer.get_worst_performers(holdings_details, top_n=5)
        
        return {
            "metrics": metrics,
            "holdings": holdings_details,
            "distribution": distribution,
            "market_exposure": market_exposure,
            "top_performers": top_performers,
            "worst_performers": worst_performers
        }
    
    def add_deposit(self, portfolio_id: int, amount: float, currency: str = "USD",
                   deposit_date: datetime = None, market: str = "US", notes: str = None):
        """Add cash deposit - doesn't affect portfolio returns
        
        This creates a cash holding that increases total assets but doesn't 
        change the cost basis for return calculations.
        """
        try:
            if deposit_date is None:
                deposit_date = datetime.utcnow()
            
            # Determine cash symbol based on market
            cash_symbol = "CASH_USD" if currency == "USD" else "CASH_TWD"
            
            # Check if matching cash holding already exists
            existing_cash = self.db.get_holdings(portfolio_id)
            cash_holding = next((h for h in existing_cash 
                               if h.symbol == cash_symbol and h.currency == currency), None)
            
            if cash_holding:
                # Update existing cash holding - add to quantity
                new_quantity = cash_holding.quantity + amount
                self.db.adjust_holding_quantity(cash_holding.id, new_quantity)
                logger.info(f"已入金 {amount:.2f} {currency}，當前現金: {new_quantity:.2f} {currency}")
            else:
                # Create new cash holding
                self.db.add_holding(
                    portfolio_id=portfolio_id,
                    symbol=cash_symbol,
                    asset_type="現金",
                    quantity=amount,
                    purchase_price=1.0,  # Cash always has price of 1.0
                    purchase_date=deposit_date,
                    current_price=1.0,
                    market=market,
                    currency=currency,
                    notes=f"現金入金 - {notes}" if notes else "現金入金"
                )
                logger.info(f"已創建現金持倉: {cash_symbol} x {amount:.2f} {currency}")
            
            return True
        except Exception as e:
            logger.error(f"入金失敗: {e}")
            raise e

    def add_holding(self, portfolio_id: int, symbol: str, asset_type: str,
                   quantity: float, purchase_price: float, purchase_date: datetime,
                   market: str = "US", currency: str = "USD", notes: str = None):
        """Add a new holding"""
        try:
            # Handle cash deposit
            if symbol.upper() == "CASH" or asset_type == "現金":
                current_price = 1.0  # Cash is always 1.0
                currency = "USD" if market == "US" else "NTD"
            else:
                # Get current price
                current_price = DataFetcher.get_price(symbol, market)
                if not current_price:
                    logger.error(f"無法取得 {symbol} 的價格")
                    raise ValueError(f"無法取得 {symbol} 的價格")
            
            # Determine currency based on market if not provided
            if currency == "USD" and market == "TW":
                currency = "NTD"
            elif currency == "NTD" and market == "US":
                currency = "USD"
            
            holding = self.db.add_holding(
                portfolio_id=portfolio_id,
                symbol=symbol,
                asset_type=asset_type if asset_type != "現金" else "現金",
                quantity=quantity,
                purchase_price=purchase_price,
                purchase_date=purchase_date,
                current_price=current_price,
                market=market,
                currency=currency,
                notes=notes
            )
            
            logger.info(f"已添加持倉: {symbol} x {quantity} ({currency})")
            return holding
        except Exception as e:
            logger.error(f"添加持倉時出錯: {e}")
            raise
    
    def update_holding(self, holding_id: int, **kwargs):
        """Update a holding"""
        return self.db.update_holding(holding_id, **kwargs)
    
    def delete_holding(self, holding_id: int):
        """Delete a holding"""
        return self.db.delete_holding(holding_id)
    
    def create_portfolio(self, name: str, description: str = None):
        """Create new portfolio"""
        return self.db.create_portfolio(name, description)
    
    def get_portfolio(self, portfolio_id: int):
        """Get portfolio details"""
        return self.db.get_portfolio(portfolio_id)
    
    def get_all_portfolios(self, active_only: bool = True):
        """Get all portfolios"""
        return self.db.get_all_portfolios(active_only)

    def update_portfolio(self, portfolio_id: int, **kwargs):
        """Update portfolio details"""
        return self.db.update_portfolio(portfolio_id, **kwargs)

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete portfolio (soft delete)"""
        return self.db.delete_portfolio(portfolio_id)

    def adjust_holding_quantity(self, holding_id: int, new_quantity: float, new_price: float = None):
        """Adjust holding quantity (reduce position or sell)"""
        return self.db.adjust_holding_quantity(holding_id, new_quantity, new_price)
    
    def sell_position(self, portfolio_id: int, holding_id: int, sell_quantity: float):
        """Sell a position and convert proceeds to cash"""
        holding = self.db.get_holdings(portfolio_id)
        holding_obj = next((h for h in holding if h.id == holding_id), None)
        
        if not holding_obj:
            raise ValueError("持倉不存在")
        
        if sell_quantity > holding_obj.quantity:
            raise ValueError("賣出數量超過持倉數量")
        
        # Calculate proceeds and realized P&L
        proceeds = sell_quantity * holding_obj.current_price
        cost_sold = sell_quantity * holding_obj.purchase_price
        realized_pl = proceeds - cost_sold
        
        # Update original holding quantity
        new_quantity = holding_obj.quantity - sell_quantity
        if new_quantity > 0:
            self.db.adjust_holding_quantity(holding_id, new_quantity)
            logger.info(f"已減碼 {holding_obj.symbol}: {sell_quantity} 股，已實現損益: ${realized_pl:.2f}")
        else:
            # Delete if sold all
            self.db.delete_holding(holding_id)
            logger.info(f"已賣出 {holding_obj.symbol}: {holding_obj.quantity} 股，已實現損益: ${realized_pl:.2f}")
        
        # Update portfolio's total realized P&L
        portfolio = self.db.get_portfolio(portfolio_id)
        if portfolio:
            new_total_realized_pl = (portfolio.total_realized_pl or 0.0) + realized_pl
            self.db.update_portfolio(portfolio_id, total_realized_pl=new_total_realized_pl)
        
        # Record transaction
        self.db.record_transaction(
            portfolio_id=portfolio_id,
            symbol=holding_obj.symbol,
            transaction_type="SELL",
            quantity=sell_quantity,
            price=holding_obj.current_price,
            transaction_date=datetime.utcnow(),
            realized_pl=realized_pl,
            notes=f"減碼/賣出 {holding_obj.symbol}"
        )
        
        # Add cash holding - convert proceeds to standardized cash holding
        cash_symbol = "CASH_USD" if holding_obj.currency == "USD" else "CASH_TWD"
        cash_asset_type = "現金"
        
        # Check if matching cash holding already exists
        cash_holdings = [h for h in self.db.get_holdings(portfolio_id) 
                        if h.symbol == cash_symbol and h.currency == holding_obj.currency]
        
        if cash_holdings:
            # Update existing cash by merging proceeds
            cash_holding = cash_holdings[0]
            new_cash_amount = cash_holding.quantity + proceeds
            self.db.adjust_holding_quantity(cash_holding.id, new_cash_amount)
            logger.info(f"已增加現金 {proceeds:.2f} {holding_obj.currency}，當前現金: {new_cash_amount:.2f} {holding_obj.currency}")
        else:
            # Create new cash holding
            self.db.add_holding(
                portfolio_id=portfolio_id,
                symbol=cash_symbol,
                asset_type=cash_asset_type,
                quantity=proceeds,
                purchase_price=1.0,
                purchase_date=datetime.utcnow(),
                current_price=1.0,
                market=holding_obj.market,
                currency=holding_obj.currency,
                notes=f"從出售{holding_obj.symbol}轉換而來"
            )
            logger.info(f"已轉換 {proceeds:.2f} {holding_obj.currency} 為現金({cash_symbol})")
    
    # ============ Option Management ============
    
    def add_option(self, portfolio_id: int, symbol: str, option_type: str,
                  strike: float, expiration: datetime, quantity: int,
                  premium: float, market: str = "US", currency: str = "USD",
                  notes: str = None):
        """Add a new option contract to portfolio
        
        Args:
            portfolio_id: Portfolio ID
            symbol: Underlying stock symbol (e.g., 'TSLA')
            option_type: 'CALL' or 'PUT'
            strike: Strike price
            expiration: Expiration date
            quantity: Number of contracts (1 contract = 100 shares)
            premium: Price paid per share (actual cost = quantity * 100 * premium)
            market: 'US' or 'TW'
            currency: 'USD' or 'NTD'
            notes: Optional notes
        
        Returns:
            Option contract object
        """
        try:
            # Get current option price
            expiration_str = expiration.strftime("%Y-%m-%d")
            current_price = DataFetcher.get_option_price(symbol, expiration_str, strike, option_type)
            
            if current_price is None:
                logger.warning(f"無法取得選擇權價格，使用輸入的期權費率: {premium}")
                current_price = premium
            
            option = self.db.add_option(
                portfolio_id=portfolio_id,
                symbol=symbol,
                option_type=option_type.upper(),
                strike=strike,
                expiration=expiration,
                quantity=quantity,
                premium=premium,
                current_price=current_price,
                market=market,
                currency=currency,
                notes=notes
            )
            
            logger.info(f"已添加選擇權: {symbol} {option_type} {strike} @ {expiration.strftime('%Y-%m-%d')}, 數量: {quantity}")
            return option
        except Exception as e:
            logger.error(f"添加選擇權時出錯: {e}")
            raise
    
    def get_options(self, portfolio_id: int) -> List[OptionDetail]:
        """Get all options for a portfolio with calculated performance"""
        options = self.db.get_options(portfolio_id)
        option_details = []
        
        for option in options:
            detail = self._calculate_option_performance(option)
            option_details.append(detail)
        
        return option_details
    
    def _calculate_option_performance(self, option) -> OptionDetail:
        """Calculate performance metrics for an option"""
        # Cost basis: number of contracts * 100 shares per contract * premium per share
        cost_basis = option.quantity * 100 * option.premium
        
        # Current value: number of contracts * 100 shares per contract * current price per share
        current_value = option.quantity * 100 * option.current_price
        
        # Unrealized P&L
        unrealized_pl = current_value - cost_basis
        
        # Unrealized return %
        unrealized_return_pct = (unrealized_pl / cost_basis * 100) if cost_basis > 0 else 0
        
        return OptionDetail(
            symbol=option.symbol,
            option_type=option.option_type,
            strike=option.strike,
            expiration=option.expiration,
            quantity=option.quantity,
            premium=option.premium,
            current_price=option.current_price,
            cost_basis=cost_basis,
            current_value=current_value,
            unrealized_pl=unrealized_pl,
            unrealized_return_pct=unrealized_return_pct,
            status=option.status,
            market=option.market,
            currency=option.currency,
            last_updated=option.price_updated_at
        )
    
    def close_option(self, option_id: int, close_price: float) -> Optional[OptionDetail]:
        """Close an option contract"""
        try:
            option = self.db.close_option(option_id, close_price)
            if option:
                logger.info(f"已平倉選擇權: {option.symbol} {option.option_type} {option.strike}")
                return self._calculate_option_performance(option)
            return None
        except Exception as e:
            logger.error(f"平倉選擇權時出錯: {e}")
            raise
    
    def expire_option(self, option_id: int) -> Optional[OptionDetail]:
        """Mark option as expired"""
        try:
            option = self.db.expire_option(option_id)
            if option:
                logger.info(f"已標記選擇權為過期: {option.symbol} {option.option_type} {option.strike}")
                return self._calculate_option_performance(option)
            return None
        except Exception as e:
            logger.error(f"標記選擇權過期時出錯: {e}")
            raise
    
    def delete_option(self, option_id: int) -> bool:
        """Delete an option contract"""
        try:
            result = self.db.delete_option(option_id)
            if result:
                logger.info(f"已刪除選擇權合約: ID {option_id}")
            return result
        except Exception as e:
            logger.error(f"刪除選擇權時出錯: {e}")
            raise
    
    def get_option_chain(self, symbol: str) -> List[str]:
        """Get available option expirations for a stock"""
        try:
            expirations = DataFetcher.get_option_chain(symbol)
            logger.info(f"取得 {symbol} 的選擇權到期日: {expirations}")
            return expirations
        except Exception as e:
            logger.error(f"取得選擇權鏈時出錯: {e}")
            return []
    
    def get_option_quotes(self, symbol: str, expiration: str) -> Dict:
        """Get option quotes (calls and puts) for a specific symbol and expiration"""
        try:
            return DataFetcher.get_option_data(symbol, expiration)
        except Exception as e:
            logger.error(f"取得選擇權報價時出錯: {e}")
            return {'calls': {}, 'puts': {}, 'expiration': expiration}
    
    def get_all_portfolios_analysis(self) -> Dict:
        """Get analysis for all portfolios combined"""
        portfolios = self.get_all_portfolios()
        
        all_holdings_details = []
        total_metrics_us = None
        total_metrics_tw = None
        
        for portfolio in portfolios:
            _, holdings_details, _ = self.get_portfolio_performance(portfolio.id)
            
            # Separate by currency
            holdings_us = [h for h in holdings_details if getattr(h, 'currency', 'USD') == 'USD']
            holdings_tw = [h for h in holdings_details if getattr(h, 'currency', 'NTD') == 'NTD']
            portfolio_realized_pl = portfolio.total_realized_pl or 0.0
            
            # Split realized P/L by currency exposure when needed
            total_current_value = sum(h.current_value for h in holdings_us) + sum(h.current_value for h in holdings_tw)
            us_realized_pl = portfolio_realized_pl
            tw_realized_pl = 0.0
            if holdings_us and holdings_tw and total_current_value > 0:
                us_ratio = sum(h.current_value for h in holdings_us) / total_current_value
                us_realized_pl = portfolio_realized_pl * us_ratio
                tw_realized_pl = portfolio_realized_pl * (1 - us_ratio)
            elif holdings_tw and not holdings_us:
                us_realized_pl = 0.0
                tw_realized_pl = portfolio_realized_pl

            if holdings_us:
                us_metrics = PortfolioCalculator.calculate_portfolio_metrics(holdings_us, total_realized_pl=us_realized_pl)
                if total_metrics_us is None:
                    total_metrics_us = us_metrics
                else:
                    total_metrics_us.total_value += us_metrics.total_value
                    total_metrics_us.total_cost += us_metrics.total_cost
                    total_metrics_us.total_realized_pl += us_metrics.total_realized_pl
                    total_metrics_us.total_pl += us_metrics.total_pl
                    total_metrics_us.total_pl_percentage = (total_metrics_us.total_pl / total_metrics_us.total_cost * 100) if total_metrics_us.total_cost > 0 else 0

            if holdings_tw:
                tw_metrics = PortfolioCalculator.calculate_portfolio_metrics(holdings_tw, total_realized_pl=tw_realized_pl)
                if total_metrics_tw is None:
                    total_metrics_tw = tw_metrics
                else:
                    total_metrics_tw.total_value += tw_metrics.total_value
                    total_metrics_tw.total_cost += tw_metrics.total_cost
                    total_metrics_tw.total_realized_pl += tw_metrics.total_realized_pl
                    total_metrics_tw.total_pl += tw_metrics.total_pl
                    total_metrics_tw.total_pl_percentage = (total_metrics_tw.total_pl / total_metrics_tw.total_cost * 100) if total_metrics_tw.total_cost > 0 else 0

            all_holdings_details.extend(holdings_details)
        
        return {
            "total_portfolios": len(portfolios),
            "us_metrics": total_metrics_us,
            "tw_metrics": total_metrics_tw,
            "all_holdings": all_holdings_details,
            "portfolios": portfolios
        }
    
    def get_performance_history(self, portfolio_id: int):
        """Get performance history for trend chart"""
        try:
            return self.db.get_performance_history(portfolio_id)
        except Exception as e:
            logger.error(f"Error getting performance history: {e}")
            return []
