"""Service container for dependency injection"""
from backend.portfolio_manager import PortfolioManager
from ui.metrics import MetricsRenderer
from ui.charts import ChartsRenderer
from ui.forms import FormsRenderer

class ServiceContainer:
    """Container for managing application services and dependencies"""

    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register(self, service_name: str, service_class, singleton: bool = True):
        """Register a service"""
        self._services[service_name] = (service_class, singleton)

    def get(self, service_name: str):
        """Get a service instance"""
        if service_name not in self._services:
            raise ValueError(f"Service {service_name} not registered")

        service_class, singleton = self._services[service_name]

        if singleton:
            if service_name not in self._singletons:
                self._singletons[service_name] = service_class()
            return self._singletons[service_name]
        else:
            return service_class()

# Global service container
container = ServiceContainer()

# Register services
container.register("portfolio_manager", PortfolioManager)
container.register("metrics_renderer", MetricsRenderer)
container.register("charts_renderer", ChartsRenderer)
container.register("forms_renderer", FormsRenderer)