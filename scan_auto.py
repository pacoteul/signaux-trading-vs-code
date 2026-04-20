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
from history_stats import load_stats, get_historical_adjustment

# Load historical stats once at startup (empty dict if file not yet generated)
HIST_STATS = load_stats()

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
        if abs(price - level) / max(level, 0.0001) < 0.001:  # Relative tolerance 0.1%
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

    # RSI — current and previous bar for reversal/divergence detection
    rsi = ta.rsi(df['close'], length=14)
    indicators['RSI'] = float(rsi.iloc[-1]) if len(rsi) > 0 and pd.notna(rsi.iloc[-1]) else 50
    indicators['RSI_prev'] = float(rsi.iloc[-2]) if len(rsi) > 1 and pd.notna(rsi.iloc[-2]) else 50

    # MACD
    macd = ta.macd(df['close'])
    indicators['MACD.hist'] = macd['MACDh_12_26_9'].iloc[-1] if 'MACDh_12_26_9' in macd.columns else 0

    # Stoch
    stoch = ta.stoch(df['high'], df['low'], df['close'])
    indicators['Stoch.K'] = stoch['STOCHk_14_3_3'].iloc[-1] if 'STOCHk_14_3_3' in stoch.columns else 50

    # Pivot points — use last COMPLETE candle (iloc[-2]), not the forming one
    prev = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]
    pivot = (prev['high'] + prev['low'] + prev['close']) / 3
    r1 = (2 * pivot) - prev['low']
    s1 = (2 * pivot) - prev['high']
    r2 = pivot + (prev['high'] - prev['low'])
    s2 = pivot - (prev['high'] - prev['low'])

    indicators['Pivot.M.Classic.Middle'] = pivot
    indicators['Pivot.M.Classic.R1'] = r1
    indicators['Pivot.M.Classic.S1'] = s1
    indicators['Pivot.M.Classic.R2'] = r2
    indicators['Pivot.M.Classic.S2'] = s2

    # ADX
    adx = ta.adx(df['high'], df['low'], df['close'])
    indicators['ADX'] = adx['ADX_14'].iloc[-1] if 'ADX_14' in adx.columns else 20

    # ATR for volatility-based stop loss
    atr = ta.atr(df['high'], df['low'], df['close'], length=14)
    indicators['ATR'] = float(atr.iloc[-1]) if atr is not None and len(atr) > 0 and pd.notna(atr.iloc[-1]) else None

    # EMA trend filter (20 and 50 period)
    ema20 = ta.ema(df['close'], length=20)
    ema50 = ta.ema(df['close'], length=50)
    indicators['EMA20'] = float(ema20.iloc[-1]) if ema20 is not None and len(ema20) > 0 and pd.notna(ema20.iloc[-1]) else None
    indicators['EMA50'] = float(ema50.iloc[-1]) if ema50 is not None and len(ema50) > 0 and pd.notna(ema50.iloc[-1]) else None

    # Fair Value Gap — genuine 3-candle gap analysis
    if len(df) >= 3:
        c1_high = df['high'].iloc[-3]
        c1_low = df['low'].iloc[-3]
        c3_high = df['high'].iloc[-1]
        c3_low = df['low'].iloc[-1]
        if c3_low > c1_high:
            indicators['FVG'] = 'Bullish FVG'
        elif c3_high < c1_low:
            indicators['FVG'] = 'Bearish FVG'
        else:
            indicators['FVG'] = None
    else:
        indicators['FVG'] = None

    return indicators


def compute_recommendation(indicators):
    rsi = indicators.get('RSI', 50)
    macd_hist = indicators.get('MACD.hist', 0)
    stoch_k = indicators.get('Stoch.K', 50)
    adx = indicators.get('ADX', 20)
    close = indicators.get('close')
    ema20 = indicators.get('EMA20')
    ema50 = indicators.get('EMA50')

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

    # EMA trend alignment: price position relative to both EMAs confirms trend
    if close and ema20 and ema50:
        if close > ema20 > ema50:
            buy_signals += 1
        elif close < ema20 < ema50:
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
    rsi_prev = indicators.get('RSI_prev', 50)

    # zones contains strings like 'Support S1', 'Resistance R1', 'Pivot' — use substring match
    strong_support = any('Support' in z for z in zones) or any('Pivot' in z for z in zones)
    strong_resistance = any('Resistance' in z for z in zones) or any('Pivot' in z for z in zones)

    # Bullish OB: oversold at support zone
    if rsi < 35 and strong_support:
        return 'Bullish OB'
    # Bearish OB: overbought at resistance zone
    if rsi > 65 and strong_resistance:
        return 'Bearish OB'
    # Bullish OB: RSI recovering from oversold (rsi_prev < rsi = RSI rising)
    if rsi < 40 and rsi_prev < rsi:
        return 'Bullish OB'
    # Bearish OB: RSI falling from overbought (rsi_prev > rsi = RSI falling)
    if rsi > 60 and rsi_prev > rsi:
        return 'Bearish OB'

    return None


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
    # Use genuine 3-candle gap analysis pre-calculated in compute_indicators
    return indicators.get('FVG', None)


