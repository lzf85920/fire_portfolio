"""Session state management"""
import streamlit as st
from datetime import datetime
from backend.portfolio_manager import PortfolioManager
from config.ui_config import SESSION_KEYS, DEFAULTS

class SessionManager:
    """Manages Streamlit session state"""

    def __init__(self):
        self.pm = PortfolioManager()

    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Portfolio state
        if SESSION_KEYS["portfolio_id"] not in st.session_state:
            portfolios = self.pm.get_all_portfolios()
            st.session_state[SESSION_KEYS["portfolio_id"]] = portfolios[0].id if portfolios else None

        # UI state
        if SESSION_KEYS["last_refresh"] not in st.session_state:
            st.session_state[SESSION_KEYS["last_refresh"]] = None

        if SESSION_KEYS["view_mode"] not in st.session_state:
            st.session_state[SESSION_KEYS["view_mode"]] = DEFAULTS["view_mode"]

        if SESSION_KEYS["trend_window"] not in st.session_state:
            st.session_state[SESSION_KEYS["trend_window"]] = DEFAULTS["trend_window"]

        # Form states
        if SESSION_KEYS["show_add_form"] not in st.session_state:
            st.session_state[SESSION_KEYS["show_add_form"]] = False

        if SESSION_KEYS["show_portfolio_form"] not in st.session_state:
            st.session_state[SESSION_KEYS["show_portfolio_form"]] = False

        # Confirmation states
        if SESSION_KEYS["confirm_add"] not in st.session_state:
            st.session_state[SESSION_KEYS["confirm_add"]] = None

        if SESSION_KEYS["confirm_adjust"] not in st.session_state:
            st.session_state[SESSION_KEYS["confirm_adjust"]] = None

        # Authentication
        if SESSION_KEYS["authenticated"] not in st.session_state:
            st.session_state[SESSION_KEYS["authenticated"]] = False

    def get(self, key: str, default=None):
        """Get session state value"""
        return st.session_state.get(SESSION_KEYS.get(key, key), default)

    def set(self, key: str, value):
        """Set session state value"""
        st.session_state[SESSION_KEYS.get(key, key)] = value

    def update_last_refresh(self):
        """Update last refresh timestamp"""
        self.set("last_refresh", datetime.now())

    def reset_form_states(self):
        """Reset all form-related states"""
        self.set("show_add_form", False)
        self.set("show_portfolio_form", False)
        self.set("confirm_add", None)
        self.set("confirm_adjust", None)