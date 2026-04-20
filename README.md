# 🔥 Fire Portfolio Dashboard

Interactive investment performance tracking dashboard for US and Taiwan stocks/ETFs.

## Features

### Core Features
- 📊 **Asset Distribution** - View portfolio composition by asset class
- 💰 **Performance Metrics** - Track total P&L, realized/unrealized gains
- 📋 **Holdings List** - Detailed view of each position with current performance
- 🔄 **Price Updates** - Daily refresh of stock prices from Yahoo Finance

### Advanced Features
- 🚀 **Top/Worst Performers** - Identify best and worst performing holdings
- 🌍 **Market Exposure** - US vs Taiwan market allocation analysis
- 📈 **Multiple Portfolios** - Manage and compare different portfolios
- 💾 **Price History** - Track historical prices for analysis

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python with modular architecture
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Data Sources**: 
  - `yfinance` - US stocks and ETFs
  - `twstock` - Taiwan stocks (optional)
  - TDX API support (ready for integration)

## Project Structure

```
fire_portfolio/
├── main.py                      # Streamlit app entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── init_sample_data.py          # Sample data initialization
│
├── backend/
│   ├── models.py               # Data models
│   ├── data_fetcher.py         # Stock price fetching
│   ├── calculator.py           # Performance calculations
│   └── portfolio_manager.py    # Portfolio operations
│
├── database/
│   ├── schema.py               # Database schema
│   └── db_manager.py           # Database operations
│
├── utils/
│   └── helpers.py              # Utility functions
│
└── data/
    └── portfolio.db            # SQLite database
```

## Installation

### 1. Clone/Download the Project
```bash
cd fire_portfolio
```

### 2. Create and Activate a Virtual Environment (Recommended)
Use a virtual environment so your project dependencies stay isolated from system Python.

```bash
python -m venv venv
```

Activate the environment:

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Mac/Linux:
  ```bash
  source venv/bin/activate
  ```

After activation, you should see `(venv)` at the start of your shell prompt.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Sample Data
```bash
python init_sample_data.py
```

This creates:
- Sample portfolio with US and Taiwan holdings
- Initial price data from Yahoo Finance
- Display summary of sample portfolio

### 5. Run the Dashboard
```bash
streamlit run main.py
```

The dashboard will open at `http://localhost:8501`

## Local SQLite Database Setup

This project uses SQLite as the local database engine. SQLite stores data in a single file and requires no separate database server.

### 1. Ensure the data folder exists
`config.py` defines the database path as `sqlite:///data/portfolio.db` and will create `data/` automatically.

### 2. Initialize the database locally
If you are cloning the repository for the first time, run:

```bash
python init_sample_data.py
```

This creates the SQLite database and the initial sample data.

### 3. Custom local DB path (optional)
You can override the database location with an environment variable before running the app.

- Windows:
  ```bash
  set DATABASE_URL=sqlite:///C:/full/path/to/portfolio.db
  ```
- Mac/Linux:
  ```bash
  export DATABASE_URL=sqlite:////full/path/to/portfolio.db
  ```

If `DATABASE_URL` is not set, the app uses the default `data/portfolio.db` file.

### 4. Git and local database files
The repository already excludes database files with `.gitignore` entries like `*.db`, `*.sqlite`, and `*.sqlite3`. This prevents local data from being committed to Git.

### 5. Deploying the local SQLite DB without pushing it to Git
If you want to deploy the SQLite database together with the app but do not want to store it in Git:

- Keep the local database file in `data/portfolio.db` and do not add it to source control.
- Use a separate secure deployment workflow so the DB file is provided outside Git.
- On Streamlit Cloud, the safest pattern is to either:
  - use a managed remote database service, or
  - store the SQLite file in a secure private storage location and download it at runtime using a secret URL.

This means the app code can stay in Git while the database stays private.

## Deployment Architecture for Streamlit Cloud

SQLite is a great choice for local development, but for a deployed dashboard with data persistence and security you should treat it as a local-only storage option.

### Recommended architecture

1. Local development:
   - App runs with `DATABASE_URL=sqlite:///data/portfolio.db`
   - Use `init_sample_data.py` to create the database and tables
   - Store data locally in `data/portfolio.db`

2. Streamlit Cloud / production:
   - Use a managed database service such as PostgreSQL, MySQL, or another cloud database
   - Keep the app code on Streamlit Cloud, but connect to the remote database using a secure connection string
   - Store the connection string in Streamlit Secrets or environment variables, not in source code

### Why this is safer

- SQLite on Streamlit Cloud is not ideal because the container filesystem is ephemeral and not guaranteed persistent.
- A managed database service provides:
  - persistent storage
  - access control
  - backups
  - encryption at rest and in transit

### How to structure the app for both local and cloud

- Use SQLAlchemy and `config.DATABASE_URL` as the database abstraction layer.
- In local mode, `DATABASE_URL` points to `sqlite:///data/portfolio.db`.
- In deployment mode, set `DATABASE_URL` to a remote database URI such as `postgresql://user:pass@host/dbname`.

### Secure deployment checklist

- Do not commit `data/portfolio.db` or any database files to Git.
- Keep secrets out of source control and use Streamlit Secrets for production credentials.
- Use a database user with only the permissions needed by the app.
- If you need to keep SQLite for a prototype, treat it as temporary storage only and plan to migrate to a managed database later.

### Streamlit access password
This dashboard now requires a 4-digit password before the app content is shown.

- Local development: set `APP_PASSWORD` as an environment variable.
- Streamlit Cloud: add `APP_PASSWORD` to Streamlit Secrets.

Only users who know the password can open the dashboard.

## SQLite Schema Design