def detect_wyckoff_phase(df, indicators):
    """
    Détecte les phases et événements Wyckoff clés sur les données OHLCV.

    Événements détectés :
    - Spring (Accumulation)       : faux cassage sous le support → retournement haussier
    - Selling Climax / SC         : bougie baissière large + volume élevé aux bas → épuisement vendeurs
    - Upthrust / UT               : faux cassage au-dessus de la résistance → retournement baissier
    - Buying Climax / BC          : bougie haussière large + volume élevé aux hauts → épuisement acheteurs
    - Sign of Strength / SOS      : cassage de résistance + volume → continuation haussière
    - Sign of Weakness / SOW      : cassage de support + volume → continuation baissière

    Retourne un dict {'phase', 'event', 'wyckoff_bias': 'BUY'|'SELL'|'NEUTRAL'}
    """
    if len(df) < 21:
        return {'phase': None, 'event': None, 'wyckoff_bias': 'NEUTRAL'}

    close = df['close']
    high_col = df['high']
    low_col = df['low']
    open_col = df['open']
    volume = df['tick_volume']

    curr_close = close.iloc[-1]
    curr_open = open_col.iloc[-1]
    curr_high = high_col.iloc[-1]
    curr_low = low_col.iloc[-1]
    curr_volume = volume.iloc[-1]

    # Volume moyen sur 20 bougies (hors bougie courante)
    avg_volume = volume.iloc[-21:-1].mean()
    high_volume = curr_volume > avg_volume * 1.5 if avg_volume > 0 else False

    # Range des 20 bougies précédentes
    recent_high = high_col.iloc[-21:-1].max()
    recent_low = low_col.iloc[-21:-1].min()
    trend_range = recent_high - recent_low if recent_high > recent_low else 1e-9

    # Position du prix dans le range (0 = bas, 1 = haut)
    price_position = max(0.0, min(1.0, (curr_close - recent_low) / trend_range))

    # Caractéristiques de la bougie courante
    candle_range = curr_high - curr_low
    atr = indicators.get('ATR') or (trend_range / 10)
    is_large_candle = candle_range > atr * 1.3
    is_bullish = curr_close > curr_open
    is_bearish = curr_close < curr_open

    # Contexte de tendance via EMA
    ema20 = indicators.get('EMA20')
    ema50 = indicators.get('EMA50')
    in_downtrend = bool(ema20 and ema50 and curr_close < ema20 and ema20 < ema50)
    in_uptrend = bool(ema20 and ema50 and curr_close > ema20 and ema20 > ema50)

    # --- SPRING (Accumulation) ---
    # La bougie plonge sous le support récent puis remonte au-dessus → shakeout classique
    if curr_low < recent_low and curr_close > recent_low and is_bullish:
        return {'phase': 'Accumulation', 'event': 'Spring', 'wyckoff_bias': 'BUY'}

    # --- SELLING CLIMAX (SC) ---
    # Grande bougie baissière avec volume élevé en bas de range + tendance baissière
    if price_position < 0.25 and is_bearish and is_large_candle and high_volume and in_downtrend:
        return {'phase': 'Accumulation', 'event': 'Selling Climax (SC)', 'wyckoff_bias': 'BUY'}

    # --- UPTHRUST (UT / Distribution) ---
    # La bougie perce au-dessus de la résistance récente puis clôture en dessous → bull trap
    if curr_high > recent_high and curr_close < recent_high and is_bearish:
        return {'phase': 'Distribution', 'event': 'Upthrust (UT)', 'wyckoff_bias': 'SELL'}

    # --- BUYING CLIMAX (BC) ---
    # Grande bougie haussière avec volume élevé en haut de range + tendance haussière
    if price_position > 0.75 and is_bullish and is_large_candle and high_volume and in_uptrend:
        return {'phase': 'Distribution', 'event': 'Buying Climax (BC)', 'wyckoff_bias': 'SELL'}

    # --- SIGN OF STRENGTH (SOS) ---
    # Clôture au-dessus de la résistance récente + volume élevé + tendance haussière
    if curr_close > recent_high and is_bullish and high_volume and in_uptrend:
        return {'phase': 'Markup', 'event': 'Sign of Strength (SOS)', 'wyckoff_bias': 'BUY'}

    # --- SIGN OF WEAKNESS (SOW) ---
    # Clôture en dessous du support récent + volume élevé + tendance baissière
    if curr_close < recent_low and is_bearish and high_volume and in_downtrend:
        return {'phase': 'Markdown', 'event': 'Sign of Weakness (SOW)', 'wyckoff_bias': 'SELL'}

    return {'phase': None, 'event': None, 'wyckoff_bias': 'NEUTRAL'}


# ─────────────────────────────────────────────────────────────────────────────
# SMART MONEY CONCEPT (SMC) — LOGIQUE INSTITUTIONNELLE COMPLÈTE
# ─────────────────────────────────────────────────────────────────────────────

def detect_swing_points(df, window=3):
    highs, lows = [], []
    n = len(df)
    limit = min(n, 50)
    start = n - limit
    for i in range(start + window, n - window):
        h = df['high'].iloc[i]
        l = df['low'].iloc[i]
        if all(h >= df['high'].iloc[i - j] for j in range(1, window + 1)) and \
           all(h >= df['high'].iloc[i + j] for j in range(1, window + 1)):
            highs.append((i, h))
        if all(l <= df['low'].iloc[i - j] for j in range(1, window + 1)) and \
           all(l <= df['low'].iloc[i + j] for j in range(1, window + 1)):
            lows.append((i, l))
    return {'highs': highs, 'lows': lows}


def detect_market_structure(df):
    empty = {'trend': 'RANGING', 'bos': None, 'choch': None,
             'last_swing_high': None, 'last_swing_low': None,
             'prev_swing_high': None, 'prev_swing_low': None}
    if len(df) < 20:
        return empty
    swings = detect_swing_points(df, window=3)
    if len(swings['highs']) < 2 or len(swings['lows']) < 2:
        return empty
    curr_close = df['close'].iloc[-1]
    _, last_sh = swings['highs'][-1]
    _, prev_sh = swings['highs'][-2]
    _, last_sl = swings['lows'][-1]
    _, prev_sl = swings['lows'][-2]
    trend = 'RANGING'
    if last_sh > prev_sh and last_sl > prev_sl:
        trend = 'BULLISH'
    elif last_sh < prev_sh and last_sl < prev_sl:
        trend = 'BEARISH'
    bos = None
    if curr_close > last_sh:
        bos = 'Bullish BOS'
    elif curr_close < last_sl:
        bos = 'Bearish BOS'
    choch = None
    if bos == 'Bullish BOS' and trend == 'BEARISH':
        choch = 'ChoCH Bullish'
    elif bos == 'Bearish BOS' and trend == 'BULLISH':
        choch = 'ChoCH Bearish'
    return {'trend': trend, 'bos': bos, 'choch': choch,
            'last_swing_high': last_sh, 'last_swing_low': last_sl,
            'prev_swing_high': prev_sh, 'prev_swing_low': prev_sl}


def detect_true_order_block(df, structure):
    if len(df) < 10 or not structure.get('bos'):
        return None
    curr_close = df['close'].iloc[-1]
    curr_low   = df['low'].iloc[-1]
    curr_high  = df['high'].iloc[-1]
    bos        = structure['bos']
    window     = min(15, len(df) - 2)
    if bos == 'Bullish BOS':
        for i in range(-2, -window - 1, -1):
            if df['close'].iloc[i] < df['open'].iloc[i]:
                ob_top    = df['high'].iloc[i]
                ob_bottom = df['low'].iloc[i]
                mitigated = curr_low < ob_bottom
                retesting = ob_bottom <= curr_close <= ob_top * 1.002
                if not mitigated:
                    return {'type': 'Bullish OB', 'top': ob_top, 'bottom': ob_bottom,
                            'retesting': retesting, 'mitigated': False}
                break
    elif bos == 'Bearish BOS':
        for i in range(-2, -window - 1, -1):
            if df['close'].iloc[i] > df['open'].iloc[i]:
                ob_top    = df['high'].iloc[i]
                ob_bottom = df['low'].iloc[i]
                mitigated = curr_high > ob_top
                retesting = ob_bottom * 0.998 <= curr_close <= ob_top
                if not mitigated:
                    return {'type': 'Bearish OB', 'top': ob_top, 'bottom': ob_bottom,
                            'retesting': retesting, 'mitigated': False}
                break
    return None


def detect_liquidity(df, structure):
    result = {'bsl': None, 'ssl': None, 'bsl_swept': False, 'ssl_swept': False,
              'eqh': False, 'eql': False, 'bias': 'NEUTRAL'}
    if len(df) < 20:
        return result
    last_sh = structure.get('last_swing_high')
    last_sl = structure.get('last_swing_low')
    prev_sh = structure.get('prev_swing_high')
    prev_sl = structure.get('prev_swing_low')
    if not last_sh or not last_sl:
        return result
    curr_close = df['close'].iloc[-1]
    curr_high  = df['high'].iloc[-1]
    curr_low   = df['low'].iloc[-1]
    result['bsl'] = last_sh
    result['ssl'] = last_sl
    result['bsl_swept'] = curr_high > last_sh and curr_close < last_sh
    result['ssl_swept'] = curr_low  < last_sl and curr_close > last_sl
    if prev_sh:
        result['eqh'] = abs(last_sh - prev_sh) / max(prev_sh, 1e-9) < 0.001
    if prev_sl:
        result['eql'] = abs(last_sl - prev_sl) / max(prev_sl, 1e-9) < 0.001
    if result['ssl_swept']:
        result['bias'] = 'BUY'
    elif result['bsl_swept']:
        result['bias'] = 'SELL'
    return result


