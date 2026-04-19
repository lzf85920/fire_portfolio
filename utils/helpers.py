"""Utility helper functions"""
import pandas as pd
from datetime import datetime
from typing import Dict, List

def format_currency(value: float, currency: str = "USD", decimal_places: int = 2) -> str:
    """Format value as currency"""
    if currency == "NTD":
        return f"NT${value:,.{decimal_places}f}"
    else:
        return f"${value:,.{decimal_places}f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage"""
    symbol = "+" if value >= 0 else ""
    return f"{symbol}{value:.{decimal_places}f}%"

def get_percentage_color(value: float) -> str:
    """Get color for percentage value (for UI display)"""
    if value > 0:
        return "#06D6A0"  # Green
    elif value < 0:
        return "#EF476F"  # Red
    else:
        return "#FFD166"  # Yellow

def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime to string"""
    if isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
    return date.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """Parse date string to datetime"""
    return datetime.strptime(date_str, format_str)

def round_to_decimals(value: float, decimals: int = 2) -> float:
    """Round value to specified decimal places"""
    return round(value, decimals)

def get_change_badge(value: float, decimal_places: int = 2) -> Dict:
    """Get badge information for change value"""
    if value > 0:
        return {
            "value": format_percentage(value, decimal_places),
            "color": "#06D6A0",
            "icon": "📈"
        }
    elif value < 0:
        return {
            "value": format_percentage(value, decimal_places),
            "color": "#EF476F",
            "icon": "📉"
        }
    else:
        return {
            "value": "0%",
            "color": "#FFD166",
            "icon": "➡️"
        }

def sum_values(values: List[float]) -> float:
    """Sum list of values safely"""
    return sum(v for v in values if v is not None)

def calculate_average(values: List[float]) -> float:
    """Calculate average of values"""
    clean_values = [v for v in values if v is not None]
    return sum(clean_values) / len(clean_values) if len(clean_values) > 0 else 0

def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string to max length"""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text
