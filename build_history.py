"""
Build historical statistics for 23 forex pairs.

Fetches up to 10 years D1/H4 and 5 years H1 from MT5.
For each pair, computes:
  - Psychological level bounce rates (D1, 10y)
  - Kill zone directional performance (H1, 5y)
  - Premium / Discount zone accuracy (D1, 10y)
  - FVG mitigation rate (H4, 10y)
  - Daily volatility profile (D1, 10y)

Output: historical_stats.json  (resume-capable — already-computed pairs are skipped)

Usage:
    python build_history.py
    python build_history.py --force   # recompute all pairs
"""

import os
import sys
import json
import datetime
import logging
import argparse

import MetaTrader5 as mt5
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

PAIRS = [
    "EURUSD", "EURGBP", "EURCAD", "EURJPY", "EURCHF", "EURAUD", "EURNZD",
    "USDCAD", "USDJPY", "USDCHF",
    "GBPUSD", "GBPCAD", "GBPJPY", "GBPCHF", "GBPNZD", "GBPAUD",
    "AUDUSD", "AUDCAD", "AUDCHF", "AUDJPY",
    "NZDUSD", "NZDCAD", "NZDCHF"
]

# Comprehensive psychological levels per pair (whole/half figures that matter)
PSYCH_LEVELS = {
    "EURUSD": [0.9500, 1.0000, 1.0500, 1.1000, 1.1500, 1.2000, 1.2500],
    "GBPUSD": [1.1500, 1.2000, 1.2500, 1.3000, 1.3500, 1.4000, 1.4500],
    "USDJPY": [100.00, 105.00, 110.00, 115.00, 120.00, 125.00, 130.00, 135.00, 140.00, 145.00, 150.00, 155.00, 160.00],
    "EURJPY": [115.00, 120.00, 125.00, 130.00, 135.00, 140.00, 145.00, 150.00, 155.00, 160.00, 165.00, 170.00],
    "GBPJPY": [145.00, 150.00, 155.00, 160.00, 165.00, 170.00, 175.00, 180.00, 185.00, 190.00, 195.00, 200.00],
    "AUDUSD": [0.5500, 0.6000, 0.6500, 0.7000, 0.7500, 0.8000],
    "NZDUSD": [0.5000, 0.5500, 0.6000, 0.6500, 0.7000, 0.7500],
    "USDCAD": [1.1500, 1.2000, 1.2500, 1.3000, 1.3500, 1.4000, 1.4500],
    "USDCHF": [0.8000, 0.8500, 0.9000, 0.9500, 1.0000, 1.0500],
    "EURGBP": [0.7500, 0.8000, 0.8500, 0.9000, 0.9500, 1.0000],
    "EURCAD": [1.3500, 1.4000, 1.4500, 1.5000, 1.5500, 1.6000, 1.6500],
    "EURCHF": [0.9000, 0.9500, 1.0000, 1.0500, 1.1000, 1.1500, 1.2000],
    "EURAUD": [1.4500, 1.5000, 1.5500, 1.6000, 1.6500, 1.7000, 1.7500],
    "EURNZD": [1.5500, 1.6000, 1.6500, 1.7000, 1.7500, 1.8000, 1.8500],
    "GBPCAD": [1.5500, 1.6000, 1.6500, 1.7000, 1.7500, 1.8000, 1.8500],
    "GBPCHF": [1.1000, 1.1500, 1.2000, 1.2500, 1.3000, 1.3500, 1.4000],
    "GBPNZD": [1.7500, 1.8000, 1.8500, 1.9000, 1.9500, 2.0000, 2.0500, 2.1000],
    "GBPAUD": [1.6500, 1.7000, 1.7500, 1.8000, 1.8500, 1.9000, 1.9500],
    "AUDJPY": [75.00, 80.00, 85.00, 90.00, 95.00, 100.00, 105.00],
    "AUDCAD": [0.8000, 0.8500, 0.9000, 0.9500, 1.0000, 1.0500],
    "AUDCHF": [0.5000, 0.5500, 0.6000, 0.6500, 0.7000, 0.7500],
    "NZDCAD": [0.7500, 0.8000, 0.8500, 0.9000, 0.9500],
    "NZDCHF": [0.4500, 0.5000, 0.5500, 0.6000, 0.6500],
}

KILL_ZONE_HOURS = {
    'London Kill Zone':  list(range(7, 10)),
    'New York Kill Zone': list(range(12, 15)),
    'London Close':      list(range(15, 16)),
    'Asian Kill Zone':   list(range(0, 4)),
}

# MT5 bar counts (approximate, accounting for weekends)
D1_BARS_10Y  = 2520   # ~252 trading days × 10 years
H4_BARS_10Y  = 10080  # 6 H4 bars/day × 252 × 10y (slightly over-fetching is fine)
H1_BARS_5Y   = 9000   # ~6 active H1 bars/day × 252 × 5y (conservative)

