"""
Historical statistics module for the trading signal scanner.

Loads historical_stats.json (built by build_history.py) and provides:
  - get_historical_adjustment()  →  score delta  [-20, +25]
  - get_pair_volatility()        →  avg daily range in pips (or None)
  - get_level_report()           →  debug string with nearby level stats

The adjustment is a Bayesian update on the technical score:
  "Technically this looks bullish — and empirically, setups like this
   at THIS level / THIS kill zone / THIS P/D zone for THIS pair have
   worked X% of the time over the past 10 years."

Adjustment breakdown (max values):
  ┌──────────────────────────────────────────┬───────────┐
  │ Psychological level strength             │ -8 / +8   │
  │ Kill zone directional performance        │ -5 / +5   │
  │ Premium / Discount zone accuracy         │ -5 / +6   │
  │ FVG historical mitigation rate           │  0 / +4   │
  │ Weekday volatility alignment             │ -5 /  0   │
  ├──────────────────────────────────────────┼───────────┤
  │ TOTAL (clamped)                          │ -20 / +25 │
  └──────────────────────────────────────────┴───────────┘
"""

import os
import json
import datetime
import logging

logger = logging.getLogger(__name__)

STATS_FILE = 'historical_stats.json'
_cache: dict | None = None


# ─── Loader ───────────────────────────────────────────────────────────────────

def load_stats() -> dict:
    """
    Load historical_stats.json into memory (cached after first call).
    Returns an empty dict if the file is absent — scanner still works,
    just without the historical layer.
    """
    global _cache
    if _cache is not None:
        return _cache

    if not os.path.exists(STATS_FILE):
        logger.info(
            "historical_stats.json not found. "
            "Run  python build_history.py  to generate it. "
            "Scanner will operate without the historical layer."
        )
        _cache = {}
        return _cache

    try:
        with open(STATS_FILE, 'r') as f:
            _cache = json.load(f)
        pairs_loaded = sum(1 for k in _cache if not k.startswith('_'))
        meta = _cache.get('_meta', {})
        logger.info(
            f"Historical stats loaded: {pairs_loaded} pairs "
            f"(generated {meta.get('generated_at', 'unknown')[:10]})"
        )
    except Exception as e:
        logger.warning(f"Could not load {STATS_FILE}: {e}")
        _cache = {}

    return _cache


# ─── Score adjustment ─────────────────────────────────────────────────────────

def get_historical_adjustment(
    pair: str,
    current_price: float,
    pd_info: dict | None,
    kz_info: dict | None,
    direction: str,
    hist_stats: dict,
    has_fvg: bool = False,
) -> int:
    """
    Returns an integer score adjustment in [-20, +25].

    Parameters
    ----------
    pair          : e.g. "EURUSD"
    current_price : latest close price
    pd_info       : output of detect_premium_discount()  — may be None
    kz_info       : output of is_kill_zone()             — may be None
    direction     : 'BUY' | 'SELL' | 'NEUTRAL'
    hist_stats    : dict from load_stats()
    has_fvg       : True if a FVG was detected on any timeframe
    """
    if not hist_stats or pair not in hist_stats or direction == 'NEUTRAL':
        return 0

    p   = hist_stats[pair]
    adj = 0.0
    pip = 0.01 if 'JPY' in pair else 0.0001

    # ── 1. Psychological level strength ─────────────────────────────────────
    # Find the nearest psych level.  If price is within 20 pips, apply bonus/penalty
    # based on the historically measured bounce rate at that level.
    psych_data     = p.get('psychological_levels', {})
    nearest_stats  = None
    nearest_dist_p = float('inf')

    for level_str, lvl_stats in psych_data.items():
        try:
            level = float(level_str)
        except ValueError:
            continue
        dist_pips = abs(current_price - level) / pip
        if dist_pips < nearest_dist_p:
            nearest_dist_p = dist_pips
            nearest_stats  = lvl_stats

    if nearest_stats and nearest_dist_p <= 20:
        br     = nearest_stats.get('bounce_rate')
        strong = nearest_stats.get('strong', False)
        if br is not None:
            if br >= 0.70:
                adj += 8 if strong else 6     # very strong level historically
            elif br >= 0.62:
                adj += 4
            elif br >= 0.52:
                adj += 1
            elif br < 0.35:
                adj -= 8                       # level has been broken more than bounced
            elif br < 0.45:
                adj -= 4

    # ── 2. Kill zone directional performance ────────────────────────────────
    # Higher bonus when the current kill zone has historically favoured
    # the signal direction for this specific pair.
    kz_data = p.get('kill_zones', {})
    if kz_info and kz_info.get('active') and kz_info.get('name'):
        kz = kz_data.get(kz_info['name'])
        if kz:
            bull_rate = kz.get('bullish_rate', 0.5)
            # directional rate: how often kz moves our way
            rate = bull_rate if direction == 'BUY' else (1.0 - bull_rate)
            if rate >= 0.63:
                adj += 5
            elif rate >= 0.57:
                adj += 3
            elif rate >= 0.52:
                adj += 1
            elif rate < 0.43:
                adj -= 5
            elif rate < 0.48:
                adj -= 2

    # ── 3. Premium / Discount zone accuracy ─────────────────────────────────
    # Quantify how reliably the P/D classification has predicted direction.
    pd_data = p.get('premium_discount', {})
    if pd_info and pd_data:
        zone = pd_info.get('zone')
        rate = None

        if direction == 'BUY' and zone == 'Discount':
            rate = pd_data.get('discount_bull_rate')
        elif direction == 'SELL' and zone == 'Premium':
            rate = pd_data.get('premium_bear_rate')

        if rate is not None:
            if rate >= 0.68:
                adj += 6
            elif rate >= 0.58:
                adj += 3
            elif rate >= 0.50:
                adj += 1
            elif rate < 0.40:
                adj -= 5
            elif rate < 0.48:
                adj -= 2

    # ── 4. FVG historical mitigation rate ───────────────────────────────────
    # When a FVG is present, weight the signal by how reliably FVGs for
    # this pair get filled (mitigated) — high rate = price is likely to
    # revisit the gap zone, confirming the setup.
    if has_fvg:
        fvg_data = p.get('fvg', {})
        mit_rate = fvg_data.get('mitigation_rate')
        if mit_rate is not None:
            if mit_rate >= 0.78:
                adj += 4
            elif mit_rate >= 0.68:
                adj += 2

    # ── 5. Weekday volatility alignment ─────────────────────────────────────
    # If today is historically a very low-volatility day for this pair,
    # the signal is less likely to reach its targets → penalise.
    vol_data  = p.get('volatility', {})
    avg_range = vol_data.get('avg_daily_range_pips', 0)
    if avg_range > 0:
        today_wd = str(datetime.datetime.utcnow().weekday())
        wd_avg   = vol_data.get('by_weekday', {}).get(today_wd, avg_range)
        if wd_avg < avg_range * 0.55:
            adj -= 5   # historically lowest-volatility day for this pair

    return int(max(-20, min(25, round(adj))))