def detect_premium_discount(df, structure):
    last_sh = structure.get('last_swing_high')
    last_sl = structure.get('last_swing_low')
    if not last_sh or not last_sl:
        return {'zone': 'NEUTRAL', 'ote': False, 'price_pct': 50.0, 'fib_level': None}
    curr_close  = df['close'].iloc[-1]
    swing_range = last_sh - last_sl
    if swing_range <= 0:
        return {'zone': 'NEUTRAL', 'ote': False, 'price_pct': 50.0, 'fib_level': None}
    price_pct = max(0.0, min(100.0, (curr_close - last_sl) / swing_range * 100))
    zone      = 'Discount' if price_pct < 50 else ('Premium' if price_pct > 50 else 'Equilibrium')
    fib_levels = [0, 23.6, 38.2, 50, 61.8, 70.5, 79, 88.2, 100]
    fib_level  = min(fib_levels, key=lambda x: abs(x - price_pct))
    trend = structure.get('trend', 'RANGING')
    ote = False
    if trend == 'BULLISH' and 20.0 <= price_pct <= 38.2:
        ote = True
    elif trend == 'BEARISH' and 61.8 <= price_pct <= 80.0:
        ote = True
    return {'zone': zone, 'ote': ote, 'price_pct': round(price_pct, 1), 'fib_level': fib_level}


def detect_displacement(df, indicators):
    if len(df) < 4:
        return {'detected': False, 'direction': None}
    atr = indicators.get('ATR')
    if not atr or atr == 0:
        return {'detected': False, 'direction': None}
    c = df['close'].iloc[-1]
    o = df['open'].iloc[-1]
    if abs(c - o) > atr * 1.5:
        return {'detected': True, 'direction': 'BUY' if c > o else 'SELL'}
    move = abs(df['close'].iloc[-1] - df['open'].iloc[-4])
    if move > atr * 2.0:
        direction = 'BUY' if df['close'].iloc[-1] > df['open'].iloc[-4] else 'SELL'
        return {'detected': True, 'direction': direction}
    return {'detected': False, 'direction': None}


# ─────────────────────────────────────────────────────────────────────────────
# LOI DE LA MAIN DOMINANTE — BIAIS JOURNALIER
# ─────────────────────────────────────────────────────────────────────────────

def detect_daily_bias(df_d1, df_h4):
    """
    Établit le biais directionnel du jour (D1 + H4 doivent être alignés).

    D1 : Structure macro (HH/HL vs LH/LL) + position par rapport EMA50.
    H4 : Structure récente (6 dernières bougies) + position EMA20.

    Règle absolue : si D1 et H4 ne s'accordent pas → NEUTRAL = pas de trade.
    C'est la loi de la main dominante : ne jamais trader contre le flux institutionnel.
    """
    if df_d1 is None or df_h4 is None or len(df_d1) < 55 or len(df_h4) < 25:
        return 'NEUTRAL'

    # ── D1 bias ─────────────────────────────────────────────────────────────
    ema50_d1 = ta.ema(df_d1['close'], length=50)
    if ema50_d1 is None or pd.isna(ema50_d1.iloc[-1]):
        return 'NEUTRAL'

    d1_close  = float(df_d1['close'].iloc[-1])
    d1_ema50  = float(ema50_d1.iloc[-1])

    # Higher Highs & Higher Lows on D1 (last 5 candles)
    d1_hi = df_d1['high'].iloc[-5:]
    d1_lo = df_d1['low'].iloc[-5:]
    d1_hh = float(d1_hi.iloc[-1]) > float(d1_hi.iloc[-3])
    d1_hl = float(d1_lo.iloc[-1]) > float(d1_lo.iloc[-3])
    d1_lh = float(d1_hi.iloc[-1]) < float(d1_hi.iloc[-3])
    d1_ll = float(d1_lo.iloc[-1]) < float(d1_lo.iloc[-3])

    d1_bullish = d1_close > d1_ema50 and d1_hh and d1_hl
    d1_bearish = d1_close < d1_ema50 and d1_lh and d1_ll

    # ── H4 bias ─────────────────────────────────────────────────────────────
    ema20_h4 = ta.ema(df_h4['close'], length=20)
    if ema20_h4 is None or pd.isna(ema20_h4.iloc[-1]):
        return 'NEUTRAL'

    h4_close = float(df_h4['close'].iloc[-1])
    h4_ema20 = float(ema20_h4.iloc[-1])

    h4_hi = df_h4['high'].iloc[-6:]
    h4_lo = df_h4['low'].iloc[-6:]
    h4_hh = float(h4_hi.iloc[-1]) > float(h4_hi.iloc[-3])
    h4_hl = float(h4_lo.iloc[-1]) > float(h4_lo.iloc[-3])
    h4_lh = float(h4_hi.iloc[-1]) < float(h4_hi.iloc[-3])
    h4_ll = float(h4_lo.iloc[-1]) < float(h4_lo.iloc[-3])

    h4_bullish = h4_close > h4_ema20 and h4_hh and h4_hl
    h4_bearish = h4_close < h4_ema20 and h4_lh and h4_ll

    if d1_bullish and h4_bullish:
        return 'BUY'
    if d1_bearish and h4_bearish:
        return 'SELL'
    return 'NEUTRAL'


# ─────────────────────────────────────────────────────────────────────────────
# FVG PRÉCIS — DÉFINITION MATHÉMATIQUE + RÈGLE D'OR 50%
# ─────────────────────────────────────────────────────────────────────────────