OUTPUT_FILE = 'historical_stats.json'
RESUME_MAX_AGE_DAYS = 7   # skip re-computation if pair was updated < 7 days ago


# ─── Helpers ──────────────────────────────────────────────────────────────────

def pip_size(pair: str) -> float:
    return 0.01 if 'JPY' in pair else 0.0001


def load_existing() -> dict:
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not parse existing {OUTPUT_FILE}: {e}")
    return {'_meta': {}}


def save_stats(stats: dict) -> None:
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"  → Saved to {OUTPUT_FILE}")


def fetch_data(pair: str, mt5_tf: int, count: int) -> pd.DataFrame | None:
    """Fetch `count` bars from MT5 and return a DataFrame (newest last)."""
    rates = mt5.copy_rates_from_pos(pair, mt5_tf, 0, count)
    if rates is None or len(rates) == 0:
        logger.warning(f"    No data for {pair} tf={mt5_tf} count={count}")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    if 'tick_volume' in df.columns:
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    return df


# ─── Analysis functions ────────────────────────────────────────────────────────

def analyze_psych_levels(df_d1: pd.DataFrame, pair: str) -> dict:
    """
    For each psychological level, count touches and confirmed bounces using D1 data.

    A touch   = any candle whose wick reaches within 15 pips of the level.
    A bounce  = within the next 10 D1 candles, price moves ≥ 30 pips AWAY from
                the level in the direction of the approach (reversal confirmation).
    Strong level if bounce_rate ≥ 0.60 AND touches ≥ 8.
    """
    levels = PSYCH_LEVELS.get(pair, [])
    pip    = pip_size(pair)
    touch_tolerance = pip * 15   # 15 pips
    min_reaction    = pip * 30   # 30 pips to confirm bounce
    result = {}
    n = len(df_d1)

    for level in levels:
        touches           = 0
        bounces           = 0
        reaction_pips_acc = []

        for i in range(n - 10):
            lo = df_d1['low'].iloc[i]
            hi = df_d1['high'].iloc[i]
            op = df_d1['open'].iloc[i]

            # Touch: wick or body crosses within tolerance
            if not (abs(lo - level) <= touch_tolerance or
                    abs(hi - level) <= touch_tolerance or
                    lo <= level <= hi):
                continue

            touches += 1
            approach_from_below = op < level

            for j in range(i + 1, min(i + 11, n)):
                nxt_cl = df_d1['close'].iloc[j]
                nxt_lo = df_d1['low'].iloc[j]
                nxt_hi = df_d1['high'].iloc[j]
                if approach_from_below:
                    # Expect bullish bounce: close ≥ level + 30 pips
                    if nxt_cl >= level + min_reaction:
                        bounces += 1
                        reaction_pips_acc.append((nxt_cl - level) / pip)
                        break
                    if nxt_lo < level - min_reaction:
                        break  # continuation down — no bounce
                else:
                    # Expect bearish bounce: close ≤ level − 30 pips
                    if nxt_cl <= level - min_reaction:
                        bounces += 1
                        reaction_pips_acc.append((level - nxt_cl) / pip)
                        break
                    if nxt_hi > level + min_reaction:
                        break  # continuation up — no bounce

        br  = round(bounces / touches, 3) if touches >= 5 else None
        avg = round(sum(reaction_pips_acc) / len(reaction_pips_acc), 1) if reaction_pips_acc else 0.0

        result[str(level)] = {
            'touches':           touches,
            'bounces':           bounces,
            'bounce_rate':       br,
            'avg_reaction_pips': avg,
            'strong':            br is not None and br >= 0.60 and touches >= 8,
        }

    return result


def analyze_kill_zones(df_h1: pd.DataFrame, pair: str) -> dict:
    """
    For each kill zone, measure directional bias and average range using H1 data.

    bullish_rate  = fraction of kill-zone H1 candles that closed bullish.
    avg_range_pips = mean(high − low) in pips across all kill-zone H1 candles.
    """
    pip    = pip_size(pair)
    result = {}

    for kz_name, hours in KILL_ZONE_HOURS.items():
        mask = df_h1.index.hour.isin(hours)
        kz_df = df_h1[mask]

        if len(kz_df) < 50:
            continue

        bullish = (kz_df['close'] > kz_df['open']).sum()
        ranges  = ((kz_df['high'] - kz_df['low']) / pip).tolist()

        result[kz_name] = {
            'bullish_rate':    round(float(bullish) / len(kz_df), 3),
            'avg_range_pips':  round(sum(ranges) / len(ranges), 1),
            'sample':          len(kz_df),
        }

    return result


