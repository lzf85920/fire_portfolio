# 🚀 Quick Start Guide

## Installation & Setup

### Step 1: Navigate to Project Directory
```bash
cd c:\Users\User\Desktop\python\fire_portfolio
```

### Step 2: Activate Virtual Environment
```bash
.venv\Scripts\activate
```

### Step 3: Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Sample Data (Optional)
```bash
python init_sample_data.py
```

This creates a sample portfolio with:
- **US Stocks**: AAPL, MSFT, NVDA (10, 5, 2 shares)
- **US ETFs**: VOO, QQQ (20, 15 shares)
- **Taiwan Stocks**: 2330.TW (TSMC), 3008.TW (100 shares each)
- **Taiwan ETFs**: 0050.TW (50 shares)

**Sample Portfolio Stats:**
- Total Value: $495,715.46
- Total Cost: $117,325.00
- Total P&L: $378,390.46 (322.51%)
- Market Exposure: 94.35% Taiwan, 5.65% US

## Running the Dashboard

### Start the Streamlit App
```bash
streamlit run main.py
```

The dashboard will automatically open in your browser at:
```
http://localhost:8501
```

### What You'll See

#### Dashboard Features:
1. **Portfolio Overview** - Key metrics at a glance
   - Total Value
   - Total Cost
   - Total Return ($ and %)

2. **Asset Distribution** - Interactive pie chart showing portfolio composition

3. **Holdings Details** - Table with per-stock performance
   - Symbol, Asset Type, Market
   - Quantity, Cost basis, Current price
   - Unrealized P&L and return %

4. **Market Exposure** - US vs Taiwan allocation breakdown

5. **Top/Worst Performers** - Quick performance rankings

6. **Sidebar Controls**
   - Portfolio selector (if multiple portfolios exist)
   - Refresh prices button
   - Add holding button
   - Settings menu

## Common Tasks

### Add a New Stock Holding

1. Click **➕ Add Holding** in the sidebar
2. Fill in the form:
   ```
   Symbol: AAPL (US stocks) or 2330.TW (Taiwan stocks)
   Market: US or TW
   Asset Type: Stock - US, Stock - Taiwan, ETF - US, ETF - Taiwan, etc.
   Quantity: Number of shares (e.g., 10)
   Purchase Price: Cost per share (e.g., 150.00)
   Purchase Date: When you bought it
   Notes: Optional notes
   ```
3. Click **Add Holding**

### Refresh Latest Prices

1. Click **🔄 Refresh Prices** in the sidebar
2. Wait for prices to update
3. Dashboard will show latest performance

### Create Multiple Portfolios

1. Click **Create New Portfolio** in settings
2. Portfolio name and description
3. Start adding holdings to each portfolio
4. Switch between portfolios using the dropdown

## Supported Stock Symbols

### US Market (use with market="US")
- **Mega Cap**: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
- **Broad Market ETFs**: VOO, VTI, SPY, IVV
- **Tech-focused ETFs**: QQQ, XLK
- **Indices**: ^GSPC (S&P500), ^IXIC (NASDAQ)

### Taiwan Market (use with market="TW")
- **Add .TW suffix** to symbol
- **Major stocks**: 2330.TW (TSMC), 2317.TW (2330 Subsidiary)
- **Broad index**: 0050.TW (Taiwan ETF 50)
- **Examples**: 1101.TW, 1102.TW, 2801.TW, 3008.TW

## Troubleshooting

### "Port already in use" Error
```bash
streamlit run main.py --server.port 8502
```

### "Could not fetch price" for Taiwan stocks
- Ensure symbol ends with `.TW`
- Check internet connection
- Verify symbol is correct (example: 2330.TW not 2330)

### Database Lock Error
Delete `data/portfolio.db` and run `init_sample_data.py` again

### Slow Performance
- First refresh may take longer (fetching prices)
- Subsequent refreshes are faster
- More holdings = slower calculations

## Data Refresh

The dashboard shows real-time prices fetched from Yahoo Finance:
- Click "🔄 Refresh Prices" to manually update
- No scheduled auto-refresh (can be added in advanced configuration)

## Database

Your portfolio data is stored in:
```
data/portfolio.db
```

This SQLite database contains:
- Portfolio configuration
- Holdings and positions
- Price history
- Performance snapshots

To reset everything:
```bash
# Delete the database
rm data/portfolio.db

# Reinitialize sample data
python init_sample_data.py
```

## Next Steps

### Add More Holdings
Use the dashboard form to add your actual investment holdings

### Track Multiple Portfolios
Create separate portfolios for:
- Long-term investments
- Day trading
- Retirement accounts
- By asset class or strategy

### Update Prices Daily
Keep prices updated for accurate performance tracking

### Advanced Configuration
Edit `config.py` to customize:
- Asset classes
- Benchmark indices
- Risk-free rate for calculations

## Support

For issues, check:
1. Python version (3.8+)
2. All packages are installed (`pip list`)
3. Database exists (`data/portfolio.db`)
4. Internet connection (for real-time prices)

## Have Questions?

Check the [README.md](README.md) for:
- Detailed feature documentation
- Technical architecture
- Advanced usage examples
- Future enhancements

---

**Happy investing! 📈**