def detect_fvg_precision(df, pair):
    """
    Définition mathématique du FVG (Fair Value Gap / Imbalance).

    FVG Haussier : Candle A (High) < Candle C (Low)   → gap entre A.high et C.low
    FVG Baissier : Candle A (Low)  > Candle C (High)  → gap entre C.high et A.low

    Règle d'Or : un FVG touché à plus de 50% est INVALIDE pour une entrée Qualité A.
    Freshness   : on recherche le FVG le plus récent dans les 15 dernières bougies.

    Returns dict with quality 'A' (fresh < 50% touched) or 'B' (partial) or None.
    """
    if len(df) < 5:
        return None

    pip  = 0.01 if 'JPY' in pair else 0.0001
    curr = float(df['close'].iloc[-1])
    n    = len(df)

    for i in range(n - 2, max(n - 16, 1), -1):
        # Candle A = i-2, Candle B = i-1 (middle), Candle C = i
        if i < 2:
            break
        a_hi = float(df['high'].iloc[i - 2])
        a_lo = float(df['low'].iloc[i - 2])
        c_hi = float(df['high'].iloc[i])
        c_lo = float(df['low'].iloc[i])

        # ── Bullish FVG: A.high < C.low ────────────────────────────────────
        if c_lo > a_hi:
            gap_bottom = a_hi
            gap_top    = c_lo
            gap_size   = gap_top - gap_bottom
            if gap_size < pip * 2:
                continue

            if curr <= gap_bottom:
                # Price still below gap → untouched → Quality A
                touched_pct = 0.0
                quality = 'A'
            elif curr <= gap_top:
                touched_pct = (curr - gap_bottom) / gap_size * 100
                quality = 'A' if touched_pct < 50 else 'B'
            else:
                continue  # Fully mitigated

            return {
                'direction':   'BUY',
                'quality':     quality,
                'top':         gap_top,
                'bottom':      gap_bottom,
                'touched_pct': round(touched_pct, 1),
                'gap_pips':    round(gap_size / pip, 1),
            }

        # ── Bearish FVG: A.low > C.high ────────────────────────────────────
        elif c_hi < a_lo:
            gap_top    = a_lo
            gap_bottom = c_hi
            gap_size   = gap_top - gap_bottom
            if gap_size < pip * 2:
                continue

            if curr >= gap_top:
                touched_pct = 0.0
                quality = 'A'
            elif curr >= gap_bottom:
                touched_pct = (gap_top - curr) / gap_size * 100
                quality = 'A' if touched_pct < 50 else 'B'
            else:
                continue  # Fully mitigated

            return {
                'direction':   'SELL',
                'quality':     quality,
                'top':         gap_top,
                'bottom':      gap_bottom,
                'touched_pct': round(touched_pct, 1),
                'gap_pips':    round(gap_size / pip, 1),
            }

    return None


# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT D'INDUCEMENT (IDM) — LE PIÈGE FINAL
# ─────────────────────────────────────────────────────────────────────────────

def detect_inducement(df, direction, true_ob):
    """
    Le Concept d'Inducement — ce qui sépare l'amateur du pro.

    Avant que le prix touche l'Order Block :
    - Pour un SELL : le prix crée un swing HIGH entre le prix actuel et l'OB.
      Les amateurs SMC entrent short ici → ils se font liquider.
      Les pros attendent que ce high soit sweepé (prix passe au-dessus) PUIS short.
    - Pour un BUY  : le prix crée un swing LOW entre le prix actuel et l'OB.
      Les amateurs long ici → liquidés. Les pros attendent le sweep du low.

    Un signal sans IDM sweepé = entrée prématurée = perdant potentiel.
    Returns: {'idm_level': float|None, 'swept': bool, 'quality': str|None}
    """
    if true_ob is None or len(df) < 10:
        return {'idm_level': None, 'swept': False, 'quality': None}

    curr  = float(df['close'].iloc[-1])
    c_hi  = float(df['high'].iloc[-1])
    c_lo  = float(df['low'].iloc[-1])
    ob_top    = true_ob.get('top')
    ob_bottom = true_ob.get('bottom')

    if direction == 'BUY':
        # OB is below price — find swing low BETWEEN ob_top and curr
        if ob_top is None or ob_top >= curr:
            return {'idm_level': None, 'swept': False, 'quality': None}

        idm = None
        for i in range(len(df) - 2, max(len(df) - 25, 1), -1):
            lo = float(df['low'].iloc[i])
            if ob_top < lo < curr:
                lo_prev = float(df['low'].iloc[i - 1]) if i > 0 else lo
                lo_next = float(df['low'].iloc[i + 1]) if i < len(df) - 1 else lo
                if lo <= lo_prev and lo <= lo_next:
                    idm = lo
                    break

        if idm is None:
            return {'idm_level': None, 'swept': False, 'quality': None}

        swept = c_lo < idm
        return {'idm_level': round(idm, 5), 'swept': swept, 'quality': 'critical'}

    elif direction == 'SELL':
        # OB is above price — find swing high BETWEEN curr and ob_bottom
        if ob_bottom is None or ob_bottom <= curr:
            return {'idm_level': None, 'swept': False, 'quality': None}

        idm = None
        for i in range(len(df) - 2, max(len(df) - 25, 1), -1):
            hi = float(df['high'].iloc[i])
            if curr < hi < ob_bottom:
                hi_prev = float(df['high'].iloc[i - 1]) if i > 0 else hi
                hi_next = float(df['high'].iloc[i + 1]) if i < len(df) - 1 else hi
                if hi >= hi_prev and hi >= hi_next:
                    idm = hi
                    break

        if idm is None:
            return {'idm_level': None, 'swept': False, 'quality': None}

        swept = c_hi > idm
        return {'idm_level': round(idm, 5), 'swept': swept, 'quality': 'critical'}

    return {'idm_level': None, 'swept': False, 'quality': None}


# ─────────────────────────────────────────────────────────────────────────────
# POINT DE NON-RETOUR (PNR) — 50% DE LA BOUGIE MSS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_pnr(df, structure):
    """
    Le Point de Non-Retour = 50% du corps de la bougie de displacement (MSS).

    Règle : si le prix repasse sous ce niveau (pour BUY) → le setup est invalidé.
    Si le prix est dans la zone 0-50% de retracement → entrée encore valide.

    C'est le filtre qui évite les entrées sur des structures déjà cassées.
    Returns: {'pnr': float, 'valid': bool, 'retrace_pct': float}
    """
    if len(df) < 5 or not structure.get('bos'):
        return {'pnr': None, 'valid': True, 'retrace_pct': 0.0}

    bos  = structure['bos']
    curr = float(df['close'].iloc[-1])

    # Identify the displacement candle: largest range in last 10 bars
    last_n = min(10, len(df))
    segment = df.iloc[-last_n:]
    ranges  = segment['high'] - segment['low']
    max_idx = int(ranges.values.argmax())

    imp_hi  = float(segment['high'].iloc[max_idx])
    imp_lo  = float(segment['low'].iloc[max_idx])
    imp_rng = imp_hi - imp_lo

    if imp_rng == 0:
        return {'pnr': None, 'valid': True, 'retrace_pct': 0.0}

    pnr = (imp_hi + imp_lo) / 2  # 50% of the impulse candle

    if bos == 'Bullish BOS':
        retrace_pct = max(0.0, (imp_hi - curr) / imp_rng * 100)
        valid = curr > pnr  # Must stay above 50% of the MSS candle
    elif bos == 'Bearish BOS':
        retrace_pct = max(0.0, (curr - imp_lo) / imp_rng * 100)
        valid = curr < pnr  # Must stay below 50% of the MSS candle
    else:
        return {'pnr': None, 'valid': True, 'retrace_pct': 0.0}

    return {'pnr': round(pnr, 5), 'valid': valid, 'retrace_pct': round(retrace_pct, 1)}


# ─────────────────────────────────────────────────────────────────────────────
# RÈGLES DE LA BOUGIE INSTITUTIONNELLE
# ─────────────────────────────────────────────────────────────────────────────

