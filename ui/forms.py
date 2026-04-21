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
                # Transaction type selection
                transaction_type = st.radio("交易類型", ["📊 購買持倉", "💰 現金入金", "📈 期權合約"], horizontal=True)
                is_deposit = "現金入金" in transaction_type
                is_option = "期權合約" in transaction_type

                # Market selection (only for positions and options)
                if not is_deposit:
                    market = st.radio("選擇市場", ["🇺🇸 美股 (USD)", "🇹🇼 台股 (NTD)"])
                    market_code = "US" if "美股" in market else "TW"
                    currency = "USD" if market_code == "US" else "NTD"
                else:
                    # For deposits, always US by default (user can choose)
                    market = st.radio("選擇幣種", ["🇺🇸 USD", "🇹🇼 NTD"])
                    market_code = "US" if "USD" in market else "TW"
                    currency = "USD" if market_code == "US" else "NTD"

                # Asset type and symbol
                col1, col2 = st.columns(2)

                with col1:
                    import config
                    if is_deposit:
                        asset_type = "現金"
                        st.text_input("資產類別", value="現金", disabled=True, key="asset_type_display")
                    elif is_option:
                        asset_type = "Option"
                        st.text_input("資產類別", value="期權 (Option)", disabled=True, key="asset_type_display")
                    else:
                        asset_type = st.selectbox("資產類別", config.ASSET_CLASSES, key="asset_type")

                with col2:
                    if is_deposit:
                        symbol = "CASH"
                        st.text_input("代碼", value=symbol, disabled=True, key="symbol")
                    elif is_option:
                        symbol = st.text_input("標的股票代碼 (例如: TSLA, 2330)", placeholder="TSLA", key="symbol")
                    else:
                        symbol = st.text_input("代碼 (例如: AAPL, 2330)", key="symbol")

                # Option-specific fields
                if is_option:
                    opt_col1, opt_col2 = st.columns(2)
                    with opt_col1:
                        option_type = st.selectbox("期權類型", ["CALL", "PUT"], key="option_type")
                    with opt_col2:
                        strike = st.number_input("行權價 (Strike)", min_value=0.0, step=0.01, key="strike")
                    
                    opt_col3, opt_col4 = st.columns(2)
                    with opt_col3:
                        expiration_date = st.date_input("到期日期", key="expiration_date")
                    with opt_col4:
                        option_quantity = st.number_input("合約數量 (1份=100股)", min_value=1, step=1, value=1, key="option_quantity")
                    
                    opt_col5, opt_col6 = st.columns(2)
                    with opt_col5:
                        premium = st.number_input("期權費 (每股價格)", min_value=0.0, step=0.01, key="premium")
                    with opt_col6:
                        # Display cost basis
                        cost = option_quantity * 100 * premium
                        st.text_input("成本基礎", value=f"{cost:,.2f}", disabled=True, key="cost_display")
                    
                    purchase_date = st.date_input("購買日期", key="purchase_date_opt")
                    notes = st.text_area("備註（可選）", placeholder="例如：CALL TSLA 330 @ 2026-03-20", key="notes_opt")
                else:
                    # Quantity and purchase price
                    col3, col4 = st.columns(2)

                    with col3:
                        if is_deposit:
                            quantity = st.number_input("入金金額", min_value=0.0, step=100.0, key="quantity")
                        else:
                            quantity = st.number_input("持倉數量", min_value=0.0, step=0.01, key="quantity")

                    with col4:
                        if is_deposit:
                            purchase_price = 1.0
                            st.text_input("金額倍數", value="1.00", disabled=True, key="purchase_price")
                        else:
                            purchase_price = st.number_input("購買價格", min_value=0.0, step=0.01, key="purchase_price")

                    # Purchase date
                    if is_deposit:
                        purchase_date = st.date_input("入金日期", key="purchase_date")
                        notes = st.text_area("入金備註（可選）", placeholder="例如：薪資轉入、獲利提取", key="notes")
                    else:
                        purchase_date = st.date_input("購買日期", key="purchase_date")
                        notes = st.text_area("備註（可選）", key="notes")

                submitted = st.form_submit_button(
                    "確認入金" if is_deposit else ("確認添加期權" if is_option else "確認購買"), 
                    use_container_width=True
                )

                if submitted:
                    if is_option:
                        if not symbol or not strike or not premium or not option_quantity:
                            st.error("請填寫所有必填字段")
                        else:
                            st.session_state.confirm_add = {
                                'symbol': symbol,
                                'asset_type': "Option",
                                'option_type': option_type,
                                'strike': strike,
                                'expiration': expiration_date,
                                'quantity': option_quantity,
                                'premium': premium,
                                'purchase_date': purchase_date,
                                'market': market_code,
                                'currency': currency,
                                'notes': notes,
                                'is_option': True,
                                'is_deposit': False
                            }
                            st.rerun()
                    elif not symbol or (not purchase_price and not is_deposit) or not quantity:
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
                            'notes': notes,
                            'is_option': False,
                            'is_deposit': is_deposit
                        }
                        st.rerun()

        # 確認視窗
        if 'confirm_add' in st.session_state and st.session_state.confirm_add is not None:
            data = st.session_state.confirm_add
            is_deposit = data.get('is_deposit', False)
            is_option = data.get('is_option', False)
            
            if is_option:
                st.subheader("📈 確認添加期權合約")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**標的物:** {data['symbol']}")
                    st.write(f"**期權類型:** {data['option_type']}")
                    st.write(f"**行權價:** ${data['strike']:.2f}")
                with col2:
                    st.write(f"**到期日期:** {data['expiration']}")
                    st.write(f"**合約數量:** {data['quantity']}")
                    st.write(f"**期權費:** ${data['premium']:.2f} /股")
                
                cost_basis = data['quantity'] * 100 * data['premium']
                st.info(f"✅ 成本基礎: ${cost_basis:,.2f}")
                
                if data['notes']:
                    st.write(f"**備註:** {data['notes']}")
            else:
                st.subheader("💰 確認現金入金" if is_deposit else "🔍 確認購買持倉")

                # 顯示確認資訊
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**幣種:** {data['currency']}")
                    if not is_deposit:
                        st.write(f"**代碼:** {data['symbol']}")
                        st.write(f"**資產類別:** {data['asset_type']}")
                    st.write(f"**數量/金額:** {data['quantity']}")
                with col2:
                    if not is_deposit:
                        st.write(f"**購買價格:** {format_currency(data['purchase_price'], data['currency'])}")
                        st.write(f"**市場:** {data['market']}")
                    st.write(f"**交易日期:** {data['purchase_date']}")
                    if is_deposit:
                        st.info("✅ 現金入金不會影響投資回報率計算")

                if data['notes']:
                    st.write(f"**備註:** {data['notes']}")

            col1, col2 = st.columns(2)
            with col1:
                if is_option:
                    button_text = "✅ 確認添加期權"
                else:
                    button_text = "✅ 確認入金" if is_deposit else "✅ 確認購買"
                    
                if st.button(button_text, use_container_width=True):
                    try:
                        with st.spinner("正在處理..."):
                            if is_option:
                                # Handle option
                                from datetime import datetime
                                expiration = pd.Timestamp(data['expiration']).to_pydatetime()
                                self.pm.add_option(
                                    portfolio_id=st.session_state.portfolio_id,
                                    symbol=data['symbol'],
                                    option_type=data['option_type'],
                                    strike=data['strike'],
                                    expiration=expiration,
                                    quantity=data['quantity'],
                                    premium=data['premium'],
                                    market=data['market'],
                                    currency=data['currency'],
                                    notes=data['notes']
                                )
                                st.success(f"✅ {data['symbol']} {data['option_type']} 期權已添加！")
                            elif is_deposit:
                                # Handle deposit - adds to cash without affecting returns
                                self.pm.add_deposit(
                                    portfolio_id=st.session_state.portfolio_id,
                                    amount=data['quantity'],
                                    currency=data['currency'],
                                    deposit_date=pd.Timestamp(data['purchase_date']).to_pydatetime(),
                                    market=data['market'],
                                    notes=data['notes']
                                )
                                st.success(f"成功入金 {data['quantity']:.2f} {data['currency']}！")
                            else:
                                # Handle regular holding purchase
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
                                st.success(f"{data['symbol']} 成功購買！")
                            st.session_state.show_add_form = False
                            del st.session_state.confirm_add
                            st.rerun()
                    except Exception as e:
                        st.error(f"處理失敗: {e}")

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    del st.session_state.confirm_add
                    st.rerun()

    def render_holdings_table(self, analysis: Dict):
        """Render holdings table with edit capability"""
        holdings = analysis["holdings"]
        options = self.pm.get_options(st.session_state.portfolio_id)

        # Display holdings
        if holdings:
            st.write("**📊 股票和現金持倉**")
            # Prepare dataframe
            data = []
            for holding in holdings:
                currency = getattr(holding, 'currency', 'USD')
                data.append({
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

            # Sort by asset type first, then by symbol
            df_sorted = df.sort_values(by=["資產類別", "代碼"], ascending=[True, True])

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

            styled_df = df_sorted.style.map(color_return, subset=["回報%"])

            st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Display options
        if options:
            st.write("**📈 期權合約**")
            option_data = []
            for opt in options:
                option_data.append({
                    "標的物": opt.symbol,
                    "類型": opt.option_type,
                    "行權價": f"${opt.strike:.2f}",
                    "到期日": opt.expiration.strftime("%Y-%m-%d"),
                    "數量": f"{opt.quantity}份",
                    "期權費": f"${opt.premium:.2f}/股",
                    "現價": f"${opt.current_price:.2f}/股",
                    "成本": format_currency(opt.cost_basis, opt.currency),
                    "現值": format_currency(opt.current_value, opt.currency),
                    "損益": format_currency(opt.unrealized_pl, opt.currency),
                    "回報%": format_percentage(opt.unrealized_return_pct),
                    "狀態": opt.status
                })
            
            opt_df = pd.DataFrame(option_data)
            
            def color_option_return(val):
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
            
            styled_opt_df = opt_df.style.map(color_option_return, subset=["回報%"])
            st.dataframe(styled_opt_df, use_container_width=True, hide_index=True)
        
        if not holdings and not options:
            st.info("此投資組合中沒有持倉")
            return

        # Edit/Adjust positions
        st.subheader("📝 調整持倉")

        all_items = []
        all_items_info = []
        
        # Add holdings to list
        for i, holding in enumerate(holdings):
            all_items.append(f"{holding.symbol} (股票 x{holding.quantity:.2f})")
            all_items_info.append(('holding', holding, i))
        
        # Add options to list
        for i, opt in enumerate(options):
            all_items.append(f"{opt.symbol} {opt.option_type} ${opt.strike} (期權 x{opt.quantity}份)")
            all_items_info.append(('option', opt, i))

        if not all_items:
            st.info("沒有可調整的持倉")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_idx = st.selectbox("選擇要調整的持倉", range(len(all_items)), format_func=lambda i: all_items[i])

        item_type, selected_item, _ = all_items_info[selected_idx]

        with col2:
            if item_type == 'holding':
                action = st.radio("操作", ["減碼", "賣出全部"])
            else:
                action = st.radio("操作", ["平倉", "標記過期"])

        with col3:
            if item_type == 'holding':
                if action == "減碼":
                    adjust_quantity = st.number_input(
                        "減碼數量",
                        min_value=0.0,
                        max_value=selected_item.quantity,
                        step=0.01,
                        value=0.0
                    )
                else:
                    adjust_quantity = selected_item.quantity
            else:  # option
                if action == "平倉":
                    adjust_quantity = st.number_input(
                        "平倉價格 ($/股)",
                        min_value=0.0,
                        step=0.01,
                        value=selected_item.current_price
                    )
                else:
                    adjust_quantity = 0  # Not used for expire action

        if st.button("執行調整", use_container_width=True):
            if item_type == 'holding':
                if adjust_quantity > 0:
                    st.session_state.confirm_adjust = {
                        'item_type': 'holding',
                        'item': selected_item,
                        'adjust_quantity': adjust_quantity,
                        'action': action
                    }
                    st.rerun()
                else:
                    st.warning("請輸入有效的調整數量")
            else:  # option
                if action == "平倉":
                    if adjust_quantity >= 0:
                        st.session_state.confirm_adjust = {
                            'item_type': 'option',
                            'item': selected_item,
                            'adjust_quantity': adjust_quantity,
                            'action': action
                        }
                        st.rerun()
                    else:
                        st.warning("請輸入有效的平倉價格")
                else:  # expire
                    st.session_state.confirm_adjust = {
                        'item_type': 'option',
                        'item': selected_item,
                        'adjust_quantity': 0,
                        'action': action
                    }
                    st.rerun()

        # 確認調整視窗
        if 'confirm_adjust' in st.session_state and st.session_state.confirm_adjust is not None:
            data = st.session_state.confirm_adjust
            item_type = data['item_type']
            item = data['item']
            action = data['action']

            if item_type == 'holding':
                st.subheader("🔍 確認調整持倉")
                currency = getattr(item, 'currency', 'USD')
                adjust_quantity = data['adjust_quantity']
                current_value = adjust_quantity * item.current_price
                cost_sold = adjust_quantity * item.purchase_price
                realized_pl = current_value - cost_sold

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**代碼:** {item.symbol}")
                    st.write(f"**操作:** {action}")
                    st.write(f"**調整數量:** {adjust_quantity}")
                with col2:
                    st.write(f"**現價:** {format_currency(item.current_price, currency)}")
                    st.write(f"**預計賣出價值:** {format_currency(current_value, currency)}")
                    st.write(f"**預計已實現損益:** {format_currency(realized_pl, currency)}")
            else:  # option
                st.subheader("📈 確認調整期權")
                if action == "平倉":
                    close_price = data['adjust_quantity']
                    current_value_after = item.quantity * 100 * close_price
                    realized_pl = current_value_after - item.cost_basis
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**標的物:** {item.symbol}")
                        st.write(f"**期權類型:** {item.option_type}")
                        st.write(f"**行權價:** ${item.strike:.2f}")
                    with col2:
                        st.write(f"**操作:** 平倉")
                        st.write(f"**平倉價格:** ${close_price:.2f}/股")
                        st.write(f"**預計損益:** {format_currency(realized_pl, item.currency)}")
                else:  # expire
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**標的物:** {item.symbol}")
                        st.write(f"**期權類型:** {item.option_type}")
                        st.write(f"**行權價:** ${item.strike:.2f}")
                    with col2:
                        st.write(f"**操作:** 標記為過期")
                        st.write(f"**到期日:** {item.expiration.strftime('%Y-%m-%d')}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 確定調整", use_container_width=True):
                    try:
                        with st.spinner("正在調整..."):
                            if item_type == 'holding':
                                # Find the actual holding ID from database
                                holdings_db = self.pm.db.get_holdings(st.session_state.portfolio_id)
                                holding_obj = next((h for h in holdings_db if h.symbol == item.symbol), None)

                                if holding_obj:
                                    self.pm.sell_position(st.session_state.portfolio_id, holding_obj.id, data['adjust_quantity'])
                                    st.success(f"已調整 {item.symbol}!")
                            else:  # option
                                if action == "平倉":
                                    self.pm.close_option(item.id, data['adjust_quantity'])
                                    st.success(f"已平倉 {item.symbol} {item.option_type} {item.strike}!")
                                else:  # expire
                                    self.pm.expire_option(item.id)
                                    st.success(f"已標記 {item.symbol} {item.option_type} {item.strike} 為過期!")
                            
                            del st.session_state.confirm_adjust
                            st.rerun()
                    except Exception as e:
                        st.error(f"調整失敗: {e}")

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    del st.session_state.confirm_adjust
                    st.rerun()