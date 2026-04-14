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


def is_kill_zone():
    h = datetime.datetime.utcnow().hour
    if  7 <= h < 10: return {'active': True,  'name': 'London Kill Zone'}
    if 12 <= h < 15: return {'active': True,  'name': 'New York Kill Zone'}
    if 15 <= h < 16: return {'active': True,  'name': 'London Close'}
    if  0 <= h <  4: return {'active': True,  'name': 'Asian Kill Zone'}
    return {'active': False, 'name': None}


def get_target_levels(entry, sl, direction):
    distance = abs(entry - sl)
    if distance == 0:
        return None, None, None
    if direction == 'BUY':
        return entry + distance, entry + 2 * distance, entry + 3 * distance
    if direction == 'SELL':
        return entry - distance, entry - 2 * distance, entry - 3 * distance
    return None, None, None


def choose_levels(current_price, direction, indicators, smc_data=None):
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

    zone_line = ''
    if pd_info and pd_info.get('zone') not in (None, 'NEUTRAL'):
        zone_icon = '🔵' if pd_info['zone'] == 'Discount' else '🔴'
        ote_str   = ' ✨ <b>OTE</b>' if pd_info.get('ote') else ''
        zone_line = (f"\n<b>Zone SMC:</b> {zone_icon} {pd_info['zone']} "
                     f"({pd_info['price_pct']:.1f}% | Fib {pd_info['fib_level']}%){ote_str}")

    kz_line = ''
    if kz_info and kz_info.get('active'):
        kz_line = f"\n<b>⏰ Kill Zone:</b> {kz_info['name']}"

    return (
        f"<b>{pair} {direction_icon} {direction}</b> — <i>{score}/100</i>\n"
        f"<b>Entrée:</b> <code>{entry:.5f}</code>\n"
        f"<b>SL:</b> <code>{sl:.5f}</code>\n"
        f"<b>TP1:</b> <code>{t1:.5f}</code> | <b>TP2:</b> <code>{t2:.5f}</code> | <b>TP3:</b> <code>{t3:.5f}</code>\n"
        f"<b>R/R:</b> 1:{rr1/sl_dist:.1f} | 2:{rr2/sl_dist:.1f} | 3:{rr3/sl_dist:.1f}"
        f"{zone_line}"
        f"{kz_line}\n"
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
        bonus += 8
    if any(r['ob'] for r in pair_results):
        bonus += 6
    if any(r['zones'] for r in pair_results):
        bonus += 6
    if any(r['fvg'] for r in pair_results):
        bonus += 5

    wyckoff_aligned = [r['wyckoff'] for r in pair_results
                       if r.get('wyckoff') and r['wyckoff']['wyckoff_bias'] == direction]
    wyckoff_opposed = [r['wyckoff'] for r in pair_results
                       if r.get('wyckoff') and r['wyckoff']['wyckoff_bias'] not in ('NEUTRAL', direction)]
    if wyckoff_aligned:
        bonus += 12

    bos_aligned = [r['structure'] for r in pair_results
                   if r.get('structure') and (
                       (r['structure'].get('bos') == 'Bullish BOS' and direction == 'BUY') or
                       (r['structure'].get('bos') == 'Bearish BOS' and direction == 'SELL'))]
    choch_aligned = [r['structure'] for r in pair_results
                     if r.get('structure') and (
                         (r['structure'].get('choch') == 'ChoCH Bullish' and direction == 'BUY') or
                         (r['structure'].get('choch') == 'ChoCH Bearish' and direction == 'SELL'))]
    if bos_aligned:
        bonus += 10
    if choch_aligned:
        bonus += 15

    liq_aligned = [r['liquidity'] for r in pair_results
                   if r.get('liquidity') and r['liquidity'].get('bias') == direction]
    liq_opposed = [r['liquidity'] for r in pair_results
                   if r.get('liquidity') and r['liquidity'].get('bias') not in ('NEUTRAL', direction)
                   and r['liquidity'].get('bias')]
    if liq_aligned:
        bonus += 12

    true_ob_aligned = [r['true_ob'] for r in pair_results
                       if r.get('true_ob') and (
                           (r['true_ob']['type'] == 'Bullish OB' and direction == 'BUY') or
                           (r['true_ob']['type'] == 'Bearish OB' and direction == 'SELL'))]
    if true_ob_aligned:
        bonus += 10
        if any(ob.get('retesting') for ob in true_ob_aligned):
            bonus += 5

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
        bonus += 8
    if pd_ote:
        bonus += 10

    disp_aligned = [r['displacement'] for r in pair_results
                    if r.get('displacement') and r['displacement'].get('detected')
                    and r['displacement'].get('direction') == direction]
    if disp_aligned:
        bonus += 8

    score += bonus

    if any(r['recommendation'] == direction for r in pair_results if direction != 'NEUTRAL'):
        score += 5
    if any(r['recommendation'] == 'NEUTRAL' for r in pair_results):
        score -= 5

    if wyckoff_opposed and not wyckoff_aligned:
        score -= 10
    if pd_wrong and not pd_correct:
        score -= 15
    if liq_opposed and not liq_aligned:
        score -= 8

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
                    'tf': tf, 'recommendation': recommendation,
                    'psych': psych, 'ob': ob, 'zones': zones, 'fvg': fvg,
                    'wyckoff': wyckoff, 'structure': structure, 'true_ob': true_ob,
                    'liquidity': liquidity, 'premium_discount': premium_disc,
                    'displacement': displacement
                })

                time.sleep(API_REQUEST_DELAY)

            if not pair_results or last_indicators is None:
                logger.info(f"{pair} - No results")
                continue

            direction, score, rationale = compute_pair_score(pair_results)

            # Kill Zone : +5 pts si signal pendant une fenêtre institutionnelle
            kz = is_kill_zone()
            if kz['active'] and direction != 'NEUTRAL':
                score = min(score + 5, 100)

            if score < 68:
                logger.info(f"{pair} - Score {score} below threshold (68)")
                continue

            logger.info(f"{pair} - SIGNAL DETECTED: {direction} {score}/100"
                        + (f" [{kz['name']}]" if kz['active'] else ""))

            best_true_ob   = next((r['true_ob']  for r in pair_results if r.get('true_ob')),  None)
            best_liquidity = next((r['liquidity'] for r in pair_results
                                   if r.get('liquidity') and r['liquidity'].get('bsl')), None)
            best_pd = next((r['premium_discount'] for r in pair_results
                            if r.get('premium_discount') and r['premium_discount']['zone'] != 'NEUTRAL'), None)

            sl, levels = choose_levels(last_current_price, direction, last_indicators,
                                       smc_data={'true_ob': best_true_ob, 'liquidity': best_liquidity})
            if direction == 'NEUTRAL' or sl is None:
                message = format_pair_message(pair, direction, score, rationale,
                                              last_current_price, sl or last_current_price,
                                              last_current_price, last_current_price, last_current_price,
                                              last_current_price, best_pd, kz)
            else:
                t1, t2, t3 = get_target_levels(last_current_price, sl, direction)
                message = format_pair_message(pair, direction, score, rationale,
                                              last_current_price, sl, t1, t2, t3,
                                              last_current_price, best_pd, kz)

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