def analyze_premium_discount(df_d1: pd.DataFrame) -> dict:
    """
    Classify each D1 candle's position in a 20-period swing range as
    Discount (<40%) or Premium (>60%) and check if the next 5 candles
    confirm the expected directional move (≥ 30% of the period's ATR).

    Returns discount_bull_rate and premium_bear_rate.
    """
    n = len(df_d1)
    if n < 35:
        return {}

    swing_window = 20
    check_window = 5
    move_factor  = 0.3    # 30% of mean ATR = meaningful move

    discount_bull  = 0
    discount_total = 0
    premium_bear   = 0
    premium_total  = 0

    for i in range(swing_window, n - check_window):
        w_high = df_d1['high'].iloc[i - swing_window:i].max()
        w_low  = df_d1['low'].iloc[i - swing_window:i].min()
        rng    = w_high - w_low
        if rng == 0:
            continue

        curr_cl = df_d1['close'].iloc[i]
        pct     = (curr_cl - w_low) / rng * 100

        atr_approx = float(
            (df_d1['high'].iloc[i - swing_window:i] - df_d1['low'].iloc[i - swing_window:i]).mean()
        )
        min_move = atr_approx * move_factor

        future_cl = df_d1['close'].iloc[i + check_window]

        if pct < 40:
            discount_total += 1
            if future_cl > curr_cl + min_move:
                discount_bull += 1
        elif pct > 60:
            premium_total += 1
            if future_cl < curr_cl - min_move:
                premium_bear += 1

    return {
        'discount_bull_rate': round(discount_bull / discount_total, 3) if discount_total >= 20 else None,
        'premium_bear_rate':  round(premium_bear  / premium_total,  3) if premium_total  >= 20 else None,
        'discount_sample':    discount_total,
        'premium_sample':     premium_total,
    }


def analyze_fvg_mitigation(df_h4: pd.DataFrame, pair: str) -> dict:
    """
    Detect all Fair Value Gaps (3-candle imbalances) on H4 and check
    whether each gap is filled (mitigated) within the next 20 H4 bars.

    A FVG is valid only if the gap width ≥ 3 pips (filters noise).
    mitigation_rate = mitigated_count / total_valid_fvgs
    """
    pip          = pip_size(pair)
    min_gap_pips = 3
    check_window = 20
    n            = len(df_h4)

    if n < check_window + 3:
        return {}

    total_fvgs = 0
    mitigated  = 0

    for i in range(1, n - check_window - 1):
        c1_hi = df_h4['high'].iloc[i - 1]
        c1_lo = df_h4['low'].iloc[i - 1]
        c3_hi = df_h4['high'].iloc[i + 1]
        c3_lo = df_h4['low'].iloc[i + 1]

        # Bullish FVG: c3_low > c1_high
        if c3_lo > c1_hi and (c3_lo - c1_hi) >= pip * min_gap_pips:
            gap_top    = c3_lo
            gap_bottom = c1_hi
        # Bearish FVG: c3_high < c1_low
        elif c3_hi < c1_lo and (c1_lo - c3_hi) >= pip * min_gap_pips:
            gap_top    = c1_lo
            gap_bottom = c3_hi
        else:
            continue

        total_fvgs += 1

        for j in range(i + 2, min(i + 2 + check_window, n)):
            lo_j = df_h4['low'].iloc[j]
            hi_j = df_h4['high'].iloc[j]
            # Mitigation: price re-enters the gap zone
            if lo_j <= gap_top and hi_j >= gap_bottom:
                mitigated += 1
                break

    return {
        'mitigation_rate': round(mitigated / total_fvgs, 3) if total_fvgs >= 20 else None,
        'total_fvgs':      total_fvgs,
        'mitigated':       mitigated,
    }


def analyze_volatility(df_d1: pd.DataFrame, pair: str) -> dict:
    """
    Compute average daily range (H−L) in pips and breakdown by weekday (0=Mon…4=Fri).
    Used to flag historically low-volatility days when scoring signals.
    """
    pip = pip_size(pair)
    df  = df_d1.copy()
    df['range_pips'] = (df['high'] - df['low']) / pip

    avg_daily = round(float(df['range_pips'].mean()), 1)
    by_weekday: dict[str, float] = {}

    for wd in range(5):
        mask = df.index.weekday == wd
        if mask.sum() >= 10:
            by_weekday[str(wd)] = round(float(df.loc[mask, 'range_pips'].mean()), 1)

    return {
        'avg_daily_range_pips': avg_daily,
        'by_weekday':           by_weekday,
        'sample':               len(df),
    }


# ─── Per-pair orchestrator ─────────────────────────────────────────────────────

