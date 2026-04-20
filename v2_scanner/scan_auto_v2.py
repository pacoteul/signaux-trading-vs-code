"""
scan_auto_v2.py — Scanner de signaux day-trading SMC, version 2 (checklist binaire).

Philosophie : ZÉRO système de points. Chaque signal doit passer 6 conditions
obligatoires, sinon rejeté. Maximum 2 signaux par scan, pendant London Open ou
NY Open uniquement. Setup unique : MSS M15 + FVG frais + retest à l'intérieur.

Les 6 conditions obligatoires :
  1. Session active (London Open 7-10 GMT ou NY Open 13-15 GMT)
  2. Biais H4 clair (4 dernières bougies du bon côté de l'EMA20 + structure HH/HL)
  3. MSS M15 confirmé dans la direction du biais H4 (≤ 10 bougies)
  4. FVG frais dans la jambe de déplacement (touched_pct < 40%)
  5. Prix actuel À L'INTÉRIEUR du FVG (pas "proche", vraiment dedans)
  6. SL dans les bornes (5-20p majors, 5-25p exotiques, 5-30p JPY)
"""

import os
import sys
import time
import datetime
import logging
import requests
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta


# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scan_auto_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ─── Credentials ──────────────────────────────────────────────────────────────

def _load_credentials():
    env = {
        'MT5_LOGIN':          os.getenv('MT5_LOGIN'),
        'MT5_PASSWORD':       os.getenv('MT5_PASSWORD'),
        'MT5_SERVER':         os.getenv('MT5_SERVER'),
        'MT5_PATH':           os.getenv('MT5_PATH'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID':   os.getenv('TELEGRAM_CHAT_ID'),
    }
    if not all(env.values()):
        try:
            from config import (MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH,
                                TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            env['MT5_LOGIN']          = env['MT5_LOGIN']          or MT5_LOGIN
            env['MT5_PASSWORD']       = env['MT5_PASSWORD']       or MT5_PASSWORD
            env['MT5_SERVER']         = env['MT5_SERVER']         or MT5_SERVER
            env['MT5_PATH']           = env['MT5_PATH']           or MT5_PATH
            env['TELEGRAM_BOT_TOKEN'] = env['TELEGRAM_BOT_TOKEN'] or TELEGRAM_BOT_TOKEN
            env['TELEGRAM_CHAT_ID']   = env['TELEGRAM_CHAT_ID']   or TELEGRAM_CHAT_ID
        except ImportError:
            logger.error("config.py absent et variables d'environnement incomplètes.")
            sys.exit(1)
    env['MT5_LOGIN'] = int(env['MT5_LOGIN'])
    return env


_CREDS = _load_credentials()


# ─── Constantes ───────────────────────────────────────────────────────────────

PAIRS = [
    "EURUSD", "EURGBP", "EURCAD", "EURJPY", "EURCHF", "EURAUD", "EURNZD",
    "USDCAD", "USDJPY", "USDCHF",
    "GBPUSD", "GBPCAD", "GBPJPY", "GBPCHF", "GBPNZD", "GBPAUD",
    "AUDUSD", "AUDCAD", "AUDCHF", "AUDJPY",
    "NZDUSD", "NZDCAD", "NZDCHF",
]

EXOTIC_PAIRS = {'GBPNZD', 'GBPAUD', 'EURNZD', 'EURAUD', 'GBPCHF', 'GBPCAD'}

# SL hard caps (pips) — day trading only, never risk more
SL_MAX_PIPS = {'major': 20, 'exotic': 25, 'jpy': 30}
SL_MIN_PIPS = 5

# FVG freshness threshold — above this, FVG is "stale" and rejected
FVG_MAX_TOUCHED_PCT = 40.0

# R/R targets
RR_TP1 = 2.0
RR_TP2 = 3.0
RR_TP3 = 5.0

# Délais API MT5
API_DELAY    = 0.3   # entre chaque requête get_mt5_data
PAIR_DELAY   = 0.5   # entre chaque paire
SIGNAL_DELAY = 2.0   # entre chaque message Telegram

# Validité d'un signal day-trade : 90 minutes
SIGNAL_VALIDITY_MIN = 90

# Maximum de signaux envoyés par scan (après tri par fraîcheur)
MAX_SIGNALS_PER_SCAN = 2


# ─── Infrastructure MT5 / Telegram ────────────────────────────────────────────

def initialize_mt5() -> bool:
    if not mt5.initialize(_CREDS['MT5_PATH']):
        logger.error(f"MT5 init failed: {mt5.last_error()}")
        return False
    if not mt5.login(_CREDS['MT5_LOGIN'], _CREDS['MT5_PASSWORD'], _CREDS['MT5_SERVER']):
        logger.error(f"MT5 login failed: {mt5.last_error()}")
        return False
    logger.info("MT5 connected")
    return True


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{_CREDS['TELEGRAM_BOT_TOKEN']}/sendMessage"
    data = {
        'chat_id': _CREDS['TELEGRAM_CHAT_ID'],
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code != 200:
            logger.error(f"Telegram {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Telegram error: {e}")


def get_mt5_data(symbol: str, timeframe, n: int = 100) -> pd.DataFrame | None:
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df


# ─── Helpers génériques ───────────────────────────────────────────────────────

def _pip_size(pair: str) -> float:
    return 0.01 if 'JPY' in pair else 0.0001


def _sl_cap_pips(pair: str) -> int:
    if 'JPY' in pair:
        return SL_MAX_PIPS['jpy']
    if pair in EXOTIC_PAIRS:
        return SL_MAX_PIPS['exotic']
    return SL_MAX_PIPS['major']


def _fmt_price(price: float, pair: str) -> str:
    digits = 3 if 'JPY' in pair else 5
    return f"{price:.{digits}f}"


# ─── Condition 1 : Session Active ─────────────────────────────────────────────

def is_quality_session() -> dict:
    """London Open (7-10 GMT) = qualité A ; NY Open (13-15 GMT) = qualité A.
    En dehors de ces fenêtres, AUCUN scan."""
    h = datetime.datetime.utcnow().hour
    if 7 <= h < 10:
        return {'active': True, 'name': 'London Open', 'quality': 'A'}
    if 13 <= h < 15:
        return {'active': True, 'name': 'New York Open', 'quality': 'A'}
    return {'active': False, 'name': None, 'quality': None}


# ─── Condition 2 : Biais H4 ───────────────────────────────────────────────────

def detect_h4_bias(df_h4: pd.DataFrame) -> str | None:
    """
    Biais H4 clair si :
      - Les 4 dernières bougies H4 closes sont du même côté de l'EMA20
      - La structure est cohérente (HH/HL pour bull, LH/LL pour bear)
    Retourne 'BUY', 'SELL' ou None.
    """
    if df_h4 is None or len(df_h4) < 25:
        return None

    ema20 = ta.ema(df_h4['close'], length=20)
    if ema20 is None or ema20.isna().all():
        return None

    # On exclut la bougie en cours (iloc[-1]) et on regarde les 4 précédentes closes
    closes_sample = df_h4['close'].iloc[-5:-1]
    ema_sample    = ema20.iloc[-5:-1]

    above = (closes_sample > ema_sample).sum()
    below = (closes_sample < ema_sample).sum()

    # Structure sur les 6 dernières bougies closes
    highs = df_h4['high'].iloc[-7:-1].values
    lows  = df_h4['low'].iloc[-7:-1].values

    hh = highs[-1] > highs[-4] and lows[-1] > lows[-4]
    ll = highs[-1] < highs[-4] and lows[-1] < lows[-4]

    if above >= 4 and hh:
        return 'BUY'
    if below >= 4 and ll:
        return 'SELL'
    return None


# ─── Condition 3 : MSS M15 ────────────────────────────────────────────────────

def detect_m15_mss(df_m15: pd.DataFrame, direction: str, lookback: int = 20):
    """
    Trouve le Market Structure Shift le plus récent dans la direction du biais.
    MSS bull : une bougie close AU-DESSUS du plus haut des 10 bougies précédentes.
    MSS bear : une bougie close EN-DESSOUS du plus bas des 10 bougies précédentes.
    Retourne (position_mss, swing_level) ou (None, None).
    """
    if df_m15 is None or len(df_m15) < lookback + 10:
        return None, None

    # On parcourt des 20 dernières bougies vers la plus récente
    start = len(df_m15) - lookback
    end   = len(df_m15)

    latest_mss = None
    swing      = None

    for i in range(start + 10, end):
        window = df_m15.iloc[i-10:i]  # 10 bougies précédentes
        bar    = df_m15.iloc[i]

        if direction == 'BUY':
            swing_high = window['high'].max()
            if bar['close'] > swing_high:
                latest_mss = i
                swing      = swing_high
        elif direction == 'SELL':
            swing_low = window['low'].min()
            if bar['close'] < swing_low:
                latest_mss = i
                swing      = swing_low

    return latest_mss, swing


# ─── Condition 4 : FVG frais ──────────────────────────────────────────────────

def _fvg_touched_pct(df: pd.DataFrame, fvg: dict, direction: str) -> float:
    """Pourcentage de la FVG déjà violée depuis sa création."""
    after = df.iloc[fvg['created_idx'] + 1:]
    if after.empty:
        return 0.0
    fvg_range = fvg['top'] - fvg['bottom']
    if fvg_range <= 0:
        return 100.0

    if direction == 'BUY':
        lowest = after['low'].min()
        if lowest >= fvg['top']:
            return 0.0
        if lowest <= fvg['bottom']:
            return 100.0
        return (fvg['top'] - lowest) / fvg_range * 100
    else:
        highest = after['high'].max()
        if highest <= fvg['bottom']:
            return 0.0
        if highest >= fvg['top']:
            return 100.0
        return (highest - fvg['bottom']) / fvg_range * 100


def detect_fresh_fvg(df_m15: pd.DataFrame, direction: str, mss_idx: int) -> dict | None:
    """
    Cherche la FVG la plus fraîche dans la jambe de déplacement du MSS.
    Définition mathématique :
      BUY  : bougie[i-2].high < bougie[i].low
      SELL : bougie[i-2].low  > bougie[i].high
    Retourne le FVG le plus récent dont touched_pct < 40%, ou None.
    """
    if df_m15 is None or mss_idx is None:
        return None

    start = max(2, mss_idx - 5)
    end   = min(len(df_m15), mss_idx + 3)

    candidates = []
    for i in range(start, end):
        a = df_m15.iloc[i - 2]
        c = df_m15.iloc[i]

        if direction == 'BUY' and a['high'] < c['low']:
            candidates.append({
                'top':         float(c['low']),
                'bottom':      float(a['high']),
                'midpoint':    float((c['low'] + a['high']) / 2),
                'created_idx': i,
                'created_at':  df_m15.index[i],
            })
        elif direction == 'SELL' and a['low'] > c['high']:
            candidates.append({
                'top':         float(a['low']),
                'bottom':      float(c['high']),
                'midpoint':    float((a['low'] + c['high']) / 2),
                'created_idx': i,
                'created_at':  df_m15.index[i],
            })

    if not candidates:
        return None

    for fvg in reversed(candidates):
        fvg['touched_pct'] = _fvg_touched_pct(df_m15, fvg, direction)
        if fvg['touched_pct'] < FVG_MAX_TOUCHED_PCT:
            return fvg

    return None


# ─── Condition 5 : Prix à l'intérieur du FVG ──────────────────────────────────

def price_inside_fvg(current_price: float, fvg: dict) -> bool:
    return fvg['bottom'] <= current_price <= fvg['top']


# ─── Condition 6 : SL/TP dans les bornes ──────────────────────────────────────

def compute_sl_tp(pair: str, entry: float, fvg: dict, direction: str):
    """
    SL = extrémité opposée du FVG + 3 pips de buffer.
    TP1/2/3 = 2R/3R/5R.
    Retourne (sl, t1, t2, t3, err) — si err != None, le signal est rejeté.
    """
    pip    = _pip_size(pair)
    buffer = 3 * pip
    cap    = _sl_cap_pips(pair)

    if direction == 'BUY':
        sl       = fvg['bottom'] - buffer
        sl_dist  = entry - sl
    else:
        sl       = fvg['top'] + buffer
        sl_dist  = sl - entry

    sl_pips = sl_dist / pip

    if sl_pips > cap:
        return None, None, None, None, f"SL {sl_pips:.1f}p > cap {cap}p"
    if sl_pips < SL_MIN_PIPS:
        return None, None, None, None, f"SL {sl_pips:.1f}p < {SL_MIN_PIPS}p"

    if direction == 'BUY':
        t1 = entry + RR_TP1 * sl_dist
        t2 = entry + RR_TP2 * sl_dist
        t3 = entry + RR_TP3 * sl_dist
    else:
        t1 = entry - RR_TP1 * sl_dist
        t2 = entry - RR_TP2 * sl_dist
        t3 = entry - RR_TP3 * sl_dist

    return sl, t1, t2, t3, None


# ─── Mise en forme Telegram ───────────────────────────────────────────────────

def build_message(sig: dict) -> str:
    pair      = sig['pair']
    direction = sig['direction']
    pip       = _pip_size(pair)
    entry     = sig['entry']
    sl        = sig['sl']
    sl_pips   = abs(entry - sl) / pip

    expires = (datetime.datetime.utcnow()
               + datetime.timedelta(minutes=SIGNAL_VALIDITY_MIN)).strftime('%H:%M')

    arrow = '🟢 LONG' if direction == 'BUY' else '🔴 SHORT'
    fmt   = lambda p: _fmt_price(p, pair)

    return (
        f"<b>{pair} {arrow}</b>\n"
        f"<b>Session :</b> {sig['session']['name']}\n"
        f"\n"
        f"<b>Entrée :</b> <code>{fmt(entry)}</code>\n"
        f"<b>SL :</b> <code>{fmt(sl)}</code> <i>({sl_pips:.0f} pips)</i>\n"
        f"<b>TP1 :</b> <code>{fmt(sig['t1'])}</code> <i>(2.0R)</i>\n"
        f"<b>TP2 :</b> <code>{fmt(sig['t2'])}</code> <i>(3.0R)</i>\n"
        f"<b>TP3 :</b> <code>{fmt(sig['t3'])}</code> <i>(5.0R)</i>\n"
        f"\n"
        f"<b>Setup :</b> MSS M15 + FVG frais "
        f"<i>({sig['fvg']['touched_pct']:.0f}% rempli)</i>\n"
        f"<b>Biais H4 :</b> {direction}\n"
        f"<b>Valide jusqu'à :</b> {expires} GMT"
    )


# ─── Scan principal ───────────────────────────────────────────────────────────

def scan() -> int:
    """Exécute un scan complet. Retourne le nombre de signaux envoyés."""
    session = is_quality_session()
    now_utc = datetime.datetime.utcnow()

    if not session['active']:
        logger.info(f"Session inactive à {now_utc.strftime('%H:%M')} UTC — scan ignoré.")
        return 0

    logger.info(f"═══ SCAN V2 — {session['name']} @ {now_utc.strftime('%H:%M')} UTC ═══")

    if not initialize_mt5():
        return 0

    candidates = []
    rejected   = {'h4_bias': 0, 'mss': 0, 'fvg': 0, 'not_in_fvg': 0, 'sl': 0, 'data': 0}

    try:
        for pair in PAIRS:
            df_h4  = get_mt5_data(pair, mt5.TIMEFRAME_H4, 50)
            time.sleep(API_DELAY)
            df_m15 = get_mt5_data(pair, mt5.TIMEFRAME_M15, 100)
            time.sleep(API_DELAY)

            if df_h4 is None or df_m15 is None:
                rejected['data'] += 1
                time.sleep(PAIR_DELAY)
                continue

            # 2. Biais H4
            bias = detect_h4_bias(df_h4)
            if bias is None:
                rejected['h4_bias'] += 1
                time.sleep(PAIR_DELAY)
                continue

            # 3. MSS M15
            mss_idx, _ = detect_m15_mss(df_m15, bias)
            if mss_idx is None:
                rejected['mss'] += 1
                time.sleep(PAIR_DELAY)
                continue

            # 4. FVG frais dans la jambe de déplacement
            fvg = detect_fresh_fvg(df_m15, bias, mss_idx)
            if fvg is None:
                rejected['fvg'] += 1
                time.sleep(PAIR_DELAY)
                continue

            # 5. Prix À L'INTÉRIEUR du FVG
            entry = float(df_m15['close'].iloc[-1])
            if not price_inside_fvg(entry, fvg):
                rejected['not_in_fvg'] += 1
                time.sleep(PAIR_DELAY)
                continue

            # 6. SL/TP dans les bornes
            sl, t1, t2, t3, err = compute_sl_tp(pair, entry, fvg, bias)
            if err:
                rejected['sl'] += 1
                logger.info(f"{pair} REJECT — {err}")
                time.sleep(PAIR_DELAY)
                continue

            # Candidat valide
            candidates.append({
                'pair':      pair,
                'direction': bias,
                'entry':     entry,
                'sl':        sl,
                't1':        t1,
                't2':        t2,
                't3':        t3,
                'fvg':       fvg,
                'session':   session,
                'freshness': 100.0 - fvg['touched_pct'],
            })
            logger.info(
                f"{pair} ✓ CANDIDAT — {bias} | "
                f"FVG {fvg['touched_pct']:.0f}% rempli | "
                f"SL {abs(entry-sl)/_pip_size(pair):.0f}p"
            )

            time.sleep(PAIR_DELAY)

        # Tri par fraîcheur (FVG la moins touchée en premier), top N
        candidates.sort(key=lambda c: c['freshness'], reverse=True)
        top = candidates[:MAX_SIGNALS_PER_SCAN]

        logger.info(
            f"Résultat : {len(candidates)} candidat(s), envoi des {len(top)} meilleurs. "
            f"Rejets : {rejected}"
        )

        for sig in top:
            send_telegram(build_message(sig))
            time.sleep(SIGNAL_DELAY)

        return len(top)

    finally:
        mt5.shutdown()


# ─── Boucle automatique ───────────────────────────────────────────────────────

def auto_scan() -> None:
    """Scan toutes les 30 minutes, mais uniquement pendant London Open ou NY Open."""
    logger.info("═══ scan_auto_v2 démarré — scans toutes les 30 min pendant London/NY Open ═══")

    while True:
        try:
            session = is_quality_session()
            now     = datetime.datetime.utcnow()

            if session['active']:
                scan()
                # Prochain scan dans 30 min
                logger.info("Prochain scan dans 30 minutes.")
                time.sleep(30 * 60)
            else:
                # Calcul du temps jusqu'au prochain créneau (London 07:00 ou NY 13:00)
                next_slots = [
                    now.replace(hour=7,  minute=0, second=0, microsecond=0),
                    now.replace(hour=13, minute=0, second=0, microsecond=0),
                ]
                future = [s for s in next_slots if s > now]
                next_scan = min(future) if future else \
                            next_slots[0] + datetime.timedelta(days=1)
                wait = (next_scan - now).total_seconds()
                logger.info(
                    f"Hors session. Prochain scan : "
                    f"{next_scan.strftime('%Y-%m-%d %H:%M')} UTC "
                    f"(dans {int(wait/60)} min)"
                )
                time.sleep(wait)

        except KeyboardInterrupt:
            logger.info("Scanner arrêté par l'utilisateur.")
            break
        except Exception as e:
            logger.error(f"Erreur boucle auto : {e}", exc_info=True)
            time.sleep(60)


if __name__ == '__main__':
    # Usage :
    #   python scan_auto_v2.py          → boucle automatique
    #   python scan_auto_v2.py once     → un seul scan puis sortie
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        scan()
    else:
        auto_scan()
