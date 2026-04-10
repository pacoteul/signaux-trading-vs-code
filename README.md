# Trading Signal Scanner

Professional forex trading signal scanner with technical analysis and Telegram notifications. Analyze 23 pairs across 4 timeframes (D1, H4, H1, M15) with Smart Money Concept (SMC), Order Block (OB), Support/Resistance (S/R), and Fair Value Gap (FVG) detection.

## Features

- 📊 **Multi-timeframe Analysis**: D1, H4, H1, M15 with weighted scoring
- 🎯 **Technical Patterns**: Order Blocks, Support/Resistance, Fair Value Gaps, Psychological Levels
- 📱 **Telegram Notifications**: HTML formatted signals with Entry, SL, TP levels and R/R ratios
- 🔐 **Secure Credentials**: Environment variables for Railway, config.py for local
- 🖥️ **Two Versions**:
  - `main.py` → GUI with manual scan button (local use)
  - `scan_auto.py` → Headless automation (Railway deployment)
- ⏰ **Automated Scanning**: Hourly scans 8h-18h GMT
- 🔄 **Batch Processing**: 10 pairs/batch with stabilization delays
- 🎚️ **Quality Filter**: Score ≥ 68/100 threshold

## Installation

### Prerequisites
- Python 3.9+
- MetaTrader 5 account (Admiral Markets demo account recommended)
- Telegram Bot (create via @BotFather)

### Local Setup

```bash
# Clone repository
git clone <your-repo-url>
cd signaux-trading

# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config.example.py config.py

# Edit config.py with your credentials
# - MT5_LOGIN: Your MT5 account number
# - MT5_PASSWORD: Your MT5 password
# - MT5_SERVER: Your broker server (e.g., AdmiralsGroup-Demo)
# - MT5_PATH: Path to MT5 terminal executable
# - TELEGRAM_BOT_TOKEN: Your Telegram bot token
# - TELEGRAM_CHAT_ID: Your Telegram chat ID
```

### Run Locally

**Option 1: GUI with Manual Scanning (Recommended for Testing)**
```bash
python main.py
# Click "Scan for Signals" button to manually trigger scans
# Auto-scan runs hourly in background (8h-18h GMT)
```

**Option 2: Headless Mode (Terminal Only)**
```bash
python scan_auto.py
# Runs hourly scans 8h-18h GMT with console logging
```

## Railway Deployment

### Setup Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure Environment Variables**
   - Go to your Railway project settings
   - Add variables from `.env.example`:
     - `MT5_LOGIN`: Your MT5 account number
     - `MT5_PASSWORD`: Your MT5 password
     - `MT5_SERVER`: Broker server name
     - `MT5_PATH`: (optional, defaults to config.py value)
     - `TELEGRAM_BOT_TOKEN`: Your bot token
     - `TELEGRAM_CHAT_ID`: Your chat ID

4. **Deploy**
   - Railway auto-deploys on every GitHub push
   - App runs `python scan_auto.py` automatically
   - Logs viewable in Railway dashboard

### Monitoring

- Check Railway logs for hourly scan output
- Telegram messages arrive each hour during 8h-18h GMT
- Logs also saved to `scan_auto.log` on Railway

## Configuration

### Scoring System

Each pair gets a 20-100 score based on:
- **Multi-timeframe confluence** (weighted: D1=5pts, H4=4pts, H1=3pts, M15=2pts)
- **Pattern bonuses**:
  - Psychological level: +10pts
  - Order Block detected: +12pts
  - S/R confluence: +10pts
  - Fair Value Gap: +8pts
- **Direction alignment**: BUY/SELL consensus with major timeframes

### Signal Filtering

Only signals with **score ≥ 68** are sent to Telegram.

### Pairs Analyzed

EUR pair family: EURUSD, EURGBP, EURCAD, EURJPY, EURCHF, EURAUD, EURNZD
USD pairs: USDCAD, USDJPY, USDCHF
GBP pairs: GBPUSD, GBPCAD, GBPJPY, GBPCHF, GBPNZD, GBPAUD
AUD pairs: AUDUSD, AUDCAD, AUDCHF, AUDJPY
NZD pairs: NZDUSD, NZDCAD, NZDCHF

## API Rate Limiting & Stability

- API_REQUEST_DELAY: 2.0s between candle requests
- PAIR_DELAY: 3.0s after each pair
- BATCH_DELAY: 8.0s between 10-pair batches
- Typical full scan: ~2 minutes per 10-pair batch

## Security

- **config.py** is in `.gitignore` (never committed)
- **Railway uses environment variables** (safer than files)
- Copy `config.example.py` to start local configuration

## Telegram Signal Format

```
🟢 EURUSD BUY — 75/100
Entrée: 1.09500
SL: 1.09200
TP1: 1.09800 | TP2: 1.10100 | TP3: 1.10400
R/R: 1:1.0 | 2:2.0 | 3:3.0
Confluence: Structure haussière principale ; Order block présent ; Confluence S/R
```

## Troubleshooting

### MT5 Connection Issues
- Verify MT5_PATH points to correct terminal executable
- Check MT5_LOGIN, MT5_PASSWORD, MT5_SERVER credentials
- Ensure MT5 terminal has internet connection

### No Signals Being Sent
- Check score threshold (only ≥68/100 signals sent)
- Verify Telegram credentials are correct
- Check `scan_auto.log` or GUI status for details

### Railway Not Running
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure `Procfile` exists in root directory

## License

[Add your license here]