This app uses a clean SQLite schema with the following logical tables:

- `portfolios` — tracks portfolio metadata and activity status
- `holdings` — stores each position with symbol, market, quantity, cost, current price, and notes
- `price_history` — records historic price points by symbol and market
- `performance_snapshots` — stores daily portfolio performance metrics
- `transactions` — logs buy/sell events and realized P/L

### Relationships

- One portfolio can have many holdings
- One portfolio can have many performance snapshots
- One portfolio can have many transactions

This structure supports portfolio tracking, performance history, price history, and transaction auditing.

## Usage

### Create a New Portfolio
1. Click "Create New Portfolio" in the sidebar
2. Enter portfolio name and optional description
3. Start adding holdings

### Add a Holding
1. Click "➕ Add Holding" in sidebar
2. Enter:
   - **Symbol**: Stock ticker (AAPL, 2330.TW, VOO, etc.)
   - **Market**: US or TW
   - **Asset Type**: Select from predefined categories
   - **Quantity**: Number of shares
   - **Purchase Price**: Average cost per share
   - **Purchase Date**: When purchased
   - **Notes**: Optional notes

### Update Prices
Click "🔄 Refresh Prices" to fetch latest prices and calculate current performance

### View Performance
- **Total Value**: Current portfolio worth
- **Total P&L**: Dollar and percentage gains/losses
- **Asset Distribution**: Pie chart by asset type
- **Market Exposure**: US vs Taiwan allocation
- **Top/Worst Performers**: Quick performance overview

## Configuration

Edit `config.py` to customize:

```python
# Risk-free rate for Sharpe ratio calculation
RISK_FREE_RATE = 2.0

# Benchmark indices for comparison
BENCHMARK_INDICES = {
    "SP500": "^GSPC",
    "QQQ": "^IXIC",
    "0050": "0050.TW",
    "VTI": "VTI",
}

# Asset classes
ASSET_CLASSES = [
    "Stock - US",
    "Stock - Taiwan",
    "ETF - US",
    "ETF - Taiwan",
    "Cash",
    "Other"
]

# Refresh interval (minutes)
REFRESH_INTERVAL = 1440  # 24 hours
```

## Database Schema

### portfolios
- id: Primary key
- name: Portfolio name
- description: Optional description
- created_at, updated_at
- is_active: Active status

### holdings
- id: Primary key
- portfolio_id: Foreign key
- symbol: Stock ticker
- asset_type, quantity, purchase_price
- current_price, price_updated_at
- market: "US" or "TW"

### price_history
- symbol, price, date, market
- For tracking price changes over time

### performance_snapshots
- portfolio_id, snapshot_date
- total_value, total_cost, total_pl
- For performance tracking

## Supported Stock Symbols

### US Stocks
- Individual stocks: AAPL, MSFT, NVDA, GOOGL, etc.
- ETFs: VOO, QQQ, VTI, SPY, IVV, etc.
- Indices: ^GSPC (S&P500), ^IXIC (NASDAQ), etc.

### Taiwan Stocks
- Add `.TW` suffix: 2330.TW (TSMC), 3008.TW, etc.
- ETFs: 0050.TW, 0051.TW, 00692.TW, etc.

## Advanced Usage

### Access Raw Data
```python
from backend.portfolio_manager import PortfolioManager
pm = PortfolioManager()

# Get portfolio analysis
analysis = pm.get_portfolio_analysis(portfolio_id=1)

# Get metrics
print(analysis["metrics"].total_value)
print(analysis["distribution"])
print(analysis["market_exposure"])
```

### Fetch Price Data
```python
from backend.data_fetcher import DataFetcher

# Get single price
price = DataFetcher.get_price("AAPL", market="US")

# Get historical data
df = DataFetcher.get_historical_data("AAPL", period="1y")

# Get multiple prices
prices = DataFetcher.get_multiple_prices(["AAPL", "MSFT"], market="US")
```

### Calculate Performance
```python
from backend.calculator import PortfolioCalculator

# Calculate single holding
detail = PortfolioCalculator.calculate_holding_performance(
    symbol="AAPL",
    quantity=10,
    purchase_price=150.0,
    current_price=190.5,
    purchase_date=datetime(2024, 1, 15),
    asset_type="Stock - US",
    market="US"
)
```

## Future Enhancements

- [ ] Risk metrics (Sharpe ratio, Beta, Volatility)
- [ ] Dividend tracking and reinvestment
- [ ] Cost basis calculation with different methods (FIFO, LIFO, Average)
- [ ] Export to CSV/Excel
- [ ] Performance comparison with benchmarks
- [ ] Portfolio rebalancing suggestions
- [ ] Option tracking
- [ ] Dark mode for dashboard
- [ ] Mobile version
- [ ] Multi-currency support
- [ ] Tax reporting features

## Troubleshooting

### "Could not fetch price" Error
- Check internet connection
- Verify symbol is correct (especially Taiwan stocks)
- Taiwan stocks need `.TW` suffix

### Database Lock Error
- Close all other instances of the app
- Delete `data/portfolio.db` and reinitialize

### Streamlit Port Already in Use
```bash
streamlit run main.py --server.port 8502
```

## Data Sources & API Limits

- **yfinance**: No official API limits, but recommended < 2000 calls/hour
- **twstock**: Not rate-limited but may have occasional issues

## Disclaimer

This dashboard is for personal use only. Historical data and prices are estimates. Please verify critical financial decisions with official sources.

## License

MIT License - Feel free to modify and distribute

## Contributing

Suggestions and improvements welcome! 

## Support

For issues or questions, check:
1. Configuration in `config.py`
2. Database connection and schema
3. Internet connection and API availability
4. Python version compatibility (3.8+)
