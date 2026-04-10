"""
Headless version for Railway deployment
Automated hourly scanning without GUI
Credentials from environment variables or config.py
"""

import requests
import os
import sys
import time
import datetime
import logging
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
from math import ceil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scan_auto.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load credentials from environment or config
def load_credentials():
    """Load MT5 and Telegram credentials from environment or config.py"""
    mt5_login = os.getenv('MT5_LOGIN')
    mt5_password = os.getenv('MT5_PASSWORD')
    mt5_server = os.getenv('MT5_SERVER')
    mt5_path = os.getenv('MT5_PATH')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Fallback to config.py if environment variables not set
    if not all([mt5_login, mt5_password, mt5_server, telegram_token, telegram_chat_id]):
        try:
            from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            mt5_login = mt5_login or MT5_LOGIN
            mt5_password = mt5_password or MT5_PASSWORD
            mt5_server = mt5_server or MT5_SERVER
            mt5_path = mt5_path or MT5_PATH
            telegram_token = telegram_token or TELEGRAM_BOT_TOKEN
            telegram_chat_id = telegram_chat_id or TELEGRAM_CHAT_ID
        except ImportError:
            logger.error("config.py not found and environment variables incomplete")
            sys.exit(1)
    
    return {
        'MT5_LOGIN': int(mt5_login),
        'MT5_PASSWORD': mt5_password,
        'MT5_SERVER': mt5_server,
        'MT5_PATH': mt5_path,
        'TELEGRAM_BOT_TOKEN': telegram_token,
        'TELEGRAM_CHAT_ID': telegram_chat_id
    }

