"""Sidebar UI components"""
import streamlit as st
from backend.portfolio_manager import PortfolioManager
from config.ui_config import VIEW_MODES, SUCCESS_MESSAGES, LOADING_MESSAGES
from core.session_manager import SessionManager

def render_sidebar():
    """Render sidebar for portfolio selection"""
    pm = PortfolioManager()
    session_manager = SessionManager()

    with st.sidebar:
        st.title("🔥 投資組合控制")

        # View mode selection
        view_mode = st.radio("選擇檢視模式", VIEW_MODES)
        session_manager.set("view_mode", view_mode)
        portfolios = pm.get_all_portfolios()
        if portfolios:
            portfolio_names = {p.id: p.name for p in portfolios}
            selected_name = st.selectbox(
                "選擇投資組合",
                options=list(portfolio_names.values()),
                format_func=lambda x: x
            )
            st.session_state.portfolio_id = [p.id for p in portfolios if p.name == selected_name][0]

        st.divider()

        # Refresh button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 刷新價格", use_container_width=True):
                if view_mode == "個別投資組合" and st.session_state.portfolio_id:
                    with st.spinner("正在更新價格..."):
                        pm.refresh_prices(st.session_state.portfolio_id)
                        st.session_state.last_refresh = st.session_state.get("last_refresh")
                        st.success("價格已更新！")
                elif view_mode == "所有投資組合":
                    with st.spinner("正在更新全部投資組合..."):
                        for portfolio in pm.get_all_portfolios():
                            pm.refresh_prices(portfolio.id)
                        st.session_state.last_refresh = st.session_state.get("last_refresh")
                        st.success("全部價格已更新！")

        with col2:
            if st.button("➕ 添加持倉", use_container_width=True):
                if view_mode == "個別投資組合":
                    st.session_state.show_add_form = True
                else:
                    st.warning("請切換到個別投資組合模式")

        st.divider()

        # Last refresh info
        if st.session_state.get("last_refresh"):
            from utils.helpers import format_date
            st.info(f"最後刷新：{format_date(st.session_state.last_refresh, '%Y-%m-%d %H:%M')}")

        st.divider()

        # Settings section
        st.subheader("⚙️ 設定")
        if st.button("建立新投資組合"):
            st.session_state.show_portfolio_form = True