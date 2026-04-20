"""Portfolio performance calculator"""
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from backend.models import HoldingDetail, PerformanceMetrics
from backend.data_fetcher import DataFetcher

class PortfolioCalculator:
    """Calculates portfolio performance metrics"""
    
    @staticmethod
    def calculate_holding_performance(
        symbol: str,
        quantity: float,
        purchase_price: float,
        current_price: float,
        purchase_date: datetime,
        asset_type: str,
        market: str,
        currency: str = "USD"
    ) -> HoldingDetail:
        """Calculate performance for a single holding"""
        
        cost_basis = quantity * purchase_price
        current_value = quantity * current_price
        unrealized_pl = current_value - cost_basis
        unrealized_return_pct = (unrealized_pl / cost_basis * 100) if cost_basis != 0 else 0
        
        return HoldingDetail(
            symbol=symbol,
            asset_type=asset_type,
            quantity=quantity,
            purchase_price=purchase_price,
            current_price=current_price,
            cost_basis=cost_basis,
            current_value=current_value,
            unrealized_pl=unrealized_pl,
            unrealized_return_pct=unrealized_return_pct,
            market=market,
            currency=currency,
            last_updated=datetime.utcnow()
        )
    
    @staticmethod
    def calculate_portfolio_metrics(
        holdings_details: List[HoldingDetail],
        total_realized_pl: float = 0.0
    ) -> PerformanceMetrics:
        """Calculate overall portfolio metrics"""
        
        total_cost = sum(h.cost_basis for h in holdings_details)
        total_value = sum(h.current_value for h in holdings_details)
        total_unrealized_pl = sum(h.unrealized_pl for h in holdings_details)
        
        total_realized_pl = total_realized_pl or 0.0
        total_pl = total_unrealized_pl + total_realized_pl
        
        return_percentage = (total_pl / total_cost * 100) if total_cost != 0 else 0
        unrealized_return_percentage = (total_unrealized_pl / total_cost * 100) if total_cost != 0 else 0
        realized_return_percentage = (total_realized_pl / total_cost * 100) if total_cost != 0 else 0
        
        return PerformanceMetrics(
            total_value=round(total_value, 2),
            total_cost=round(total_cost, 2),
            total_realized_pl=round(total_realized_pl, 2),
            total_unrealized_pl=round(total_unrealized_pl, 2),
            total_pl=round(total_pl, 2),
            return_percentage=round(return_percentage, 2),
            realized_return_percentage=round(realized_return_percentage, 2),
            unrealized_return_percentage=round(unrealized_return_percentage, 2)
        )
    
    @staticmethod
    def calculate_asset_distribution(holdings_details: List[HoldingDetail]) -> Dict[str, float]:
        """Calculate portfolio asset distribution"""
        
        distribution = {}
        total_value = sum(h.current_value for h in holdings_details)
        
        if total_value == 0:
            return distribution
        
        for holding in holdings_details:
            asset_type = holding.asset_type
            if asset_type not in distribution:
                distribution[asset_type] = 0
            distribution[asset_type] += holding.current_value / total_value * 100
        
        return {k: round(v, 2) for k, v in distribution.items()}
    
    @staticmethod
    def calculate_sharpe_ratio(
        daily_returns: List[float],
        risk_free_rate: float = 2.0
    ) -> float:
        """Calculate Sharpe ratio"""
        
        if len(daily_returns) < 2:
            return 0.0
        
        daily_returns_array = np.array(daily_returns)
        excess_returns = daily_returns_array - (risk_free_rate / 252 / 100)
        
        sharpe_ratio = np.mean(excess_returns) / (np.std(excess_returns) + 1e-6) * np.sqrt(252)
        return round(float(sharpe_ratio), 2)
    
    @staticmethod
    def calculate_max_drawdown(portfolio_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        
        if len(portfolio_values) < 2:
            return 0.0
        
        values_array = np.array(portfolio_values)
        cummax = np.maximum.accumulate(values_array)
        drawdown = (values_array - cummax) / cummax * 100
        max_drawdown = np.min(drawdown)
        
        return round(float(max_drawdown), 2)
    
    @staticmethod
    def calculate_daily_returns(portfolio_values: List[float]) -> List[float]:
        """Calculate daily returns from portfolio values"""
        
        if len(portfolio_values) < 2:
            return []
        
        values_array = np.array(portfolio_values)
        returns = np.diff(values_array) / values_array[:-1] * 100
        return returns.tolist()
    
    @staticmethod
    def calculate_benchmark_comparison(
        portfolio_dataframe: pd.DataFrame,
        benchmark_dataframe: pd.DataFrame,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, float]:
        """Compare portfolio performance with benchmark"""
        
        # Normalize both series to 100 at start
        port_normalized = (portfolio_dataframe / portfolio_dataframe.iloc[0] * 100) if len(portfolio_dataframe) > 0 else portfolio_dataframe
        bench_normalized = (benchmark_dataframe / benchmark_dataframe.iloc[0] * 100) if len(benchmark_dataframe) > 0 else benchmark_dataframe
        
        return {
            "portfolio_final": round(port_normalized.iloc[-1], 2) if len(port_normalized) > 0 else 0,
            "benchmark_final": round(bench_normalized.iloc[-1], 2) if len(bench_normalized) > 0 else 0,
            "outperformance": round(port_normalized.iloc[-1] - bench_normalized.iloc[-1], 2) if len(port_normalized) > 0 and len(bench_normalized) > 0 else 0
        }

class PortfolioAnalyzer:
    """Advanced portfolio analysis"""
    
    @staticmethod
    def get_market_exposure(holdings_details: List[HoldingDetail]) -> Dict[str, float]:
        """Calculate exposure by market (US vs Taiwan)"""
        
        us_value = sum(h.current_value for h in holdings_details if h.market == "US")
        tw_value = sum(h.current_value for h in holdings_details if h.market == "TW")
        total_value = us_value + tw_value
        
        if total_value == 0:
            return {"US": 0, "TW": 0}
        
        return {
            "US": round(us_value / total_value * 100, 2),
            "TW": round(tw_value / total_value * 100, 2)
        }
    
    @staticmethod
    def get_top_performers(holdings_details: List[HoldingDetail], top_n: int = 5) -> List[HoldingDetail]:
        """Get top N performers by return percentage"""
        
        sorted_holdings = sorted(
            holdings_details,
            key=lambda x: x.unrealized_return_pct,
            reverse=True
        )
        return sorted_holdings[:top_n]
    
    @staticmethod
    def get_worst_performers(holdings_details: List[HoldingDetail], top_n: int = 5) -> List[HoldingDetail]:
        """Get worst N performers by return percentage"""
        
        sorted_holdings = sorted(
            holdings_details,
            key=lambda x: x.unrealized_return_pct
        )
        return sorted_holdings[:top_n]
