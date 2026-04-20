"""Error handling utilities"""
import streamlit as st
import logging
from functools import wraps
from config.ui_config import ERROR_MESSAGES

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles application errors consistently"""

    @staticmethod
    def handle_error(error: Exception, context: str = "", show_user: bool = True):
        """Handle and log errors"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_msg, exc_info=True)

        if show_user:
            st.error(f"{ERROR_MESSAGES.get('load_error', '操作失敗')}: {str(error)}")

    @staticmethod
    def with_error_handling(operation_name: str = ""):
        """Decorator for consistent error handling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ErrorHandler.handle_error(e, operation_name)
                    return None
            return wrapper
        return decorator

def safe_execute(func, *args, error_msg: str = "操作失敗", **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        ErrorHandler.handle_error(e, error_msg)
        return None