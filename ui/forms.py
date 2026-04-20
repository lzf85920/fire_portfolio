"""Forms UI components for adding and adjusting holdings"""
from typing import Dict

import streamlit as st
import pandas as pd
from backend.portfolio_manager import PortfolioManager
from utils.helpers import format_currency, format_percentage

class FormsRenderer:
    """Handles rendering of forms for portfolio operations"""

    def __init__(self, portfolio_manager=None):
        # Allow dependency injection
        self.pm = portfolio_manager or PortfolioManager()

    def render_add_holding_form(self):
        """Render form to add new holding"""
        if "show_add_form" not in st.session_state:
            st.session_state.show_add_form = False

        if st.session_state.show_add_form:
            st.subheader("➕ 添加新持倉")

            with st.form("add_holding_form"):
                # Market selection
                market = st.radio("選擇市場", ["🇺🇸 美股 (USD)", "🇹🇼 台股 (NTD)"])
                market_code = "US" if "美股" in market else "TW"
                currency = "USD" if market_code == "US" else "NTD"

                # Asset type and symbol
                col1, col2 = st.columns(2)

                with col1:
                    import config
                    asset_type = st.selectbox("資產類別", config.ASSET_CLASSES, key="asset_type")

                with col2:
                    if asset_type == "現金":
                        symbol = "CASH"
                        st.text_input("代碼", value=symbol, disabled=True, key="symbol")
                    else:
                        symbol = st.text_input("代碼 (例如: AAPL, 2330.TW)", key="symbol")

                # Quantity and purchase price
                col3, col4 = st.columns(2)

                with col3:
                    quantity = st.number_input("數量/金額", min_value=0.0, step=0.01, key="quantity")

                with col4:
                    if asset_type == "現金":
                        purchase_price = 1.0
                        st.text_input("購買價格", value="1.00", disabled=True, key="purchase_price")
                    else:
                        purchase_price = st.number_input("購買價格", min_value=0.0, step=0.01, key="purchase_price")

                # Purchase date
                purchase_date = st.date_input("購買日期", key="purchase_date")

                # Notes
                notes = st.text_area("備註（可選）", key="notes")

                submitted = st.form_submit_button("添加持倉", use_container_width=True)

                if submitted:
                    if not symbol or (not purchase_price and asset_type != "現金") or not quantity:
                        st.error("請填寫所有必填字段")
                    else:
                        # 設定確認資料
                        st.session_state.confirm_add = {
                            'symbol': symbol,
                            'asset_type': asset_type,
                            'quantity': quantity,
                            'purchase_price': purchase_price,
                            'purchase_date': purchase_date,
                            'market': market_code,
                            'currency': currency,
                            'notes': notes
                        }
                        st.rerun()

        # 確認視窗
        if 'confirm_add' in st.session_state and st.session_state.confirm_add is not None:
            data = st.session_state.confirm_add
            st.subheader("🔍 確認添加持倉")

            # 顯示確認資訊
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**代碼:** {data['symbol']}")
                st.write(f"**資產類別:** {data['asset_type']}")
                st.write(f"**數量:** {data['quantity']}")
            with col2:
                st.write(f"**購買價格:** {format_currency(data['purchase_price'], data['currency'])}")
                st.write(f"**購買日期:** {data['purchase_date']}")
                st.write(f"**市場:** {data['market']}")

            if data['notes']:
                st.write(f"**備註:** {data['notes']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 確定添加", use_container_width=True):
                    try:
                        with st.spinner("正在添加持倉..."):
                            self.pm.add_holding(
                                portfolio_id=st.session_state.portfolio_id,
                                symbol=data['symbol'],
                                asset_type=data['asset_type'],
                                quantity=data['quantity'],
                                purchase_price=data['purchase_price'],
                                purchase_date=pd.Timestamp(data['purchase_date']).to_pydatetime(),
                                market=data['market'],
                                currency=data['currency'],
                                notes=data['notes']
                            )
                            st.success(f"{data['symbol']} 成功添加！")
                            st.session_state.show_add_form = False
                            del st.session_state.confirm_add
                            st.rerun()
                    except Exception as e:
                        st.error(f"添加持倉時出錯: {e}")

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    del st.session_state.confirm_add
                    st.rerun()

    def render_holdings_table(self, analysis: Dict):
        """Render holdings table with edit capability"""
        holdings = analysis["holdings"]

        if not holdings:
            st.info("此投資組合中沒有持倉")
            return

        # Prepare dataframe
        data = []
        for i, holding in enumerate(holdings):
            currency = getattr(holding, 'currency', 'USD')
            data.append({
                "序號": i + 1,
                "代碼": holding.symbol,
                "資產類別": holding.asset_type,
                "貨幣": currency,
                "數量": f"{holding.quantity:.2f}",
                "購買價格": format_currency(holding.purchase_price, currency),
                "現價": format_currency(holding.current_price, currency),
                "成本基準": format_currency(holding.cost_basis, currency),
                "現值": format_currency(holding.current_value, currency),
                "未實現損益": format_currency(holding.unrealized_pl, currency),
                "回報%": format_percentage(holding.unrealized_return_pct)
            })

        import pandas as pd
        df = pd.DataFrame(data)

        # Style dataframe
        def color_return(val):
            try:
                num = float(val.replace("%", "").replace("+", ""))
                if num > 0:
                    return "color: #06D6A0"
                elif num < 0:
                    return "color: #EF476F"
                else:
                    return "color: #FFD166"
            except:
                return ""

        styled_df = df.style.map(color_return, subset=["回報%"])

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Edit/Adjust positions
        st.subheader("📝 調整持倉")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_index = st.selectbox(
                "選擇要調整的持倉",
                range(len(holdings)),
                format_func=lambda i: f"{holdings[i].symbol} (x{holdings[i].quantity:.2f})"
            )

        selected_holding = holdings[selected_index]

        with col2:
            action = st.radio("操作", ["減碼", "賣出全部"])

        with col3:
            if action == "減碼":
                adjust_quantity = st.number_input(
                    "減碼數量",
                    min_value=0.0,
                    max_value=selected_holding.quantity,
                    step=0.01,
                    value=0.0
                )
            else:
                adjust_quantity = selected_holding.quantity

        if st.button("執行調整", use_container_width=True):
            if adjust_quantity > 0:
                # 設定確認資料
                st.session_state.confirm_adjust = {
                    'holding_obj': selected_holding,
                    'adjust_quantity': adjust_quantity,
                    'action': action
                }
                st.rerun()
            else:
                st.warning("請輸入有效的調整數量")

        # 確認調整視窗
        if 'confirm_adjust' in st.session_state and st.session_state.confirm_adjust is not None:
            data = st.session_state.confirm_adjust
            holding = data['holding_obj']
            adjust_quantity = data['adjust_quantity']
            action = data['action']

            st.subheader("🔍 確認調整持倉")

            # 顯示確認資訊
            currency = getattr(holding, 'currency', 'USD')
            current_value = adjust_quantity * holding.current_price
            cost_sold = adjust_quantity * holding.purchase_price
            realized_pl = current_value - cost_sold

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**代碼:** {holding.symbol}")
                st.write(f"**操作:** {action}")
                st.write(f"**調整數量:** {adjust_quantity}")
            with col2:
                st.write(f"**現價:** {format_currency(holding.current_price, currency)}")
                st.write(f"**預計賣出價值:** {format_currency(current_value, currency)}")
                st.write(f"**預計已實現損益:** {format_currency(realized_pl, currency)}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 確定調整", use_container_width=True):
                    try:
                        with st.spinner("正在調整持倉..."):
                            # Find the actual holding ID from database
                            holdings_db = self.pm.db.get_holdings(st.session_state.portfolio_id)
                            holding_obj = next((h for h in holdings_db if h.symbol == holding.symbol), None)

                            if holding_obj:
                                self.pm.sell_position(st.session_state.portfolio_id, holding_obj.id, adjust_quantity)
                                st.success(f"已調整 {holding.symbol}!")
                                del st.session_state.confirm_adjust
                                st.rerun()
                    except Exception as e:
                        st.error(f"調整持倉時出錯: {e}")

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    del st.session_state.confirm_adjust
                    st.rerun()