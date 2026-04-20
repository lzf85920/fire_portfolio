"""Application configuration and constants"""
import os

# Page Configuration
PAGE_CONFIG = {
    "page_title": "🔥 財富自由儀表板",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Custom CSS
CUSTOM_CSS = """
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
        }
        .positive {
            color: #06D6A0;
        }
        .negative {
            color: #EF476F;
        }
        .neutral {
            color: #FFD166;
        }
    </style>
"""

# UI Constants
VIEW_MODES = ["所有投資組合", "個別投資組合"]
MARKETS = ["🇺🇸 美股 (USD)", "🇹🇼 台股 (NTD)"]
ASSET_CLASSES = ["股票", "ETF", "債券", "基金", "現金", "其他"]

# Session State Keys
SESSION_KEYS = {
    "portfolio_id": "portfolio_id",
    "last_refresh": "last_refresh",
    "view_mode": "view_mode",
    "show_add_form": "show_add_form",
    "show_portfolio_form": "show_portfolio_form",
    "confirm_add": "confirm_add",
    "confirm_adjust": "confirm_adjust",
    "trend_window": "trend_window",
    "authenticated": "authenticated"
}

# Default Values
DEFAULTS = {
    "view_mode": "所有投資組合",
    "trend_window": "半年"
}

# Error Messages
ERROR_MESSAGES = {
    "no_portfolio": "找不到投資組合。請先建立一個。",
    "load_error": "載入投資組合時出錯",
    "add_holding_error": "添加持倉時出錯",
    "adjust_holding_error": "調整持倉時出錯",
    "no_holdings": "此投資組合中沒有持倉",
    "no_distribution": "沒有持倉可顯示",
    "invalid_quantity": "請輸入有效的調整數量",
    "invalid_fields": "請填寫所有必填字段"
}

# Success Messages
SUCCESS_MESSAGES = {
    "price_updated": "價格已更新！",
    "all_prices_updated": "全部價格已更新！",
    "holding_added": "成功添加！",
    "holding_adjusted": "已調整"
}

# Loading Messages
LOADING_MESSAGES = {
    "updating_prices": "正在更新價格...",
    "updating_all": "正在更新全部投資組合...",
    "adding_holding": "正在添加持倉...",
    "adjusting_holding": "正在調整持倉..."
}