def detect_institutional_candle(df):
    """
    Une bougie institutionnelle valide doit respecter ces règles :
    - Corps (body) ≥ 60% du range total  → pas de doji, spinning top
    - Clôture dans les 25% supérieurs (BUY) ou inférieurs (SELL) du range
    - Volume > 1.2× moyenne des 10 bougies précédentes
    - Corps de préférence sans mèches dominantes contre la direction

    Returns: {'valid': bool, 'direction': str|None, 'body_ratio': float}
    """
    if len(df) < 12:
        return {'valid': False, 'direction': None, 'body_ratio': 0.0}

    c   = float(df['close'].iloc[-1])
    o   = float(df['open'].iloc[-1])
    hi  = float(df['high'].iloc[-1])
    lo  = float(df['low'].iloc[-1])
    vol = float(df['tick_volume'].iloc[-1])

    rng = hi - lo
    if rng == 0:
        return {'valid': False, 'direction': None, 'body_ratio': 0.0}

    body       = abs(c - o)
    body_ratio = body / rng
    avg_vol    = float(df['tick_volume'].iloc[-12:-1].mean())
    high_vol   = vol > avg_vol * 1.2

    if body_ratio < 0.60:
        return {'valid': False, 'direction': None, 'body_ratio': round(body_ratio, 2)}

    # BUY: bullish candle closing in top 25% of range
    if c > o and (c - lo) / rng >= 0.75 and high_vol:
        return {'valid': True, 'direction': 'BUY', 'body_ratio': round(body_ratio, 2)}

    # SELL: bearish candle closing in bottom 25% of range
    if c < o and (hi - c) / rng >= 0.75 and high_vol:
        return {'valid': True, 'direction': 'SELL', 'body_ratio': round(body_ratio, 2)}

    return {'valid': False, 'direction': None, 'body_ratio': round(body_ratio, 2)}


# ─────────────────────────────────────────────────────────────────────────────
# SESSION ALGORITHM — TIME & PRICE
# ─────────────────────────────────────────────────────────────────────────────

def is_quality_session():
    """
    L'algorithme des sessions institutionnelles (Time & Price).

    Les institutions frappent TOUJOURS pendant les ouvertures de session :
    - London Open  07:00-09:00 GMT → Qualité A (sweep asiatique + trend du jour)
    - NY Open      13:00-15:00 GMT → Qualité A (overlap + max volume + reversions)
    - London Close 15:00-16:00 GMT → Qualité B (take profit institutionnel)
    - Asian Sweep  02:00-04:00 GMT → Qualité B (range asiatique → niveaux pour London)

    EN DEHORS de ces fenêtres → pas de signal day trading.
    """
    h = datetime.datetime.utcnow().hour
    if  7 <= h <  9: return {'active': True,  'name': 'London Open',  'quality': 'A'}
    if 13 <= h < 15: return {'active': True,  'name': 'New York Open', 'quality': 'A'}
    if 15 <= h < 16: return {'active': True,  'name': 'London Close',  'quality': 'B'}
    if  2 <= h <  4: return {'active': True,  'name': 'Asian Sweep',   'quality': 'B'}
    return {'active': False, 'name': None, 'quality': None}


def is_kill_zone():
    """Legacy alias — kept for backward-compat. Redirects to is_quality_session()."""
    return is_quality_session()


def get_target_levels(entry, sl, direction):
    """Day-trading R/R: TP1=2R, TP2=3R, TP3=5R — minimum 1:2 reward."""
    distance = abs(entry - sl)
    if distance == 0:
        return None, None, None
    if direction == 'BUY':
        return entry + distance * 2.0, entry + distance * 3.0, entry + distance * 5.0
    if direction == 'SELL':
        return entry - distance * 2.0, entry - distance * 3.0, entry - distance * 5.0
    return None, None, None


# Hard SL cap per pair type (day trading: never risk more than this in pips)
_SL_MAX_PIPS = {
    'default': 20,   # EUR/USD, GBP/USD, AUD/USD, NZD/USD, USD/CAD, USD/CHF
    'jpy':     32,   # All JPY pairs (price ~100-160, pips = 0.01)
    'exotic':  26,   # GBPNZD, GBPAUD, EURNZD, EURAUD, GBPCHF, GBPCAD
}

def _max_sl_pips(pair: str) -> int:
    if 'JPY' in pair:
        return _SL_MAX_PIPS['jpy']
    if pair in ('GBPNZD', 'GBPAUD', 'EURNZD', 'EURAUD', 'GBPCHF', 'GBPCAD', 'GBPJPY'):
        return _SL_MAX_PIPS['exotic']
    return _SL_MAX_PIPS['default']


def choose_levels(current_price, direction, indicators, smc_data=None, pair=''):
    pivot = indicators.get('Pivot.M.Classic.Middle', None)
    r1 = indicators.get('Pivot.M.Classic.R1', None)
    r2 = indicators.get('Pivot.M.Classic.R2', None)
    s1 = indicators.get('Pivot.M.Classic.S1', None)
    s2 = indicators.get('Pivot.M.Classic.S2', None)
    levels    = {'pivot': pivot, 'r1': r1, 'r2': r2, 's1': s1, 's2': s2}
    atr       = indicators.get('ATR')
    true_ob   = smc_data.get('true_ob')   if smc_data else None
    liquidity = smc_data.get('liquidity') if smc_data else None

    if direction == 'BUY':
        if true_ob and true_ob['type'] == 'Bullish OB' and true_ob['bottom'] < current_price:
            sl = true_ob['bottom'] - (atr * 0.3 if atr else current_price * 0.001)
        else:
            supports = [l for l in [s2, s1, pivot] if l is not None and l < current_price]
            sl = max(supports) if supports else current_price * 0.997
            if atr and (current_price - sl) < atr:
                sl = current_price - atr
        if liquidity and liquidity.get('bsl') and liquidity['bsl'] > current_price:
            levels['smc_tp_target'] = liquidity['bsl']

    elif direction == 'SELL':
        if true_ob and true_ob['type'] == 'Bearish OB' and true_ob['top'] > current_price:
            sl = true_ob['top'] + (atr * 0.3 if atr else current_price * 0.001)
        else:
            resistances = [l for l in [r2, r1, pivot] if l is not None and l > current_price]
            sl = min(resistances) if resistances else current_price * 1.003
            if atr and (sl - current_price) < atr:
                sl = current_price + atr
        if liquidity and liquidity.get('ssl') and liquidity['ssl'] < current_price:
            levels['smc_tp_target'] = liquidity['ssl']

    else:
        sl = None

    # ── Hard SL cap: enforce day-trading pip limit ──────────────────────────
    # If the OB or pivot-based SL is too far, tighten it.
    # Prefer ATR × 1.3 if within the cap; otherwise use the hard cap directly.
    if sl is not None and direction in ('BUY', 'SELL'):
        pip          = 0.01 if 'JPY' in pair else 0.0001
        max_dist     = _max_sl_pips(pair) * pip
        sl_dist      = (current_price - sl) if direction == 'BUY' else (sl - current_price)

        if sl_dist > max_dist:
            # Tighten: use ATR × 1.3 if it fits, otherwise use the hard cap
            if atr and atr * 1.3 <= max_dist:
                tight = atr * 1.3
            else:
                tight = max_dist
            sl = (current_price - tight) if direction == 'BUY' else (current_price + tight)

    return sl, levels


