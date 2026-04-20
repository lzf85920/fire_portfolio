"""Configuration package for the application"""
import os
from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "portfolio.db"

# Database Configuration
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Supported asset classes
ASSET_CLASSES = [
    "美股",
    "台股",
    "現金",
    "其他"
]

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)