# ─── Utilities ────────────────────────────────────────────────────────────────

def get_pair_volatility(pair: str, hist_stats: dict) -> float | None:
    """Return average daily range in pips for `pair`, or None if unavailable."""
    if not hist_stats or pair not in hist_stats:
        return None
    return hist_stats[pair].get('volatility', {}).get('avg_daily_range_pips')


def get_level_report(pair: str, current_price: float, hist_stats: dict) -> str:
    """
    Build a human-readable debug report of historical stats near current price.
    Useful for diagnostics and manual back-testing review.
    """
    if not hist_stats or pair not in hist_stats:
        return f"{pair}: no historical data available (run build_history.py)"

    pip  = 0.01 if 'JPY' in pair else 0.0001
    p    = hist_stats[pair]
    lines = [f"── Historical report: {pair} @ {current_price:.5f} ──"]

    # Nearby psychological levels (within 100 pips)
    psych_data = p.get('psychological_levels', {})
    nearby = [
        (abs(current_price - float(lvl)) / pip, lvl, stats)
        for lvl, stats in psych_data.items()
        if abs(current_price - float(lvl)) / pip <= 100
    ]
    nearby.sort()
    if nearby:
        lines.append("Psychological levels (≤100 pips):")
        for dist, lvl, s in nearby:
            br  = s.get('bounce_rate')
            br_str = f"{br*100:.0f}%" if br is not None else "n/a"
            flag = " [STRONG]" if s.get('strong') else ""
            lines.append(
                f"  {lvl:>8}  dist={dist:.0f}p  "
                f"touches={s.get('touches',0)}  bounce={br_str}  "
                f"avg_reaction={s.get('avg_reaction_pips',0):.0f}p{flag}"
            )

    # Kill zones
    kz_data = p.get('kill_zones', {})
    if kz_data:
        lines.append("Kill zones:")
        for kz_name, kz in kz_data.items():
            lines.append(
                f"  {kz_name:<22} bull={kz.get('bullish_rate',0)*100:.0f}%  "
                f"avg_range={kz.get('avg_range_pips',0):.0f}p  n={kz.get('sample',0)}"
            )

    # Premium/Discount
    pd_data = p.get('premium_discount', {})
    if pd_data:
        d  = pd_data.get('discount_bull_rate')
        pr = pd_data.get('premium_bear_rate')
        lines.append(
            f"P/D zone: Discount→bull={f'{d*100:.0f}%' if d else 'n/a'} "
            f"(n={pd_data.get('discount_sample',0)})  "
            f"Premium→bear={f'{pr*100:.0f}%' if pr else 'n/a'} "
            f"(n={pd_data.get('premium_sample',0)})"
        )

    # FVG
    fvg_data = p.get('fvg', {})
    if fvg_data:
        mr = fvg_data.get('mitigation_rate')
        lines.append(
            f"FVG mitigation: {f'{mr*100:.0f}%' if mr else 'n/a'} "
            f"({fvg_data.get('mitigated',0)}/{fvg_data.get('total_fvgs',0)} FVGs)"
        )

    # Volatility
    vol_data = p.get('volatility', {})
    if vol_data:
        avg = vol_data.get('avg_daily_range_pips', 0)
        wd_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        wd_str = '  '.join(
            f"{wd_names[int(d)]}={v:.0f}p"
            for d, v in sorted(vol_data.get('by_weekday', {}).items())
        )
        lines.append(f"Volatility: avg={avg:.0f}p/day  {wd_str}")

    generated = hist_stats.get('_meta', {}).get('generated_at', '')[:10]
    if generated:
        lines.append(f"(stats generated {generated})")

    return '\n'.join(lines)