def build_pair(pair: str) -> dict:
    """Fetch all required timeframes and compute every stat block for `pair`."""
    logger.info(f"    Fetching D1  (~{D1_BARS_10Y} bars, 10y)…")
    df_d1 = fetch_data(pair, mt5.TIMEFRAME_D1, D1_BARS_10Y)

    logger.info(f"    Fetching H4  (~{H4_BARS_10Y} bars, 10y)…")
    df_h4 = fetch_data(pair, mt5.TIMEFRAME_H4, H4_BARS_10Y)

    logger.info(f"    Fetching H1  (~{H1_BARS_5Y} bars, 5y)…")
    df_h1 = fetch_data(pair, mt5.TIMEFRAME_H1, H1_BARS_5Y)

    pair_stats: dict = {}

    if df_d1 is not None and not df_d1.empty:
        logger.info(f"    Computing psychological levels ({len(df_d1)} D1 bars)…")
        pair_stats['psychological_levels'] = analyze_psych_levels(df_d1, pair)

        logger.info(f"    Computing premium/discount accuracy…")
        pair_stats['premium_discount'] = analyze_premium_discount(df_d1)

        logger.info(f"    Computing volatility profile…")
        pair_stats['volatility'] = analyze_volatility(df_d1, pair)
    else:
        logger.warning(f"    No D1 data for {pair} — skipping D1-based analyses")

    if df_h4 is not None and not df_h4.empty:
        logger.info(f"    Computing FVG mitigation rate ({len(df_h4)} H4 bars)…")
        pair_stats['fvg'] = analyze_fvg_mitigation(df_h4, pair)
    else:
        logger.warning(f"    No H4 data for {pair} — skipping FVG analysis")

    if df_h1 is not None and not df_h1.empty:
        logger.info(f"    Computing kill zone performance ({len(df_h1)} H1 bars)…")
        pair_stats['kill_zones'] = analyze_kill_zones(df_h1, pair)
    else:
        logger.warning(f"    No H1 data for {pair} — skipping kill zone analysis")

    pair_stats['_computed_at'] = datetime.datetime.utcnow().isoformat()
    return pair_stats


# ─── Main entry point ──────────────────────────────────────────────────────────

def run_build(force: bool = False) -> None:
    logger.info("=" * 60)
    logger.info("HISTORICAL STATS BUILDER  —  23 forex pairs")
    logger.info("=" * 60)

    # Load credentials (config.py first, then env vars)
    try:
        from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MT5_PATH
    except ImportError:
        try:
            MT5_LOGIN    = int(os.environ['MT5_LOGIN'])
            MT5_PASSWORD = os.environ['MT5_PASSWORD']
            MT5_SERVER   = os.environ['MT5_SERVER']
            MT5_PATH     = os.environ.get('MT5_PATH', '')
        except KeyError as e:
            logger.error(f"Missing credential: {e}. Set in config.py or environment.")
            sys.exit(1)

    if not mt5.initialize(MT5_PATH):
        logger.error("MT5 initialization failed")
        sys.exit(1)

    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        logger.error(f"MT5 login failed: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)

    logger.info("MT5 connected successfully.")
    stats = load_existing()
    stats['_meta'] = {
        'generated_at':  datetime.datetime.utcnow().isoformat(),
        'years_d1_h4':   10,
        'years_h1':       5,
        'version':       '1.0',
    }

    skipped  = 0
    computed = 0
    errors   = 0

    for idx, pair in enumerate(PAIRS, 1):
        logger.info(f"\n[{idx}/{len(PAIRS)}] {pair}")

        # Resume: skip if recently computed and --force not set
        if not force and pair in stats:
            ts = stats[pair].get('_computed_at')
            if ts:
                try:
                    age = (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(ts)).days
                    if age < RESUME_MAX_AGE_DAYS:
                        logger.info(f"  SKIP — computed {age}d ago (use --force to recompute)")
                        skipped += 1
                        continue
                except Exception:
                    pass  # bad timestamp → recompute

        try:
            pair_stats = build_pair(pair)
            stats[pair] = pair_stats
            save_stats(stats)
            computed += 1
            logger.info(f"  OK — {pair} done")
        except Exception as e:
            logger.error(f"  ERROR — {pair}: {e}", exc_info=True)
            errors += 1

    mt5.shutdown()

    logger.info("\n" + "=" * 60)
    logger.info(f"BUILD COMPLETE: {computed} computed, {skipped} skipped, {errors} errors")
    logger.info(f"Output: {os.path.abspath(OUTPUT_FILE)}")
    logger.info("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build historical stats for forex signal scanner')
    parser.add_argument('--force', action='store_true',
                        help='Recompute all pairs even if recently updated')
    args = parser.parse_args()
    run_build(force=args.force)