def format_pair_message(pair, direction, score, rationale, entry, sl, t1, t2, t3,
                        current_price, pd_info=None, kz_info=None):
    direction_icon = '🟢' if direction == 'BUY' else '🔴'
    if direction == 'NEUTRAL':
        return (
            f"<b>{pair} ⚪ NEUTRAL</b> — <i>{score}/100</i>\n"
            f"<b>Prix actuel:</b> <code>{current_price:.5f}</code>\n"
            f"<b>Raison:</b> {rationale}"
        )

    sl_dist = abs(sl - entry) or 1e-9
    rr1 = abs(t1 - entry)
    rr2 = abs(t2 - entry)
    rr3 = abs(t3 - entry)

    # SL distance in pips for transparency
    pip     = 0.01 if len(pair) >= 6 and pair[3:6] in ('JPY',) or pair[:3] in ('JPY',) or 'JPY' in pair else 0.0001
    sl_pips = sl_dist / pip

    zone_line = ''
    if pd_info and pd_info.get('zone') not in (None, 'NEUTRAL'):
        zone_icon = '🔵' if pd_info['zone'] == 'Discount' else '🔴'
        ote_str   = ' ✨ <b>OTE</b>' if pd_info.get('ote') else ''
        zone_line = (f"\n<b>Zone SMC:</b> {zone_icon} {pd_info['zone']} "
                     f"({pd_info['price_pct']:.1f}% | Fib {pd_info['fib_level']}%){ote_str}")

    kz_line = ''
    if kz_info and kz_info.get('active'):
        kz_line = f"\n<b>Kill Zone:</b> {kz_info['name']}"

    # Signal validity: day trade — max 3 hours from now
    validity = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime('%H:%M')

    return (
        f"<b>{pair} {direction_icon} {direction}</b> — <i>{score}/100</i>\n"
        f"<b>Entrée:</b> <code>{entry:.5f}</code>\n"
        f"<b>SL:</b> <code>{sl:.5f}</code> <i>({sl_pips:.0f} pips)</i>\n"
        f"<b>TP1:</b> <code>{t1:.5f}</code> ({rr1/sl_dist:.1f}R) | "
        f"<b>TP2:</b> <code>{t2:.5f}</code> ({rr2/sl_dist:.1f}R) | "
        f"<b>TP3:</b> <code>{t3:.5f}</code> ({rr3/sl_dist:.1f}R)"
        f"{zone_line}"
        f"{kz_line}\n"
        f"<b>Valide jusqu'à:</b> {validity} GMT\n"
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

    # ── Confluences — bonus réduit pour éviter l'inflation de score ──────────
    # Chaque bonus est calibré : seul une vraie confluence institutionnelle
    # doit faire monter le score. Le total max hors alignment = ~63 pts.
    bonus = 0
    if any(r['psych'] for r in pair_results):
        bonus += 5   # niveau psychologique proche (était 8)
    if any(r['ob'] for r in pair_results):
        bonus += 4   # order block classique (était 6)
    if any(r['zones'] for r in pair_results):
        bonus += 3   # zone S/R (était 6)
    if any(r['fvg'] for r in pair_results):
        bonus += 3   # Fair Value Gap (était 5)

    wyckoff_aligned = [r['wyckoff'] for r in pair_results
                       if r.get('wyckoff') and r['wyckoff']['wyckoff_bias'] == direction]
    wyckoff_opposed = [r['wyckoff'] for r in pair_results
                       if r.get('wyckoff') and r['wyckoff']['wyckoff_bias'] not in ('NEUTRAL', direction)]
    if wyckoff_aligned:
        bonus += 8   # Wyckoff aligné (était 12)

    bos_aligned = [r['structure'] for r in pair_results
                   if r.get('structure') and (
                       (r['structure'].get('bos') == 'Bullish BOS' and direction == 'BUY') or
                       (r['structure'].get('bos') == 'Bearish BOS' and direction == 'SELL'))]
    choch_aligned = [r['structure'] for r in pair_results
                     if r.get('structure') and (
                         (r['structure'].get('choch') == 'ChoCH Bullish' and direction == 'BUY') or
                         (r['structure'].get('choch') == 'ChoCH Bearish' and direction == 'SELL'))]
    if bos_aligned:
        bonus += 6   # BOS confirmé (était 10)
    if choch_aligned:
        bonus += 10  # ChoCH = renversement de structure, signal fort (était 15)

    liq_aligned = [r['liquidity'] for r in pair_results
                   if r.get('liquidity') and r['liquidity'].get('bias') == direction]
    liq_opposed = [r['liquidity'] for r in pair_results
                   if r.get('liquidity') and r['liquidity'].get('bias') not in ('NEUTRAL', direction)
                   and r['liquidity'].get('bias')]
    if liq_aligned:
        bonus += 8   # sweep de liquidité aligné (était 12)

    true_ob_aligned = [r['true_ob'] for r in pair_results
                       if r.get('true_ob') and (
                           (r['true_ob']['type'] == 'Bullish OB' and direction == 'BUY') or
                           (r['true_ob']['type'] == 'Bearish OB' and direction == 'SELL'))]
    if true_ob_aligned:
        bonus += 7   # OB institutionnel aligné (était 10)
        if any(ob.get('retesting') for ob in true_ob_aligned):
            bonus += 5  # prix actuellement EN RETEST de l'OB → entrée précise

    pd_correct = [r['premium_discount'] for r in pair_results
                  if r.get('premium_discount') and (
                      (r['premium_discount']['zone'] == 'Discount' and direction == 'BUY') or
                      (r['premium_discount']['zone'] == 'Premium' and direction == 'SELL'))]
    pd_ote     = [r['premium_discount'] for r in pair_results
                  if r.get('premium_discount') and r['premium_discount'].get('ote')]
    pd_wrong   = [r['premium_discount'] for r in pair_results
                  if r.get('premium_discount') and (
                      (r['premium_discount']['zone'] == 'Premium'  and direction == 'BUY') or
                      (r['premium_discount']['zone'] == 'Discount' and direction == 'SELL'))]
    if pd_correct:
        bonus += 5   # zone P/D correcte (était 8)
    if pd_ote:
        bonus += 7   # OTE = entrée optimale Fibonacci 61.8-79% (était 10)

    disp_aligned = [r['displacement'] for r in pair_results
                    if r.get('displacement') and r['displacement'].get('detected')
                    and r['displacement'].get('direction') == direction]
    if disp_aligned:
        bonus += 5   # displacement institutionnel (était 8)

    score += bonus

    if any(r['recommendation'] == direction for r in pair_results if direction != 'NEUTRAL'):
        score += 4   # au moins 1 TF confirm la direction (était 5)
    if any(r['recommendation'] == 'NEUTRAL' for r in pair_results):
        score -= 4

    # Pénalités
    if wyckoff_opposed and not wyckoff_aligned:
        score -= 10
    if pd_wrong and not pd_correct:
        score -= 18  # entrer en Premium pour un BUY = faute institutionnelle grave
    if liq_opposed and not liq_aligned:
        score -= 8

    # ── H1 vs M15 conflict: mauvais timing d'entrée intraday ─────────────────
    tf_map = {r['tf']: r['recommendation'] for r in pair_results}
    h1_dir  = tf_map.get(Interval.INTERVAL_1_HOUR, 'NEUTRAL')
    m15_dir = tf_map.get(Interval.INTERVAL_15_MINUTES, 'NEUTRAL')
    if (h1_dir == 'BUY'  and m15_dir == 'SELL') or \
       (h1_dir == 'SELL' and m15_dir == 'BUY'):
        score -= 12  # H1 et M15 s'opposent → pas d'entrée day trading fiable

    score = max(min(score, 100), 10)
    if direction == 'NEUTRAL' and score > 55:
        score = 55

    # SUPPRESSION du plancher artificiel (était: score < 40 → 40)
    # Un signal faible doit rester faible — le plancher gonflait les scores.

    major = [r for r in pair_results if r['tf'] in (Interval.INTERVAL_1_DAY, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_HOUR)]
    major_buy  = sum(1 for r in major if r['recommendation'] == 'BUY')
    major_sell = sum(1 for r in major if r['recommendation'] == 'SELL')
    if direction == 'BUY'  and major_buy  < 2: score -= 10
    if direction == 'SELL' and major_sell < 2: score -= 10

    score = max(score, 10)
    if score < 50:
        direction = 'NEUTRAL'

    rationale = []
    if direction == 'BUY':
        rationale.append('Structure haussière principale')
    elif direction == 'SELL':
        rationale.append('Structure baissière principale')
    else:
        rationale.append('Pas de consensus clair')

    if choch_aligned:
        rationale.append(f"ChoCH {choch_aligned[0].get('choch', '')}")
    elif bos_aligned:
        rationale.append(f"BOS {bos_aligned[0].get('bos', '')}")
    if liq_aligned:
        sweep = 'SSL Sweep' if liq_aligned[0].get('ssl_swept') else 'BSL Sweep'
        eqh_eql = ' [EQL]' if liq_aligned[0].get('eql') else (' [EQH]' if liq_aligned[0].get('eqh') else '')
        rationale.append(f"Liquidité {sweep}{eqh_eql}")
    if true_ob_aligned:
        retest_str = ' (retest)' if true_ob_aligned[0].get('retesting') else ' (frais)'
        ob_label   = 'OB Haussier' if true_ob_aligned[0]['type'] == 'Bullish OB' else 'OB Baissier'
        rationale.append(f"Order Block {ob_label}{retest_str}")
    if pd_ote:
        rationale.append(f"OTE {pd_ote[0]['price_pct']:.1f}% (Fib {pd_ote[0]['fib_level']}%)")
    elif pd_correct:
        rationale.append(f"Zone {pd_correct[0]['zone']} ({pd_correct[0]['price_pct']:.1f}%)")
    if wyckoff_aligned:
        rationale.append(f"Wyckoff {wyckoff_aligned[0]['event']}")
    if disp_aligned:
        rationale.append('Displacement institutionnel')
    if any(r['fvg'] for r in pair_results):
        rationale.append('FVG')
    if any(r['psych'] for r in pair_results):
        rationale.append('Niveau psychologique')
    if pd_wrong and not pd_correct:
        rationale.append('⚠️ Zone défavorable')

    return direction, score, ' ; '.join(rationale[:5])


def scan_signals_headless():
    """
    Headless SMC scanner — institutional grade.

    Gate system (each gate must pass for a signal to be generated):
      Gate 1 — Session    : London Open or NY Open only (Quality A/B)
      Gate 2 — Daily Bias : D1 + H4 must agree (loi de la main dominante)
      Gate 3 — Direction  : signal direction must match the daily bias
      Gate 4 — FVG        : if FVG present, must be Quality A (< 50% touched)
      Gate 5 — Inducement : IDM must be swept (or no IDM = entry near OB)
      Gate 6 — PNR        : price must be above/below 50% of MSS candle
      Gate 7 — Score      : ≥ 78 after historical adjustment
      Gate 8 — R/R        : SL 5-32 pips, TP1 reachable within session

    Max 3 signals sent per scan (ranked by score).
    """
    logger.info("=== STARTING SMC SCAN ===")
    if not initialize_mt5():
        logger.error("Failed to initialize MT5")
        return

    # ── Gate 1: Session check (global — if outside session, abort scan) ──────
    session = is_quality_session()
    if not session['active']:
        logger.info("Outside trading session (London/NY). No scan needed.")
        mt5.shutdown()
        return
    logger.info(f"Session: {session['name']} (Quality {session['quality']})")

    pending   = []   # candidate signals collected before final ranking
    pair_index = 0
    total_pairs  = len(PAIRS)
    total_batches = ceil(total_pairs / BATCH_SIZE)

    try:
        for pair in PAIRS:
            pair_index += 1
            batch_index = ceil(pair_index / BATCH_SIZE)
            logger.info(f"[{pair}] ({pair_index}/{total_pairs})")

            # ── Collect per-TF data, save DataFrames for SMC analysis ────────
            pair_results  = []
            dfs           = {}
            last_indicators   = None
            last_current_price = 0

            for tf in TIMEFRAMES:
                mt5_tf = MT5_TIMEFRAMES[tf]
                df = get_mt5_data(pair, mt5_tf)
                if df is None or df.empty:
                    time.sleep(API_REQUEST_DELAY)
                    continue

                dfs[tf] = df
                indicators     = compute_indicators(df)
                recommendation = compute_recommendation(indicators)
                current_price  = indicators['close']
                last_indicators    = indicators
                last_current_price = current_price

                psych        = is_psychological_level(current_price, pair)
                zones        = detect_support_resistance(current_price, indicators)
                ob           = detect_order_block(indicators, current_price, zones)
                fvg          = detect_fvg(current_price, indicators, zones)
                wyckoff      = detect_wyckoff_phase(df, indicators)
                structure    = detect_market_structure(df)
                true_ob      = detect_true_order_block(df, structure)
                liquidity    = detect_liquidity(df, structure)
                premium_disc = detect_premium_discount(df, structure)
                displacement = detect_displacement(df, indicators)

                pair_results.append({
                    'tf': tf, 'df': df, 'recommendation': recommendation,
                    'psych': psych, 'ob': ob, 'zones': zones, 'fvg': fvg,
                    'wyckoff': wyckoff, 'structure': structure, 'true_ob': true_ob,
                    'liquidity': liquidity, 'premium_discount': premium_disc,
                    'displacement': displacement
                })
                time.sleep(API_REQUEST_DELAY)

            if not pair_results or last_indicators is None:
                continue

            # ── Gate 2: Daily Bias ────────────────────────────────────────────
            df_d1 = dfs.get(Interval.INTERVAL_1_DAY)
            df_h4 = dfs.get(Interval.INTERVAL_4_HOURS)
            daily_bias = detect_daily_bias(df_d1, df_h4)
            if daily_bias == 'NEUTRAL':
                logger.info(f"  [{pair}] SKIP — No clear daily bias (D1/H4 conflict)")
                continue

            # ── Core scoring ──────────────────────────────────────────────────
            direction, score, rationale = compute_pair_score(pair_results)

            # ── Gate 3: Direction must match daily bias ───────────────────────
            if direction == 'NEUTRAL' or direction != daily_bias:
                logger.info(f"  [{pair}] SKIP — Signal {direction} ≠ bias {daily_bias}")
                continue

            # ── Best SMC data ─────────────────────────────────────────────────
            best_true_ob   = next((r['true_ob']  for r in pair_results if r.get('true_ob')),  None)
            best_liquidity = next((r['liquidity'] for r in pair_results
                                   if r.get('liquidity') and r['liquidity'].get('bsl')), None)
            best_pd = next((r['premium_discount'] for r in pair_results
                            if r.get('premium_discount') and r['premium_discount']['zone'] != 'NEUTRAL'), None)

            # ── Gate 4: FVG quality — Règle d'Or 50% ─────────────────────────
            # Use the best entry TF (M15 → H1 → H4)
            df_entry = dfs.get(Interval.INTERVAL_15_MINUTES) or \
                       dfs.get(Interval.INTERVAL_1_HOUR)     or \
                       dfs.get(Interval.INTERVAL_4_HOURS)

            fvg_precision = detect_fvg_precision(df_entry, pair) if df_entry is not None else None
            if fvg_precision is not None:
                if fvg_precision['direction'] == direction and fvg_precision['quality'] == 'B':
                    # FVG >50% touched → degraded quality, penalise score
                    score -= 8
                    logger.info(f"  [{pair}] FVG Quality B ({fvg_precision['touched_pct']:.0f}% touched) -8")
                elif fvg_precision['direction'] != direction:
                    # FVG goes against the bias → penalise
                    score -= 5

            # ── Gate 5: Inducement (IDM) swept? ──────────────────────────────
            idm = detect_inducement(df_entry, direction, best_true_ob) if df_entry is not None \
                  else {'idm_level': None, 'swept': False, 'quality': None}

            if idm['idm_level'] is not None and not idm['swept']:
                # IDM exists but NOT yet swept → entry is premature (amateur trap)
                logger.info(f"  [{pair}] SKIP — IDM at {idm['idm_level']:.5f} not yet swept")
                continue

            if idm['swept']:
                score += 8   # IDM swept = institutional confirmation
                rationale += ' ; IDM Swept'

            # ── Gate 6: Point de Non-Retour ───────────────────────────────────
            best_structure = next((r['structure'] for r in pair_results
                                   if r.get('structure') and r['structure'].get('bos')), None)
            pnr = calculate_pnr(df_entry, best_structure) if (df_entry is not None and best_structure) \
                  else {'pnr': None, 'valid': True, 'retrace_pct': 0.0}

            if not pnr['valid']:
                logger.info(f"  [{pair}] SKIP — PNR breached ({pnr['retrace_pct']:.0f}% retraced)")
                continue

            # ── Institutional candle quality ──────────────────────────────────
            inst_candle = detect_institutional_candle(df_entry) if df_entry is not None \
                          else {'valid': False, 'direction': None}
            if inst_candle['valid'] and inst_candle['direction'] == direction:
                score += 5   # Confirmed by institutional candle pattern
            elif inst_candle['valid'] and inst_candle['direction'] != direction:
                score -= 5

            # ── Session bonus ─────────────────────────────────────────────────
            if session['quality'] == 'A':
                score = min(score + 6, 100)
            elif session['quality'] == 'B':
                score = min(score + 3, 100)

            # ── Historical adjustment ─────────────────────────────────────────
            hist_adj = get_historical_adjustment(
                pair, last_current_price, best_pd, session,
                direction, HIST_STATS,
                has_fvg=fvg_precision is not None
            )
            if hist_adj != 0:
                score = max(min(score + hist_adj, 100), 10)

            score = max(min(score, 100), 10)

            # ── Gate 7: Score threshold ───────────────────────────────────────
            if score < 78:
                logger.info(f"  [{pair}] SKIP — score {score} < 78")
                continue

            # ── Gate 8: SL/TP validation ──────────────────────────────────────
            sl, levels = choose_levels(last_current_price, direction, last_indicators,
                                       smc_data={'true_ob': best_true_ob, 'liquidity': best_liquidity},
                                       pair=pair)
            if sl is None:
                continue

            pip     = 0.01 if 'JPY' in pair else 0.0001
            sl_pips = abs(last_current_price - sl) / pip
            atr_m15 = (last_indicators.get('ATR') or 0) / pip

            if sl_pips < 5:
                logger.info(f"  [{pair}] SKIP — SL {sl_pips:.1f}p too tight")
                continue

            tp1_pips = sl_pips * 2.0
            if atr_m15 > 0 and tp1_pips > atr_m15 * 10:
                logger.info(f"  [{pair}] SKIP — TP1 {tp1_pips:.0f}p unreachable")
                continue

            t1, t2, t3 = get_target_levels(last_current_price, sl, direction)
            if t1 is None:
                continue

            # Build extra rationale lines for the message
            extra_lines = []
            if fvg_precision and fvg_precision['direction'] == direction:
                q = fvg_precision['quality']
                extra_lines.append(f"FVG Qualité {q} ({fvg_precision['gap_pips']:.0f}p | {fvg_precision['touched_pct']:.0f}% rempli)")
            if idm['swept']:
                extra_lines.append(f"IDM Swept ({idm['idm_level']:.5f})")
            if pnr['pnr']:
                extra_lines.append(f"PNR {pnr['pnr']:.5f} ({pnr['retrace_pct']:.0f}% retrace)")
            if extra_lines:
                rationale = rationale + ' ; ' + ' ; '.join(extra_lines[:2])

            message = format_pair_message(
                pair, direction, score, rationale,
                last_current_price, sl, t1, t2, t3,
                last_current_price, best_pd, session
            )

            logger.info(f"  [{pair}] CANDIDATE: {direction} {score}/100 "
                        f"| bias={daily_bias} | IDM={'swept' if idm['swept'] else 'none'} "
                        f"| session={session['name']}"
                        + (f" | hist {hist_adj:+d}" if hist_adj != 0 else ""))

            pending.append({
                'pair': pair, 'direction': direction, 'score': score,
                'message': message, 'rationale': rationale
            })

            if pair_index % BATCH_SIZE == 0 and pair_index < total_pairs:
                logger.info(f"Batch {batch_index}/{total_batches} done. Pausing {BATCH_DELAY}s...")
                time.sleep(BATCH_DELAY)

        # ── Send top-3 signals only ───────────────────────────────────────────
        pending.sort(key=lambda x: x['score'], reverse=True)
        top = pending[:3]

        if not top:
            logger.info("=== SCAN COMPLETE — No signals passed all gates ===")
        else:
            logger.info(f"=== SCAN COMPLETE — {len(top)} signal(s) selected from {len(pending)} candidates ===")
            for sig in top:
                send_telegram_message(sig['message'])
                logger.info(f"  SENT: {sig['pair']} {sig['direction']} {sig['score']}/100")
                time.sleep(PAIR_DELAY)

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
