# Investment Trading Dashboard

Real-time investment trading dashboard with technical analysis, OHLC candlestick charts, and daily automated data updates using yfinance.

## Features

- **Real-time Technical Analysis**: RSI, SMA (20/50/200), MACD, ATR, Bollinger Bands, Support/Resistance, Fibonacci levels
- **Interactive Candlestick Charts**: 60-day OHLC data visualization for 21 US/Japan equity tickers
- **Daily Data Updates**: Automated data acquisition scheduled at 8 PM (20:00) JST
- **4-Layer Technical Analysis Engine**: 
  - Trend Analysis (35%): Moving Average crossovers, trend direction
  - Oscillators (35%): RSI, MACD momentum signals
  - Support/Resistance (20%): Key price levels and pivot points
  - Volatility (10%): ATR and Bollinger Bands analysis
- **Responsive Dashboard**: Modern HTML interface with interactive charting

## Files

- **dashboard_v2.html**: Main dashboard interface with technical indicator cards
- **detail_template.html**: Detailed analysis page with candlestick charts and in-depth metrics
- **fetch_realtime_data.py**: Python script for automated data acquisition from yfinance
- **technical_data.json**: Real-time technical data for all monitored tickers

## Getting Started

### Local Development

1. Start a local HTTP server:
```bash
python3 -m http.server 8000
```

2. Open browser to `http://localhost:8000/dashboard_v2.html`

### Data Updates

Run the data collection script manually:
```bash
python3 fetch_realtime_data.py
```

Or set up automated daily execution at 20:00 (8 PM) JST using a scheduler.

## Tickers Monitored

### Strong Buy (9): AMD, AVGO, MU, TSM, GOOGL, SOXL, SMH, 1570.T, QQQ
### Buy (8): NVDA, QCOM, ASML, AMAT, LRCX, MSFT, TECL, AMZN
### Sell (3): PLTR, ORCL, ARKK
### Strong Sell (1): META

## Deployment to GitHub Pages

The dashboard is deployed to GitHub Pages for live access.

## Technical Stack

- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Chart.js for visualizations
- **Data Source**: yfinance API for market data
- **Hosting**: GitHub Pages (static HTML deployment)
- **Automation**: Scheduled Python script execution

## Browser Requirements

- Modern browser with ES6 support
- CORS-compatible HTTP server (avoid file:// protocol)
- JavaScript enabled

## License

MIT License - Feel free to use and modify for your trading analysis needs.
