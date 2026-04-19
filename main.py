"""Main Streamlit Dashboard Application"""
import logging
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List
import config
from backend.portfolio_manager import PortfolioManager
from backend.data_fetcher import DataFetcher
from utils.helpers import format_currency, format_percentage, get_change_badge, format_date

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🔥 財富自由儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)

class DashboardApp:
    """Main dashboard application"""
    
    def __init__(self):
        self.pm = PortfolioManager()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state"""
        if "portfolio_id" not in st.session_state:
            portfolios = self.pm.get_all_portfolios()
            if portfolios:
                st.session_state.portfolio_id = portfolios[0].id
            else:
                st.session_state.portfolio_id = None
        
        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = None
        
        if "view_mode" not in st.session_state:
            st.session_state.view_mode = "所有投資組合"
    
    def render_sidebar(self):
        """Render sidebar for portfolio selection"""
        with st.sidebar:
            st.title("🔥 投資組合控制")
            
            # View mode selection
            view_mode = st.radio("選擇檢視模式", ["所有投資組合", "個別投資組合"])
            st.session_state.view_mode = view_mode
            
            # Portfolio selection (only for individual mode)
            if view_mode == "個別投資組合":
                portfolios = self.pm.get_all_portfolios()
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
                            self.pm.refresh_prices(st.session_state.portfolio_id)
                            st.session_state.last_refresh = datetime.now()
                            st.success("價格已更新！")
                    elif view_mode == "所有投資組合":
                        with st.spinner("正在更新全部投資組合..."):
                            for portfolio in self.pm.get_all_portfolios():
                                self.pm.refresh_prices(portfolio.id)
                            st.session_state.last_refresh = datetime.now()
                            st.success("全部價格已更新！")
            
            with col2:
                if st.button("➕ 添加持倉", use_container_width=True):
                    if view_mode == "個別投資組合":
                        st.session_state.show_add_form = True
                    else:
                        st.warning("請切換到個別投資組合模式")
            
            st.divider()
            
            # Last refresh info
            if st.session_state.last_refresh:
                st.info(f"最後刷新：{format_date(st.session_state.last_refresh, '%Y-%m-%d %H:%M')}")
            
            st.divider()
            
            # Settings section
            st.subheader("⚙️ 設定")
            if st.button("建立新投資組合"):
                st.session_state.show_portfolio_form = True
    
    def render_metrics(self, analysis: Dict, is_all_portfolios: bool = False):
        """Render key metrics"""
        if is_all_portfolios:
            # Show combined metrics for all portfolios
            st.subheader("📊 所有投資組合概覽")
            
            us_metrics = analysis.get("us_metrics")
            tw_metrics = analysis.get("tw_metrics")
            
            # Get previous day data for delta calculations
            prev_day_data = self._get_previous_day_metrics()
            
            # 美股總價值
            if us_metrics:
                col1, col2, col3, col4 = st.columns(4)
                us_total_pl = us_metrics.total_unrealized_pl + us_metrics.total_realized_pl
                us_return_percentage = (us_total_pl / us_metrics.total_cost * 100) if us_metrics.total_cost != 0 else 0
                
                # Calculate deltas
                us_value_delta = self._calculate_delta(us_metrics.total_value, prev_day_data.get('us_total_value'))
                us_cost_delta = self._calculate_delta(us_metrics.total_cost, prev_day_data.get('us_total_cost'))
                us_unrealized_pl_delta = self._calculate_delta(us_metrics.total_unrealized_pl, prev_day_data.get('us_unrealized_pl'))
                us_realized_pl_delta = self._calculate_delta(us_metrics.total_realized_pl, prev_day_data.get('us_realized_pl'))
                us_total_pl_delta = self._calculate_delta(us_total_pl, prev_day_data.get('us_total_pl'))
                us_return_pct_delta = self._calculate_delta(us_return_percentage, prev_day_data.get('us_return_percentage'))
                    
                with col1:
                    st.metric(
                        "🇺🇸 美股總價值 (USD)",
                        format_currency(us_metrics.total_value, "USD"),
                        delta=format_currency(us_value_delta, "USD") if us_value_delta != 0 else None
                    )
                with col2:
                    st.metric(
                        "美股成本",
                        format_currency(us_metrics.total_cost, "USD"),
                        delta=format_currency(us_cost_delta, "USD") if us_cost_delta != 0 else None
                    )
                with col3:
                    st.metric(
                        "美股未實現損益 (USD)",
                        format_currency(us_metrics.total_unrealized_pl, "USD"),
                        delta=format_currency(us_unrealized_pl_delta, "USD") if us_unrealized_pl_delta != 0 else None
                    )
                with col4:
                    st.metric(
                        "美股已實現損益 (USD)",
                        format_currency(us_metrics.total_realized_pl, "USD"),
                        delta=format_currency(us_realized_pl_delta, "USD") if us_realized_pl_delta != 0 else None
                    )
                
                col5, col6 = st.columns(2)
                with col5:
                    st.metric(
                        "總損益 (USD)", 
                        format_currency(us_total_pl, "USD"),
                        delta=format_currency(us_total_pl_delta, "USD") if us_total_pl_delta != 0 else None
                    )
                
                with col6:
                    st.metric(
                        "報酬率", 
                        f"{us_return_percentage:+.2f}%",
                        delta=f"{us_return_pct_delta:+.2f}%" if us_return_pct_delta != 0 else None
                    )

            st.divider()
            
            # 台股總價值
            if tw_metrics:
                col1, col2, col3, col4 = st.columns(4)
                tw_total_pl = tw_metrics.total_unrealized_pl + tw_metrics.total_realized_pl
                tw_return_percentage = (tw_total_pl / tw_metrics.total_cost * 100) if tw_metrics.total_cost != 0 else 0
                
                # Calculate deltas
                tw_value_delta = self._calculate_delta(tw_metrics.total_value, prev_day_data.get('tw_total_value'))
                tw_cost_delta = self._calculate_delta(tw_metrics.total_cost, prev_day_data.get('tw_total_cost'))
                tw_unrealized_pl_delta = self._calculate_delta(tw_metrics.total_unrealized_pl, prev_day_data.get('tw_unrealized_pl'))
                tw_realized_pl_delta = self._calculate_delta(tw_metrics.total_realized_pl, prev_day_data.get('tw_realized_pl'))
                tw_total_pl_delta = self._calculate_delta(tw_total_pl, prev_day_data.get('tw_total_pl'))
                tw_return_pct_delta = self._calculate_delta(tw_return_percentage, prev_day_data.get('tw_return_percentage'))
                    
                with col1:
                    st.metric(
                        "🇹🇼 台股總價值 (NTD)",
                        format_currency(tw_metrics.total_value, "NTD"),
                        delta=format_currency(tw_value_delta, "NTD") if tw_value_delta != 0 else None
                    )
                with col2:
                    st.metric(
                        "台股成本",
                        format_currency(tw_metrics.total_cost, "NTD"),
                        delta=format_currency(tw_cost_delta, "NTD") if tw_cost_delta != 0 else None
                    )
                with col3:
                    st.metric(
                        "台股未實現損益 (NTD)",
                        format_currency(tw_metrics.total_unrealized_pl, "NTD"),
                        delta=format_currency(tw_unrealized_pl_delta, "NTD") if tw_unrealized_pl_delta != 0 else None
                    )
                with col4:
                    st.metric(
                        "台股已實現損益 (NTD)",
                        format_currency(tw_realized_pl_delta, "NTD"),
                        delta=format_currency(tw_realized_pl_delta, "NTD") if tw_realized_pl_delta != 0 else None
                    )
                
                col5, col6 = st.columns(2)
                with col5:
                    st.metric(
                        "總損益 (NTD)", 
                        format_currency(tw_total_pl, "NTD"),
                        delta=format_currency(tw_total_pl_delta, "NTD") if tw_total_pl_delta != 0 else None
                    )
                
                with col6:
                    st.metric(
                        "報酬率", 
                        f"{tw_return_percentage:+.2f}%",
                        delta=f"{tw_return_pct_delta:+.2f}%" if tw_return_pct_delta != 0 else None
                    )

        else:
            # Individual portfolio metrics - detect currency from holdings
            metrics = analysis["metrics"]
            holdings = analysis.get("holdings", [])
            
            # Determine primary currency
            currencies = set(getattr(h, 'currency', 'USD') for h in holdings)
            primary_currency = list(currencies)[0] if currencies else 'USD'
            
            st.subheader(f"📊 投資組合概覽 ({primary_currency})")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "總價值",
                    format_currency(metrics.total_value, primary_currency),
                    delta=format_currency(metrics.total_pl, primary_currency)
                )
            
            with col2:
                st.metric(
                    "總成本",
                    format_currency(metrics.total_cost, primary_currency)
                )
            
            with col3:
                st.metric("未實現損益", format_currency(metrics.total_unrealized_pl, primary_currency))
            
            with col4:
                st.metric("已實現損益", format_currency(metrics.total_realized_pl, primary_currency))
            
            # Additional row for total return and percentage
            total_pl = metrics.total_unrealized_pl + metrics.total_realized_pl
            return_percentage = (total_pl / metrics.total_cost * 100) if metrics.total_cost != 0 else 0
            
            col5, col6 = st.columns(2)
            with col5:
                st.metric("總報酬", format_currency(total_pl, primary_currency))
            with col6:
                st.metric("報酬率", f"{return_percentage:+.2f}%")

    def render_distribution_chart(self, analysis: Dict):
        """Render asset distribution pie chart and holdings breakdown table"""
        distribution = analysis["distribution"]
        holdings = analysis.get("holdings", [])

        if not distribution:
            st.warning("沒有持倉可顯示")
            return

        # Pie chart section
        col1, col2 = st.columns([1, 2])  # Pie chart takes 1/3, table takes 2/3

        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=list(distribution.keys()),
                values=list(distribution.values()),
                hovertemplate="<b>%{label}</b><br>%{value:.2f}%<extra></extra>"
            )])

            fig.update_layout(
                height=400,
                showlegend=True,
                template="plotly_dark",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.subheader("按資產類別分布")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Create holdings breakdown table
            if holdings:
                # Calculate percentage for each holding
                total_value = sum(h.current_value for h in holdings)

                holdings_data = []
                for holding in holdings:
                    percentage = (holding.current_value / total_value * 100) if total_value > 0 else 0
                    holdings_data.append({
                        "代碼": holding.symbol,
                        "市值": f"{holding.current_value:,.0f}",
                        "占比": f"{percentage:.2f}%"
                    })

                # Sort by percentage descending
                holdings_data.sort(key=lambda x: float(x["占比"].rstrip("%")), reverse=True)

                # Create DataFrame and display
                df = pd.DataFrame(holdings_data)

                st.subheader("各標的占比明細")

                # Style the dataframe
                def highlight_percentage(val):
                    try:
                        num = float(val.rstrip("%"))
                        if num >= 20:
                            return "background-color: #e6f7ff; color: #0066cc; font-weight: bold"
                        elif num >= 10:
                            return "background-color: #f0f8ff; color: #004499"
                        else:
                            return ""
                    except:
                        return ""

                styled_df = df.style.map(highlight_percentage, subset=["占比"])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "代碼": st.column_config.TextColumn("代碼", width="medium"),
                        "市值": st.column_config.TextColumn("市值", width="medium"),
                        "占比": st.column_config.TextColumn("占比", width="small")
                    }
                )
            else:
                st.info("沒有持倉數據可顯示")
    
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
            try:
                if adjust_quantity > 0:
                    with st.spinner("正在調整持倉..."):
                        # Find the actual holding ID from database
                        holdings_db = self.pm.db.get_holdings(st.session_state.portfolio_id)
                        holding_obj = next((h for h in holdings_db if h.symbol == selected_holding.symbol), None)
                        
                        if holding_obj:
                            self.pm.sell_position(st.session_state.portfolio_id, holding_obj.id, adjust_quantity)
                            st.success(f"已調整 {selected_holding.symbol}!")
                            st.rerun()
            except Exception as e:
                st.error(f"調整持倉時出錯: {e}")
    
    def render_daily_trend_chart(self, portfolio_id: int, analysis: Dict):
        """Render daily portfolio value trend chart"""
        import plotly.graph_objects as go
        from datetime import datetime
        
        try:
            # Time window options (buttons rendered below chart)
            window_options = [
                ("近7天", 7, "7d"),
                ("30天", 30, "30d"),
                ("半年", 182, "6mo"),
                ("1年", 365, "1y"),
                ("兩年", 730, "2y"),
            ]
            if "trend_window" not in st.session_state:
                st.session_state.trend_window = "半年"
            selected_window = next((item for item in window_options if item[0] == st.session_state.trend_window), window_options[2])
            selected_label, selected_days, selected_period = selected_window
            
            end_date = datetime.today()
            start_date = end_date - timedelta(days=selected_days)
            
            # Get performance history
            performance_history = self.pm.get_performance_history(portfolio_id)
            
            def normalize(values):
                if not values:
                    return []
                base = values[0] if values[0] != 0 else 1
                return [(v / base) * 100 for v in values]
            
            if performance_history and len(performance_history) > 0:
                filtered = [p for p in performance_history if p.snapshot_date >= start_date]
                if len(filtered) < 2:
                    filtered = performance_history[-selected_days:] if len(performance_history) >= 2 else performance_history
                dates = [p.snapshot_date for p in filtered]
                values = [p.total_value for p in filtered]
                using_mock = False
            else:
                using_mock = True
                st.caption("📈 使用預設 mock 數據顯示趨勢圖。")
                dates = [end_date - timedelta(days=selected_days - 1 - i) for i in range(selected_days)]
                values = [100000 + i * 600 + ((-1) ** i) * 200 for i in range(selected_days)]
            
            # Aggregate data for longer time windows to reduce noise
            if selected_days > 30:  # For 半年, 1年, 2年
                import pandas as pd
                df = pd.DataFrame({'date': dates, 'value': values})
                df['date'] = pd.to_datetime(df['date'])
                
                # Group by week for better visualization
                df['week'] = df['date'].dt.to_period('W').dt.start_time
                aggregated = df.groupby('week')['value'].mean().reset_index()
                dates = aggregated['week'].tolist()
                values = aggregated['value'].tolist()
            
            # Summary metrics above chart
            col1, col2, col3 = st.columns(3)
            current_value = values[-1]
            previous_value = values[-2] if len(values) > 1 else values[-1]
            daily_change = current_value - previous_value
            daily_pct = (daily_change / previous_value * 100) if previous_value != 0 else 0
            
            with col1:
                st.metric(
                    "當前投資組合價值",
                    f"${current_value:,.0f}",
                    delta=f"${daily_change:,.0f}" if daily_change != 0 else None
                )
            
            with col2:
                daily_color = "🟢" if daily_change >= 0 else "🔴"
                st.metric(
                    "每日變動 (%)",
                    f"{daily_color} {daily_pct:+.2f}%",
                    delta=None
                )
            
            with col3:
                first_value = values[0]
                total_change = current_value - first_value
                total_pct = (total_change / first_value * 100) if first_value != 0 else 0
                st.metric(
                    "期間回報 (%)",
                    f"{total_pct:+.2f}%",
                    delta=f"${total_change:,.0f}"
                )
            
            # Benchmark data fetcher
            def build_benchmark_series(symbol: str, period: str, target_dates: List[datetime], aggregate_long_periods: bool = False):
                df = DataFetcher.get_index_historical(symbol, period=period)
                if df is None or df.empty:
                    base_values = [100 + i * 0.12 for i in range(len(target_dates))]
                    if aggregate_long_periods:
                        import pandas as pd
                        df_mock = pd.DataFrame({'date': target_dates, 'value': base_values})
                        df_mock['date'] = pd.to_datetime(df_mock['date'])
                        df_mock['week'] = df_mock['date'].dt.to_period('W').dt.start_time
                        aggregated = df_mock.groupby('week')['value'].mean().reset_index()
                        return aggregated['value'].tolist()
                    return base_values
                
                close_values = df["close"].tolist()
                if len(close_values) < len(target_dates):
                    base_values = [100 + i * 0.12 for i in range(len(target_dates))]
                    if aggregate_long_periods:
                        import pandas as pd
                        df_mock = pd.DataFrame({'date': target_dates, 'value': base_values})
                        df_mock['date'] = pd.to_datetime(df_mock['date'])
                        df_mock['week'] = df_mock['date'].dt.to_period('W').dt.start_time
                        aggregated = df_mock.groupby('week')['value'].mean().reset_index()
                        return aggregated['value'].tolist()
                    return base_values
                
                normalized = normalize(close_values[-len(target_dates):])
                
                if aggregate_long_periods:
                    import pandas as pd
                    df_bench = pd.DataFrame({'date': target_dates, 'value': normalized})
                    df_bench['date'] = pd.to_datetime(df_bench['date'])
                    df_bench['week'] = df_bench['date'].dt.to_period('W').dt.start_time
                    aggregated = df_bench.groupby('week')['value'].mean().reset_index()
                    return aggregated['value'].tolist()
                
                return normalized
            
            # Use same dates for benchmark lines where possible
            portfolio_indexed = normalize(values)
            aggregate_needed = selected_days > 30
            if aggregate_needed:
                # For aggregated data, we need to adjust benchmark dates to match
                aggregated_dates = dates
                us_indexed = build_benchmark_series("^GSPC", selected_period, aggregated_dates, aggregate_needed)
                tw_indexed = build_benchmark_series("^TWII", selected_period, aggregated_dates, aggregate_needed)
            else:
                us_indexed = build_benchmark_series("^GSPC", selected_period, dates, aggregate_needed)
                tw_indexed = build_benchmark_series("^TWII", selected_period, dates, aggregate_needed)
            
            # Create figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_indexed,
                mode='lines',
                name='投資組合',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=6)
            ))
            fig.add_trace(go.Scatter(
                x=dates,
                y=us_indexed,
                mode='lines',
                name='美股大盤 (S&P 500)',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=dates,
                y=tw_indexed,
                mode='lines',
                name='台股大盤 (加權指數)',
                line=dict(color='#2ca02c', width=2, dash='dot')
            ))
            
            fig.update_layout(
                title=f'📈 投資組合與台美大盤趨勢比較 ({selected_label})',
                xaxis_title='日期',
                yaxis_title='相對基準值 (100=起點)',
                template='plotly_white',
                hovermode='x unified',
                legend=dict(title='趨勢比較', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=450,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, width='stretch')
            
            # Time window buttons below chart
            cols = st.columns(len(window_options))
            button_clicked = False
            for col, (label, _, _) in zip(cols, window_options):
                if col.button(label, key=f"trend_window_{label}"):
                    st.session_state.trend_window = label
                    button_clicked = True
            if button_clicked:
                st.rerun()
        except Exception as e:
            st.error(f"Error rendering trend chart: {str(e)}")
            logger.exception("Error in render_daily_trend_chart")
    
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
                        try:
                            with st.spinner("正在添加持倉..."):
                                self.pm.add_holding(
                                    portfolio_id=st.session_state.portfolio_id,
                                    symbol=symbol,
                                    asset_type=asset_type,
                                    quantity=quantity,
                                    purchase_price=purchase_price,
                                    purchase_date=pd.Timestamp(purchase_date).to_pydatetime(),
                                    market=market_code,
                                    currency=currency,
                                    notes=notes
                                )
                                st.success(f"{symbol} 成功添加！")
                                st.session_state.show_add_form = False
                                st.rerun()
                        except Exception as e:
                            st.error(f"添加持倉時出錯: {e}")
    
    def _get_previous_day_metrics(self):
        """Get previous day metrics for all portfolios combined"""
        try:
            portfolios = self.pm.get_all_portfolios()
            prev_data = {}
            
            for portfolio in portfolios:
                # Get the most recent performance snapshots (last 2 days)
                history = self.pm.get_performance_history(portfolio.id)
                if len(history) >= 2:
                    # Get yesterday's data (second most recent)
                    yesterday_snapshot = history[-2]
                    
                    # For now, we'll use the total values and try to estimate US/TW split
                    # This is a simplification - ideally we'd store separate US/TW snapshots
                    total_prev_value = yesterday_snapshot.total_value
                    total_prev_cost = yesterday_snapshot.total_cost
                    
                    # Get current holdings to estimate the split ratio
                    current_analysis = self.pm.get_portfolio_analysis(portfolio.id)
                    current_holdings = current_analysis.get('holdings', [])
                    
                    us_holdings = [h for h in current_holdings if getattr(h, 'currency', 'USD') == 'USD']
                    tw_holdings = [h for h in current_holdings if getattr(h, 'currency', 'NTD') == 'NTD']
                    
                    # Calculate current split ratios
                    current_us_value = sum(h.current_value for h in us_holdings)
                    current_tw_value = sum(h.current_value for h in tw_holdings)
                    total_current_value = current_us_value + current_tw_value
                    
                    if total_current_value > 0:
                        us_ratio = current_us_value / total_current_value
                        tw_ratio = current_tw_value / total_current_value
                        
                        # Apply ratios to previous total values
                        prev_data['us_total_value'] = prev_data.get('us_total_value', 0) + (total_prev_value * us_ratio)
                        prev_data['tw_total_value'] = prev_data.get('tw_total_value', 0) + (total_prev_value * tw_ratio)
                        prev_data['us_total_cost'] = prev_data.get('us_total_cost', 0) + (total_prev_cost * us_ratio)
                        prev_data['tw_total_cost'] = prev_data.get('tw_total_cost', 0) + (total_prev_cost * tw_ratio)
                        
                        # For P&L, we'll use the same ratios (simplification)
                        prev_data['us_unrealized_pl'] = prev_data.get('us_unrealized_pl', 0) + (yesterday_snapshot.total_unrealized_pl * us_ratio)
                        prev_data['tw_unrealized_pl'] = prev_data.get('tw_unrealized_pl', 0) + (yesterday_snapshot.total_unrealized_pl * tw_ratio)
                        prev_data['us_realized_pl'] = prev_data.get('us_realized_pl', 0) + (yesterday_snapshot.total_realized_pl * us_ratio)
                        prev_data['tw_realized_pl'] = prev_data.get('tw_realized_pl', 0) + (yesterday_snapshot.total_realized_pl * tw_ratio)
            
            # Calculate total P&L and return percentages
            if prev_data.get('us_total_cost', 0) > 0:
                prev_data['us_total_pl'] = prev_data['us_unrealized_pl'] + prev_data['us_realized_pl']
                prev_data['us_return_percentage'] = (prev_data['us_total_pl'] / prev_data['us_total_cost'] * 100)
            
            if prev_data.get('tw_total_cost', 0) > 0:
                prev_data['tw_total_pl'] = prev_data['tw_unrealized_pl'] + prev_data['tw_realized_pl']
                prev_data['tw_return_percentage'] = (prev_data['tw_total_pl'] / prev_data['tw_total_cost'] * 100)
            
            return prev_data
            
        except Exception as e:
            logger.error(f"Error getting previous day metrics: {e}")
            return {}
    
    def _calculate_delta(self, current_value, previous_value):
        """Calculate the delta between current and previous values"""
        if previous_value is None or previous_value == 0:
            return 0
        return current_value - previous_value
    
    def run(self):
        """Run the dashboard"""
        st.title("🔥 火焰投資組合儀表板")
        
        # Render sidebar
        self.render_sidebar()
        
        # Main content
        view_mode = st.session_state.get("view_mode", "所有投資組合")
        
        if view_mode == "所有投資組合":
            # Show all portfolios combined
            try:
                analysis = self.pm.get_all_portfolios_analysis()
                
                if analysis["total_portfolios"] == 0:
                    st.warning("找不到投資組合。請先建立一個。")
                    if st.button("建立第一個投資組合"):
                        st.session_state.show_portfolio_form = True
                else:
                    self.render_metrics(analysis, is_all_portfolios=True)
                    st.divider()
                    
            except Exception as e:
                st.error(f"載入投資組合時出錯: {e}")
        
        else:
            # Show individual portfolio
            if not st.session_state.portfolio_id:
                st.warning("找不到投資組合。請先建立一個。")
                
                if st.button("建立第一個投資組合"):
                    st.session_state.show_portfolio_form = True
            else:
                # Get portfolio data
                try:
                    analysis = self.pm.get_portfolio_analysis(st.session_state.portfolio_id)
                    
                    # Render main dashboard
                    self.render_metrics(analysis, is_all_portfolios=False)
                    
                    st.divider()

                    # Daily trend chart
                    self.render_daily_trend_chart(st.session_state.portfolio_id, analysis)
                    
                    st.divider()
                    
                    # Distribution chart (full width)
                    self.render_distribution_chart(analysis)

                    st.divider()
                    
                    # Holdings table with edit capability
                    st.subheader("📋 持倉詳情")
                    self.render_holdings_table(analysis)
                    
                    st.divider()
                    
                    # Add holding form
                    self.render_add_holding_form()
                    
                except Exception as e:
                    st.error(f"載入投資組合時出錯: {e}")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