CREDS = load_credentials()
MT5_LOGIN = CREDS['MT5_LOGIN']
MT5_PASSWORD = CREDS['MT5_PASSWORD']
MT5_SERVER = CREDS['MT5_SERVER']
MT5_PATH = CREDS['MT5_PATH']
TELEGRAM_BOT_TOKEN = CREDS['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = CREDS['TELEGRAM_CHAT_ID']

from tradingview_ta import Interval

PAIRS = [
    "EURUSD", "EURGBP", "EURCAD", "EURJPY", "EURCHF", "EURAUD", "EURNZD",
    "USDCAD", "USDJPY", "USDCHF",
    "GBPUSD", "GBPCAD", "GBPJPY", "GBPCHF", "GBPNZD", "GBPAUD",
    "AUDUSD", "AUDCAD", "AUDCHF", "AUDJPY",
    "NZDUSD", "NZDCAD", "NZDCHF"
]

TIMEFRAMES = [Interval.INTERVAL_1_DAY, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_15_MINUTES]
API_REQUEST_DELAY = 2.0
PAIR_DELAY = 3.0
BATCH_SIZE = 10
BATCH_DELAY = 8.0
MAX_API_RETRIES = 3

MT5_TIMEFRAMES = {
    Interval.INTERVAL_1_DAY: mt5.TIMEFRAME_D1,
    Interval.INTERVAL_4_HOURS: mt5.TIMEFRAME_H4,
    Interval.INTERVAL_1_HOUR: mt5.TIMEFRAME_H1,
    Interval.INTERVAL_15_MINUTES: mt5.TIMEFRAME_M15
}


def initialize_mt5():
    if not mt5.initialize(MT5_PATH):
        logger.error("MT5 initialization failed")
        return False
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        logger.error("MT5 login failed")
        return False
    logger.info("MT5 initialized and logged in")
    return True


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info("Telegram message sent successfully")
        else:
            logger.error(f"Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")


def is_psychological_level(price, pair):
    # Basic psychological levels for major pairs
    levels = {
        "EURUSD": [1.0000, 1.0500, 1.1000, 1.1500, 1.2000],
        "GBPUSD": [1.2000, 1.2500, 1.3000, 1.3500, 1.4000],
        "USDJPY": [100.00, 110.00, 120.00, 130.00, 140.00, 150.00],
        "EURJPY": [120.00, 130.00, 140.00, 150.00, 160.00],
        "GBPJPY": [150.00, 160.00, 170.00, 180.00, 190.00],
        "AUDUSD": [0.6000, 0.6500, 0.7000, 0.7500, 0.8000],
        "NZDUSD": [0.5500, 0.6000, 0.6500, 0.7000, 0.7500],
        "USDCAD": [1.2000, 1.2500, 1.3000, 1.3500, 1.4000],
        "USDCHF": [0.8000, 0.8500, 0.9000, 0.9500, 1.0000],
        "EURGBP": [0.8000, 0.8500, 0.9000, 0.9500, 1.0000],
        "EURCAD": [1.4000, 1.4500, 1.5000, 1.5500, 1.6000],
        "EURCHF": [0.9500, 1.0000, 1.0500, 1.1000, 1.1500],
        "EURAUD": [1.5000, 1.5500, 1.6000, 1.6500, 1.7000],
        "EURNZD": [1.6000, 1.6500, 1.7000, 1.7500, 1.8000],
        "GBPCAD": [1.6000, 1.6500, 1.7000, 1.7500, 1.8000],
        "GBPCHF": [1.2000, 1.2500, 1.3000, 1.3500, 1.4000],
        "GBPNZD": [1.8000, 1.8500, 1.9000, 1.9500, 2.0000],
        "GBPAUD": [1.7000, 1.7500, 1.8000, 1.8500, 1.9000],
        "AUDCAD": [0.8500, 0.9000, 0.9500, 1.0000, 1.0500],
        "AUDCHF": [0.5500, 0.6000, 0.6500, 0.7000, 0.7500],
        "AUDJPY": [70.00, 75.00, 80.00, 85.00, 90.00],
        "NZDCAD": [0.8000, 0.8500, 0.9000, 0.9500, 1.0000],
        "NZDCHF": [0.5000, 0.5500, 0.6000, 0.6500, 0.7000]
    }
    pair_levels = levels.get(pair, [])
    for level in pair_levels:
        if abs(price - level) < 0.001:  # Tolerance
            return True
    return False


def get_mt5_data(symbol, timeframe, n_candles=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)
    if rates is None:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df


def compute_indicators(df):
    indicators = {}
    indicators['close'] = df['close'].iloc[-1]
    indicators['open'] = df['open'].iloc[-1]
    indicators['high'] = df['high'].iloc[-1]
    indicators['low'] = df['low'].iloc[-1]
    indicators['volume'] = df['tick_volume'].iloc[-1]

    # RSI
    rsi = ta.rsi(df['close'], length=14)
    indicators['RSI'] = rsi.iloc[-1] if not rsi.empty else 50

    # MACD
    macd = ta.macd(df['close'])
    indicators['MACD.hist'] = macd['MACDh_12_26_9'].iloc[-1] if 'MACDh_12_26_9' in macd.columns else 0

    # Stoch
    stoch = ta.stoch(df['high'], df['low'], df['close'])
    indicators['Stoch.K'] = stoch['STOCHk_14_3_3'].iloc[-1] if 'STOCHk_14_3_3' in stoch.columns else 50

    # Pivot points - Manual calculation
    high = df['high'].iloc[-1]
    low = df['low'].iloc[-1]
    close = df['close'].iloc[-1]
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    indicators['Pivot.M.Classic.Middle'] = pivot
    indicators['Pivot.M.Classic.R1'] = r1
    indicators['Pivot.M.Classic.S1'] = s1
    indicators['Pivot.M.Classic.R2'] = r2
    indicators['Pivot.M.Classic.S2'] = s2

    # ADX
    adx = ta.adx(df['high'], df['low'], df['close'])
    indicators['ADX'] = adx['ADX_14'].iloc[-1] if 'ADX_14' in adx.columns else 20

    return indicators


def compute_recommendation(indicators):
    rsi = indicators.get('RSI', 50)
    macd_hist = indicators.get('MACD.hist', 0)
    stoch_k = indicators.get('Stoch.K', 50)
    adx = indicators.get('ADX', 20)

    buy_signals = 0
    sell_signals = 0

    if rsi < 30:
        buy_signals += 1
    elif rsi > 70:
        sell_signals += 1

    if macd_hist > 0:
        buy_signals += 1
    elif macd_hist < 0:
        sell_signals += 1

    if stoch_k < 20:
        buy_signals += 1
    elif stoch_k > 80:
        sell_signals += 1

    if adx > 25:
        if buy_signals > sell_signals:
            return 'BUY'
        elif sell_signals > buy_signals:
            return 'SELL'

    if buy_signals > sell_signals:
        return 'BUY'
    elif sell_signals > buy_signals:
        return 'SELL'
    return 'NEUTRAL'


def get_momentum(indicators):
    rsi = indicators.get('RSI', 50)
    stoch_k = indicators.get('Stoch.K', indicators.get('Stoch.K%', indicators.get('STOCH.K', 50)))
    macd_hist = indicators.get('MACD.hist', indicators.get('MACD Histogram', indicators.get('MACD_Hist', 0)))
    adx = indicators.get('ADX', 20)
    return {
        'rsi': rsi,
        'stoch_k': stoch_k,
        'macd_hist': macd_hist,
        'adx': adx
    }


def detect_order_block(indicators, current_price, zones):
    momentum = get_momentum(indicators)
    rsi = momentum['rsi']
    macd_hist = momentum['macd_hist']
    ob = None

    strong_support = 'Support' in zones or 'Pivot' in zones
    strong_resistance = 'Resistance' in zones or 'Pivot' in zones

    if rsi < 35 and (strong_support or macd_hist < 0):
        ob = 'Bullish OB'
    elif rsi > 65 and (strong_resistance or macd_hist > 0):
        ob = 'Bearish OB'
    elif rsi < 30 and indicators.get('RSI[1]', 50) > rsi:
        ob = 'Bullish OB'
    elif rsi > 70 and indicators.get('RSI[1]', 50) < rsi:
        ob = 'Bearish OB'

    return ob


def detect_support_resistance(current_price, indicators):
    levels = []
    pivot = indicators.get('Pivot.M.Classic.Middle', None)
    r1 = indicators.get('Pivot.M.Classic.R1', None)
    r2 = indicators.get('Pivot.M.Classic.R2', None)
    s1 = indicators.get('Pivot.M.Classic.S1', None)
    s2 = indicators.get('Pivot.M.Classic.S2', None)

    if pivot is not None and abs(current_price - pivot) / max(pivot, 1) < 0.002:
        levels.append('Pivot')
    if r1 is not None and abs(current_price - r1) / max(r1, 1) < 0.002:
        levels.append('Resistance R1')
    if r2 is not None and abs(current_price - r2) / max(r2, 1) < 0.002:
        levels.append('Resistance R2')
    if s1 is not None and abs(current_price - s1) / max(s1, 1) < 0.002:
        levels.append('Support S1')
    if s2 is not None and abs(current_price - s2) / max(s2, 1) < 0.002:
        levels.append('Support S2')

    return levels


def detect_fvg(current_price, indicators, zones):
    pivot = indicators.get('Pivot.M.Classic.Middle', None)
    r1 = indicators.get('Pivot.M.Classic.R1', None)
    s1 = indicators.get('Pivot.M.Classic.S1', None)
    r2 = indicators.get('Pivot.M.Classic.R2', None)
    s2 = indicators.get('Pivot.M.Classic.S2', None)
    if pivot is None:
        return None

    distance = abs(current_price - pivot) / max(pivot, 1)
    if distance > 0.015 and ('Support' in zones or 'Resistance' in zones):
        return 'FVG Candidate'

    if r1 is not None and abs(current_price - r1) / max(r1, 1) > 0.02:
        return 'FVG Candidate'
    if s1 is not None and abs(current_price - s1) / max(s1, 1) > 0.02:
        return 'FVG Candidate'
    if r2 is not None and abs(current_price - r2) / max(r2, 1) > 0.02:
        return 'FVG Candidate'
    if s2 is not None and abs(current_price - s2) / max(s2, 1) > 0.02:
        return 'FVG Candidate'

    return None


def get_target_levels(entry, sl, direction):
    distance = abs(entry - sl)
    if distance == 0:
        return None, None, None
    if direction == 'BUY':
        return entry + distance, entry + 2 * distance, entry + 3 * distance
    if direction == 'SELL':
        return entry - distance, entry - 2 * distance, entry - 3 * distance
    return None, None, None


def choose_levels(current_price, direction, indicators):
    pivot = indicators.get('Pivot.M.Classic.Middle', None)
    r1 = indicators.get('Pivot.M.Classic.R1', None)
    r2 = indicators.get('Pivot.M.Classic.R2', None)
    s1 = indicators.get('Pivot.M.Classic.S1', None)
    s2 = indicators.get('Pivot.M.Classic.S2', None)

    levels = {
        'pivot': pivot,
        'r1': r1,
        'r2': r2,
        's1': s1,
        's2': s2
    }

    if direction == 'BUY':
        supports = [l for l in [s2, s1, pivot] if l is not None and l < current_price]
        sl = max(supports) if supports else current_price * 0.997
    elif direction == 'SELL':
        resistances = [l for l in [r2, r1, pivot] if l is not None and l > current_price]
        sl = min(resistances) if resistances else current_price * 1.003
    else:
        sl = None

    return sl, levels


def format_pair_message(pair, direction, score, rationale, entry, sl, t1, t2, t3, current_price):
    direction_icon = '🟢' if direction == 'BUY' else '🔴'
    if direction == 'NEUTRAL':
        return (
            f"<b>{pair} ⚪ NEUTRAL</b> — <i>{score}/100</i>\n"
            f"<b>Prix actuel:</b> <code>{current_price:.5f}</code>\n"
            f"<b>Raison:</b> {rationale}"
        )

    rr1 = abs(t1 - entry)
    rr2 = abs(t2 - entry)
    rr3 = abs(t3 - entry)
    return (
        f"<b>{pair} {direction_icon} {direction}</b> — <i>{score}/100</i>\n"
        f"<b>Entrée:</b> <code>{entry:.5f}</code>\n"
        f"<b>SL:</b> <code>{sl:.5f}</code>\n"
        f"<b>TP1:</b> <code>{t1:.5f}</code> | <b>TP2:</b> <code>{t2:.5f}</code> | <b>TP3:</b> <code>{t3:.5f}</code>\n"
        f"<b>R/R:</b> 1:{rr1/abs(sl-entry):.1f} | 2:{rr2/abs(sl-entry):.1f} | 3:{rr3/abs(sl-entry):.1f}\n"
        f"<b>Confluence:</b> {rationale}"
    )


def compute_pair_score(pair_results):
    weight = {
        Interval.INTERVAL_1_DAY: 5,
        Interval.INTERVAL_4_HOURS: 4,
        Interval.INTERVAL_1_HOUR: 3,
        Interval.INTERVAL_15_MINUTES: 2,
        Interval.INTERVAL_5_MINUTES: 1
    }

    totals = {'BUY': 0, 'SELL': 0, 'NEUTRAL': 0}
    for result in pair_results:
        totals[result['recommendation']] += weight.get(result['tf'], 1)

    if totals['BUY'] > totals['SELL']:
        direction = 'BUY'
        alignment = totals['BUY']
    elif totals['SELL'] > totals['BUY']:
        direction = 'SELL'
        alignment = totals['SELL']
    else:
        direction = 'NEUTRAL'
        alignment = totals['NEUTRAL']

    total_possible = sum(weight.values())
    score = 20 + int((alignment / total_possible) * 45)

    bonus = 0
    if any(r['psych'] for r in pair_results):
        bonus += 10
    if any(r['ob'] for r in pair_results):
        bonus += 12
    if any(r['zones'] for r in pair_results):
        bonus += 10
    if any(r['fvg'] for r in pair_results):
        bonus += 8
    score += bonus

    if any(r['recommendation'] == direction for r in pair_results if direction != 'NEUTRAL'):
        score += 5
    if any(r['recommendation'] == 'NEUTRAL' for r in pair_results):
        score -= 5

    score = max(min(score, 100), 10)
    if direction == 'NEUTRAL' and score > 55:
        score = 55
    if direction != 'NEUTRAL' and score < 40:
        score = 40

    major = [r for r in pair_results if r['tf'] in (Interval.INTERVAL_1_DAY, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_HOUR)]
    major_buy = sum(1 for r in major if r['recommendation'] == 'BUY')
    major_sell = sum(1 for r in major if r['recommendation'] == 'SELL')
    if direction == 'BUY' and major_buy < 2:
        score -= 8
    if direction == 'SELL' and major_sell < 2:
        score -= 8

    score = max(score, 20)
    if score < 45:
        direction = 'NEUTRAL'

    rationale = []
    if direction == 'BUY':
        rationale.append('Structure haussière principale')
    elif direction == 'SELL':
        rationale.append('Structure baissière principale')
    else:
        rationale.append('Pas de consensus clair')

    if any(r['psych'] for r in pair_results):
        rationale.append('Niveau psychologique')
    if any(r['ob'] for r in pair_results):
        rationale.append('Order block présent')
    if any(r['zones'] for r in pair_results):
        rationale.append('Confluence S/R')
    if any(r['fvg'] for r in pair_results):
        rationale.append('FVG')

    return direction, score, ' ; '.join(rationale[:3])


def scan_signals_headless():
    """Headless scan without GUI updates - logs to console and files"""
    logger.info("=== STARTING SCAN ===")
    if not initialize_mt5():
        logger.error("Failed to initialize MT5")
        return

    signals = []
    total_pairs = len(PAIRS)
    total_batches = ceil(total_pairs / BATCH_SIZE)
    pair_index = 0
    
    try:
        for pair in PAIRS:
            pair_index += 1
            batch_index = ceil(pair_index / BATCH_SIZE)
            logger.info(f"[Batch {batch_index}/{total_batches}] Scanning {pair} ({pair_index}/{total_pairs})")
            
            pair_results = []
            last_indicators = None
            last_recommendation = 'NEUTRAL'
            last_current_price = 0
            
            for tf in TIMEFRAMES:
                mt5_tf = MT5_TIMEFRAMES[tf]
                df = get_mt5_data(pair, mt5_tf)
                if df is None or df.empty:
                    logger.warning(f"No data for {pair} {tf}")
                    time.sleep(API_REQUEST_DELAY)
                    continue

                indicators = compute_indicators(df)
                recommendation = compute_recommendation(indicators)
                current_price = indicators['close']
                last_indicators = indicators
                last_current_price = current_price
                psych = is_psychological_level(current_price, pair)
                zones = detect_support_resistance(current_price, indicators)
                ob = detect_order_block(indicators, current_price, zones)
                fvg = detect_fvg(current_price, indicators, zones)

                pair_results.append({
                    'tf': tf,
                    'recommendation': recommendation,
                    'psych': psych,
                    'ob': ob,
                    'zones': zones,
                    'fvg': fvg
                })

                time.sleep(API_REQUEST_DELAY)

            if not pair_results or last_indicators is None:
                logger.info(f"{pair} - No results")
                continue

            direction, score, rationale = compute_pair_score(pair_results)
            if score < 68:
                logger.info(f"{pair} - Score {score} below threshold (68)")
                continue

            logger.info(f"{pair} - SIGNAL DETECTED: {direction} {score}/100")
            
            sl, levels = choose_levels(last_current_price, direction, last_indicators)
            if direction == 'NEUTRAL' or sl is None:
                message = format_pair_message(pair, direction, score, rationale, last_current_price, sl or last_current_price, last_current_price, last_current_price, last_current_price, last_current_price)
            else:
                t1, t2, t3 = get_target_levels(last_current_price, sl, direction)
                message = format_pair_message(pair, direction, score, rationale, last_current_price, sl, t1, t2, t3, last_current_price)

            send_telegram_message(message)
            signals.append(f'{pair}: {direction} score {score}')
            time.sleep(PAIR_DELAY)

            if pair_index % BATCH_SIZE == 0 and pair_index < total_pairs:
                logger.info(f"Batch {batch_index}/{total_batches} complete. Pausing {BATCH_DELAY}s...")
                time.sleep(BATCH_DELAY)

        logger.info(f"=== SCAN COMPLETE === {len(signals)} signals found")
        
    except Exception as e:
        logger.error(f"Error during scan: {e}", exc_info=True)
    finally:
        mt5.shutdown()


def auto_scan():
    """Main loop for automated scanning 8h-18h GMT"""
    logger.info("Auto scan daemon started. Will scan hourly 8h-18h GMT")
    while True:
        try:
            now = datetime.datetime.utcnow()
            if 8 <= now.hour < 18:
                logger.info(f"Running scan at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                scan_signals_headless()
                logger.info("Sleeping 1 hour until next scan...")
                time.sleep(3600)  # Scan every hour during active hours
            else:
                # Calculate time until next scan (8h GMT next day)
                next_scan = now.replace(hour=8, minute=0, second=0, microsecond=0)
                if now.hour >= 18:
                    next_scan += datetime.timedelta(days=1)
                sleep_seconds = (next_scan - now).total_seconds()
                logger.info(f"Outside trading hours. Next scan at {next_scan.strftime('%Y-%m-%d %H:%M:%S UTC')} ({int(sleep_seconds/3600)}h away)")
                time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            logger.info("Auto scan stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in auto scan loop: {e}", exc_info=True)
            time.sleep(60)  # Wait a minute before retrying


if __name__ == '__main__':
    logger.info("Trading Signal Scanner (Headless) started")
    auto_scan()
