"""Initialize sample portfolio data"""
from datetime import datetime, timedelta
import random
from backend.portfolio_manager import PortfolioManager
from database.db_manager import get_db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample portfolio with holdings"""
    
    pm = PortfolioManager()
    
    # Check if portfolio already exists
    existing_portfolios = pm.get_all_portfolios()
    if existing_portfolios:
        logger.info("Portfolio already exists. Skipping creation...")
        portfolio_id = existing_portfolios[0].id
        logger.info(f"Using existing portfolio (ID: {portfolio_id})")
    else:
        # Create portfolio
        portfolio = pm.create_portfolio(
            name="My Investment Portfolio 2024",
            description="Personal portfolio tracking US and Taiwan stocks"
        )
        # Get portfolio ID immediately while session is active
        portfolio_id = portfolio.id
        logger.info(f"Created portfolio: My Investment Portfolio 2024 (ID: {portfolio_id})")
        # Refresh portfolio to ensure we have the ID
        portfolio_id = pm.get_all_portfolios()[0].id
    
    # Sample holdings data
    sample_holdings = [
        # US Tech Stocks
        {
            "symbol": "AAPL",
            "asset_type": "股票 - 美股",
            "quantity": 10,
            "purchase_price": 150.0,
            "purchase_date": datetime(2024, 1, 15),
            "market": "US"
        },
        {
            "symbol": "MSFT",
            "asset_type": "股票 - 美股",
            "quantity": 5,
            "purchase_price": 350.0,
            "purchase_date": datetime(2024, 2, 1),
            "market": "US"
        },
        {
            "symbol": "NVDA",
            "asset_type": "股票 - 美股",
            "quantity": 2,
            "purchase_price": 700.0,
            "purchase_date": datetime(2024, 1, 20),
            "market": "US"
        },
        # US ETFs
        {
            "symbol": "VOO",
            "asset_type": "ETF - 美股",
            "quantity": 20,
            "purchase_price": 410.0,
            "purchase_date": datetime(2023, 12, 1),
            "market": "US"
        },
        {
            "symbol": "QQQ",
            "asset_type": "ETF - 美股",
            "quantity": 15,
            "purchase_price": 365.0,
            "purchase_date": datetime(2024, 1, 5),
            "market": "US"
        },
        # Taiwan Stocks
        {
            "symbol": "2330.TW",
            "asset_type": "股票 - 台股",
            "quantity": 100,
            "purchase_price": 600.0,
            "purchase_date": datetime(2024, 2, 15),
            "market": "TW"
        },
        {
            "symbol": "3008.TW",
            "asset_type": "股票 - 台股",
            "quantity": 100,
            "purchase_price": 300.0,
            "purchase_date": datetime(2024, 1, 10),
            "market": "TW"
        },
        # Taiwan ETF
        {
            "symbol": "0050.TW",
            "asset_type": "ETF - 台股",
            "quantity": 50,
            "purchase_price": 180.0,
            "purchase_date": datetime(2023, 11, 1),
            "market": "TW"
        },
    ]
    
    # Add holdings
    for holding_data in sample_holdings:
        try:
            pm.add_holding(
                portfolio_id=portfolio_id,
                symbol=holding_data["symbol"],
                asset_type=holding_data["asset_type"],
                quantity=holding_data["quantity"],
                purchase_price=holding_data["purchase_price"],
                purchase_date=holding_data["purchase_date"],
                market=holding_data["market"],
                notes=f"Sample holding - {holding_data['symbol']}"
            )
            logger.info(f"Added {holding_data['symbol']}: {holding_data['quantity']} units @ ${holding_data['purchase_price']}")
        except Exception as e:
            logger.error(f"Error adding {holding_data['symbol']}: {e}")
    
    logger.info("Sample data created successfully!")
    
    # Display portfolio summary
    try:
        analysis = pm.get_portfolio_analysis(portfolio_id)
        print("\n" + "="*60)
        print("📊 PORTFOLIO SUMMARY")
        print("="*60)
        
        metrics = analysis["metrics"]
        print(f"\nTotal Value: ${metrics.total_value:,.2f}")
        print(f"Total Cost:  ${metrics.total_cost:,.2f}")
        print(f"Total P&L:   ${metrics.total_pl:,.2f} ({metrics.return_percentage:.2f}%)")
        print(f"\nRealised P&L:   ${metrics.total_realized_pl:,.2f}")
        print(f"Unrealised P&L: ${metrics.total_unrealized_pl:,.2f}")
        
        print(f"\n資產分布:")
        for asset_type, percentage in analysis["distribution"].items():
            print(f"  - {asset_type}: {percentage:.2f}%")
        
        print(f"\n市場敞口:")
        print(f"  - 美股: {analysis['market_exposure']['US']:.2f}%")
        print(f"  - 台股: {analysis['market_exposure']['TW']:.2f}%")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")

if __name__ == "__main__":
    create_sample_data()
