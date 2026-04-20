"""Factory for creating UI renderers with dependency injection"""
from ui.metrics import MetricsRenderer
from ui.charts import ChartsRenderer
from ui.forms import FormsRenderer
from ui.portfolio import PortfolioRenderer
from core.container import container

class UIRendererFactory:
    """Factory for creating UI renderers"""

    @staticmethod
    def create_metrics_renderer() -> MetricsRenderer:
        """Create metrics renderer with injected dependencies"""
        pm = container.get("portfolio_manager")
        return MetricsRenderer(pm)

    @staticmethod
    def create_charts_renderer() -> ChartsRenderer:
        """Create charts renderer with injected dependencies"""
        pm = container.get("portfolio_manager")
        return ChartsRenderer(pm)

    @staticmethod
    def create_forms_renderer() -> FormsRenderer:
        """Create forms renderer with injected dependencies"""
        pm = container.get("portfolio_manager")
        return FormsRenderer(pm)

    @staticmethod
    def create_portfolio_renderer() -> PortfolioRenderer:
        """Create portfolio renderer with injected dependencies"""
        pm = container.get("portfolio_manager")
        return PortfolioRenderer(pm)

    @staticmethod
    def create_all_renderers():
        """Create all renderers at once"""
        return {
            "metrics": UIRendererFactory.create_metrics_renderer(),
            "charts": UIRendererFactory.create_charts_renderer(),
            "forms": UIRendererFactory.create_forms_renderer(),
            "portfolio": UIRendererFactory.create_portfolio_renderer()
        }