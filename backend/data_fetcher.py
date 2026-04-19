"""Data fetcher for stock prices"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches real-time stock and ETF data"""
    
    @staticmethod
    def get_us_price(symbol: str) -> Optional[float]:
        """Get current price for US stock/ETF"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return round(data["Close"].iloc[-1], 2)
            logger.warning(f"找不到美股 {symbol} 的數據")
            return None
        except Exception as e:
            logger.error(f"取得美股 {symbol} 的價格時出錯: {e}")
            return None
    
    @staticmethod
    def get_taiwan_price(symbol: str) -> Optional[float]:
        """Get current price for Taiwan stock"""
        try:
            # Taiwan stocks need .TW suffix if not already present
            if not symbol.endswith(".TW"):
                symbol = f"{symbol}.TW"
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return round(data["Close"].iloc[-1], 2)
            logger.warning(f"找不到台股 {symbol} 的數據")
            return None
        except Exception as e:
            logger.error(f"取得台股 {symbol} 的價格時出錯: {e}")
            return None
    
    @staticmethod
    def get_price(symbol: str, market: str = "US") -> Optional[float]:
        """Get current price based on market"""
        # Handle cash
        if symbol.upper() == "CASH":
            return 1.0
        
        if market.upper() == "TW":
            return DataFetcher.get_taiwan_price(symbol)
        else:
            return DataFetcher.get_us_price(symbol)
    
    @staticmethod
    def get_historical_data(symbol: str, period: str = "1y", market: str = "US") -> pd.DataFrame:
        """Get historical price data"""
        try:
            if market.upper() == "TW" and not symbol.endswith(".TW"):
                symbol = f"{symbol}.TW"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                logger.warning(f"找不到 {symbol} 的歷史數據")
                return pd.DataFrame()
            
            # Rename columns to lowercase for consistency
            data.columns = data.columns.str.lower()
            return data
        except Exception as e:
            logger.error(f"取得 {symbol} 的斷點斷市歷史數據時出錯: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_multiple_prices(symbols: List[str], market: str = "US") -> Dict[str, Optional[float]]:
        """Get multiple prices at once"""
        prices = {}
        for symbol in symbols:
            prices[symbol] = DataFetcher.get_price(symbol, market)
        return prices
    
    @staticmethod
    def get_index_price(index_symbol: str) -> Optional[float]:
        """Get benchmark index price"""
        try:
            ticker = yf.Ticker(index_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return round(data["Close"].iloc[-1], 2)
            return None
        except Exception as e:
            logger.error(f"取得指數 {index_symbol} 的價格時出錯: {e}")
            return None
    
    @staticmethod
    def get_index_historical(index_symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get index historical data"""
        try:
            ticker = yf.Ticker(index_symbol)
            data = ticker.history(period=period)
            if data.empty:
                return pd.DataFrame()
            data.columns = data.columns.str.lower()
            return data
        except Exception as e:
            logger.error(f"取得指數 {index_symbol} 的斷點斷市歷史數據時出錯: {e}")
            return pd.DataFrame()

# Try to import twstock for Taiwan stocks (optional)
try:
    import twstock
    
    class TwstockFetcher:
        """Alternative fetcher for Taiwan stocks using twstock"""
        
        @staticmethod
        def get_taiwan_price(symbol: str) -> Optional[float]:
            """Get current price for Taiwan stock using twstock"""
            try:
                # Remove .TW suffix if present
                symbol_clean = symbol.replace(".TW", "")
                data = twstock.get(symbol_clean)
                if data and data.get("data"):
                    latest = data["data"][-1]
                    # twstock returns [date, cap, vol, open, high, low, close, ...]
                    return float(latest[6])  # close price
                return None
            except Exception as e:
                logger.warning(f"twstock not available or error: {e}")
                return None
    
except ImportError:
    logger.info("twstock not installed, using yfinance for Taiwan stocks")
