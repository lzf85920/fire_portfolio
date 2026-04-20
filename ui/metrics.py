"""Metrics UI components"""
import streamlit as st
from typing import Dict
from utils.helpers import format_currency

class MetricsRenderer:
    """Handles rendering of portfolio metrics"""

    def __init__(self, portfolio_manager=None):
        # Allow dependency injection
        self.pm = portfolio_manager

    def render_metrics(self, analysis: Dict, is_all_portfolios: bool = False):
        """Render key metrics"""
        if is_all_portfolios:
            self._render_all_portfolios_metrics(analysis)
        else:
            self._render_individual_portfolio_metrics(analysis)

    def _render_all_portfolios_metrics(self, analysis: Dict):
        """Render combined metrics for all portfolios"""
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
                    format_currency(tw_metrics.total_realized_pl, "NTD"),
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

    def _render_individual_portfolio_metrics(self, analysis: Dict):
        """Render metrics for individual portfolio"""
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

    def _get_previous_day_metrics(self):
        """Get previous day metrics for all portfolios combined"""
        try:
            from backend.portfolio_manager import PortfolioManager
            pm = PortfolioManager()
            portfolios = pm.get_all_portfolios()
            prev_data = {}

            for portfolio in portfolios:
                # Get the most recent performance snapshots (last 2 days)
                history = pm.get_performance_history(portfolio.id)
                if len(history) >= 2:
                    # Get yesterday's data (second most recent)
                    yesterday_snapshot = history[-2]

                    # For now, we'll use the total values and try to estimate US/TW split
                    # This is a simplification - ideally we'd store separate US/TW snapshots
                    total_prev_value = yesterday_snapshot.total_value
                    total_prev_cost = yesterday_snapshot.total_cost

                    # Get current holdings to estimate the split ratio
                    current_analysis = pm.get_portfolio_analysis(portfolio.id)
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting previous day metrics: {e}")
            return {}

    def _calculate_delta(self, current_value, previous_value):
        """Calculate the delta between current and previous values"""
        if previous_value is None or previous_value == 0:
            return 0
        return current_value - previous_value