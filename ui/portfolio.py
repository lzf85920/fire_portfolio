"""Portfolio UI components for creating and managing portfolios"""
import streamlit as st
from datetime import datetime
from backend.portfolio_manager import PortfolioManager
from utils.helpers import format_date
from config.ui_config import SUCCESS_MESSAGES, ERROR_MESSAGES

class PortfolioRenderer:
    """Handles rendering of portfolio creation and management UI"""

    def __init__(self, pm: PortfolioManager):
        self.pm = pm

    def render_portfolio_form(self):
        """Render form for creating new portfolio"""
        if not st.session_state.get("show_portfolio_form", False):
            return

        st.subheader("📁 建立新投資組合")

        with st.form("portfolio_form"):
            name = st.text_input("投資組合名稱", placeholder="例如：我的美股投資組合")
            description = st.text_area("描述（選填）", placeholder="簡要描述這個投資組合的投資策略或目標")

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("建立投資組合", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("取消", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("請輸入投資組合名稱")
                return

            try:
                # Create new portfolio
                portfolio = self.pm.create_portfolio(
                    name=name.strip(),
                    description=description.strip() if description else None
                )

                st.success(f"✅ {SUCCESS_MESSAGES.get('portfolio_created', '投資組合已建立')}: {portfolio.name}")

                # Reset form and update session state
                st.session_state.show_portfolio_form = False

                # Refresh sidebar to show new portfolio
                st.rerun()

            except Exception as e:
                st.error(f"{ERROR_MESSAGES.get('portfolio_create_error', '建立投資組合失敗')}: {str(e)}")

        if cancelled:
            st.session_state.show_portfolio_form = False
            st.rerun()

    def render_portfolio_list(self):
        """Render list of all portfolios for management"""
        st.subheader("📋 投資組合管理")

        portfolios = self.pm.get_all_portfolios()

        if not portfolios:
            st.info("目前沒有任何投資組合")
            return

        for portfolio in portfolios:
            with st.expander(f"📁 {portfolio.name}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**描述:** {portfolio.description or '無'}")
                    st.write(f"**建立時間:** {format_date(portfolio.created_at)}")
                    st.write(f"**最後更新:** {format_date(portfolio.updated_at)}")

                with col2:
                    if st.button("編輯", key=f"edit_{portfolio.id}", use_container_width=True):
                        st.session_state[f"edit_portfolio_{portfolio.id}"] = True

                with col3:
                    if st.button("刪除", key=f"delete_{portfolio.id}", use_container_width=True, type="secondary"):
                        st.session_state[f"confirm_delete_{portfolio.id}"] = True

                # Edit form
                if st.session_state.get(f"edit_portfolio_{portfolio.id}", False):
                    self._render_edit_form(portfolio)

                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{portfolio.id}", False):
                    self._render_delete_confirmation(portfolio)

    def _render_edit_form(self, portfolio):
        """Render edit form for portfolio"""
        st.divider()

        with st.form(f"edit_portfolio_{portfolio.id}"):
            name = st.text_input("投資組合名稱", value=portfolio.name)
            description = st.text_area("描述", value=portfolio.description or "")

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("儲存變更", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("取消", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("請輸入投資組合名稱")
                return

            try:
                self.pm.update_portfolio(
                    portfolio.id,
                    name=name.strip(),
                    description=description.strip() if description else None
                )

                st.success("✅ 投資組合已更新")
                st.session_state[f"edit_portfolio_{portfolio.id}"] = False
                st.rerun()

            except Exception as e:
                st.error(f"更新失敗: {str(e)}")

        if cancelled:
            st.session_state[f"edit_portfolio_{portfolio.id}"] = False
            st.rerun()

    def _render_delete_confirmation(self, portfolio):
        """Render delete confirmation dialog"""
        st.divider()
        st.warning(f"確定要刪除投資組合「{portfolio.name}」嗎？此操作無法復原！")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("確認刪除", key=f"confirm_del_{portfolio.id}", use_container_width=True, type="primary"):
                try:
                    self.pm.delete_portfolio(portfolio.id)
                    st.success("✅ 投資組合已刪除")
                    st.rerun()
                except Exception as e:
                    st.error(f"刪除失敗: {str(e)}")

        with col2:
            if st.button("取消", key=f"cancel_del_{portfolio.id}", use_container_width=True):
                st.session_state[f"confirm_delete_{portfolio.id}"] = False
                st.rerun()