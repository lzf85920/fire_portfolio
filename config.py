"""Configuration settings for Fire Portfolio Dashboard"""
import os
from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "portfolio.db"

# Database Configuration
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Data Sources Configuration
DATA_SOURCES = {
    "yfinance": {"enabled": True, "type": "US stocks/ETFs"},
    "twstock": {"enabled": True, "type": "Taiwan stocks"},
    "tdx": {"enabled": True, "type": "TDX API (Taiwan)"}
}

# Risk-free rate for Sharpe ratio calculation (annual %)
RISK_FREE_RATE = 2.0

# Supported index symbols for benchmark comparison
BENCHMARK_INDICES = {
    "SP500": "^GSPC",      # S&P 500
    "QQQ": "^IXIC",        # NASDAQ
    "0050": "0050.TW",     # Taiwan ETF
    "VTI": "VTI",          # Vanguard Total US Stock Market
}

# Supported asset classes
ASSET_CLASSES = [
    "美股",
    "台股",
    "現金",
    "其他"
]

# Dashboard refresh interval (minutes)
REFRESH_INTERVAL = 1440  # 24 hours

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = ROOT_DIR / "logs" / "portfolio.log"

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
