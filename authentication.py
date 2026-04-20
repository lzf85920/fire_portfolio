"""Authentication module for dashboard access control"""
import os
import streamlit as st

def get_dashboard_password():
    """Load the 4-digit app password from environment or Streamlit secrets."""
    password = os.environ.get("APP_PASSWORD")
    if password:
        return password.strip()
    try:
        return st.secrets.get("APP_PASSWORD", "").strip()
    except Exception:
        return ""


def authenticate():
    """Require password before showing the dashboard."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    app_password = get_dashboard_password()

    st.title("🔒 請輸入訪問密碼")
    password_input = st.text_input(
        "請輸入 4 位數密碼以開啟儀表板",
        type="password",
        max_chars=4,
        key="login_password",
    )

    if st.button("登入"):
        if app_password and password_input == app_password:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("密碼錯誤，請重新輸入。")

    if not app_password:
        st.warning(
            "尚未設定 APP_PASSWORD。請在本機環境變數或 Streamlit Secrets 中設定 4 位數密碼。"
        )

    st.stop()
    return False