"""Main Streamlit Dashboard Application"""
import logging
import streamlit as st
from datetime import datetime
from authentication import authenticate
from config.ui_config import PAGE_CONFIG, CUSTOM_CSS
from core.session_manager import SessionManager
from core.error_handler import ErrorHandler, safe_execute
from ui.factory import UIRendererFactory
from ui.sidebar import render_sidebar

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

class DashboardApp:
    """Main dashboard application with improved architecture"""

    def __init__(self):
        self.session_manager = SessionManager()
        self.renderers = UIRendererFactory.create_all_renderers()
        self.session_manager.initialize_session_state()

    @ErrorHandler.with_error_handling("Dashboard rendering")
    def run(self):
        """Run the dashboard with improved error handling"""
        st.title("🔥 投資組合儀表板")

        # Render sidebar
        render_sidebar()

        # Render portfolio form if needed
        self.renderers["portfolio"].render_portfolio_form()

        # Main content based on view mode
        view_mode = self.session_manager.get("view_mode", "所有投資組合")

        if view_mode == "所有投資組合":
            self._render_all_portfolios_view()
        else:
            self._render_individual_portfolio_view()

    def _render_all_portfolios_view(self):
        """Render all portfolios combined view"""
        pm = self.renderers["metrics"].pm

        analysis = safe_execute(
            pm.get_all_portfolios_analysis,
            error_msg="載入所有投資組合數據"
        )

        if not analysis:
            return

        if analysis["total_portfolios"] == 0:
            st.warning("找不到投資組合。請先建立一個。")
            if st.button("建立第一個投資組合"):
                self.session_manager.set("show_portfolio_form", True)
        else:
            self.renderers["metrics"].render_metrics(analysis, is_all_portfolios=True)
            st.divider()

    def _render_individual_portfolio_view(self):
        """Render individual portfolio view"""
        portfolio_id = self.session_manager.get("portfolio_id")

        if not portfolio_id:
            st.warning("找不到投資組合。請先建立一個。")
            if st.button("建立第一個投資組合"):
                self.session_manager.set("show_portfolio_form", True)
            return

        # Get portfolio analysis
        analysis = safe_execute(
            self.renderers["metrics"].pm.get_portfolio_analysis,
            portfolio_id,
            error_msg="載入投資組合數據"
        )

        if not analysis:
            return

        # Render all components
        self.renderers["metrics"].render_metrics(analysis, is_all_portfolios=False)
        st.divider()

        self.renderers["charts"].render_daily_trend_chart(portfolio_id, analysis)
        st.divider()

        self.renderers["charts"].render_distribution_chart(analysis)
        st.divider()

        st.subheader("📋 持倉詳情")
        self.renderers["forms"].render_holdings_table(analysis)
        st.divider()

        self.renderers["forms"].render_add_holding_form()

if __name__ == "__main__":
    # if authenticate():
    app = DashboardApp()
    app.run()
