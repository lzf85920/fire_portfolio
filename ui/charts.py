"""Charts and visualizations UI components"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List
from backend.portfolio_manager import PortfolioManager
from backend.data_fetcher import DataFetcher

class ChartsRenderer:
    """Handles rendering of charts and visualizations"""

    def __init__(self, portfolio_manager=None):
        # Allow dependency injection
        self.pm = portfolio_manager or PortfolioManager()

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
                import pandas as pd
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
                        "代碼": st.column_config.TextColumn("代碼", width="small"),
                        "市值": st.column_config.TextColumn("市值", width="small"),
                        "占比": st.column_config.TextColumn("占比", width="small")
                    }
                )
            else:
                st.info("沒有持倉數據可顯示")

    def render_daily_trend_chart(self, portfolio_id: int, analysis: Dict):
        """Render daily portfolio value trend chart"""
        import plotly.graph_objects as go
        from datetime import datetime, timedelta

        try:
            # Time window options (buttons rendered below chart)
            current_year = datetime.now().year
            days_this_year = (datetime.now() - datetime(current_year, 1, 1)).days + 1  # +1 to include today
            window_options = [
                ("近7天", 7, "7d"),
                ("30天", 30, "30d"),
                ("半年", 182, "6mo"),
                ("近一年", days_this_year, "ytd"),
                ("1年", 365, "1y"),
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
                sign = "+" if daily_change >= 0 else "-"
                abs_change = abs(daily_change)
                abs_pct = abs(daily_pct)
                st.metric(
                    "每日變動",
                    f"{sign}${abs_change:,.0f} ({abs_pct:.2f}%)",
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
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
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
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error in render_daily_trend_chart")