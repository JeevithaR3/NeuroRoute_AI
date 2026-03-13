#!/usr/bin/env python3
"""
NeuroRoute CLI Dashboard — Layer 3
Real-time monitoring of queries, environmental impact, and system stats.

Usage:
  python3 dashboard.py           # Live tail mode
  python3 dashboard.py --stats   # Show aggregated stats
  python3 dashboard.py --queries # Show recent queries table
  python3 dashboard.py --watch   # Auto-refresh every 3s
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add middleware to path for logger import
sys.path.insert(0, str(Path(__file__).parent.parent / "middleware"))
from logger import get_stats, get_recent_queries

# ─── ANSI colors ─────────────────────────────────────────────────────────────

GREEN   = "\033[92m"
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
WHITE   = "\033[97m"
DIM     = "\033[2m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

def g(t): return f"{GREEN}{t}{RESET}"
def c(t): return f"{CYAN}{t}{RESET}"
def y(t): return f"{YELLOW}{t}{RESET}"
def w(t): return f"{WHITE}{BOLD}{t}{RESET}"
def d(t): return f"{DIM}{t}{RESET}"
def r(t): return f"{RED}{t}{RESET}"
def m(t): return f"{MAGENTA}{t}{RESET}"


# ─── Header ──────────────────────────────────────────────────────────────────

def print_header():
    print(f"\n{GREEN}{'═' * 60}{RESET}")
    print(f"{GREEN}  ⬡  {WHITE}{BOLD}NeuroRoute AI{RESET}{GREEN}  —  Layer 3 Monitoring Dashboard{RESET}")
    print(f"{GREEN}{'═' * 60}{RESET}")
    print(f"  {d('Green AI Router | Environmental Impact Tracker | Dataset Builder')}")
    print(f"  {d('Time: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    print(f"{GREEN}{'─' * 60}{RESET}\n")


# ─── Stats view ───────────────────────────────────────────────────────────────

def print_stats():
    stats = get_stats()
    n = stats["total_queries"]

    print_header()
    print(f"  {w('SYSTEM STATISTICS')}\n")

    # Query count
    print(f"  {'Total Queries Processed':<30} {g(str(n))}")

    if n == 0:
        print(f"\n  {d('No queries logged yet. Start using the extension!')}\n")
        return

    print(f"  {'Average Latency':<30} {c(str(stats['avg_latency']) + 's')}")
    print()

    # Environmental impact
    print(f"  {YELLOW}{'─' * 40}{RESET}")
    print(f"  {y('ENVIRONMENTAL IMPACT')}")
    print(f"  {YELLOW}{'─' * 40}{RESET}")
    e_str = f"{stats['total_energy_kwh']:.5f} kWh"
    c_str = f"{stats['total_carbon_kg']:.5f} kg"
    w_str = f"{stats['total_water_liters']:.5f} L"
    print(f"  {'⚡ Total Energy Used':<30} {g(e_str)}")
    print(f"  {'🌱 Total CO₂ Emitted':<30} {g(c_str)}")
    print(f"  {'💧 Total Water Used':<30} {g(w_str)}")

    # Per-query average
    print()
    print(f"  {d('Per-Query Averages:')}")
    eq_str = f"{stats['total_energy_kwh']/n:.6f} kWh"
    cq_str = f"{stats['total_carbon_kg']/n:.6f} kg"
    wq_str = f"{stats['total_water_liters']/n:.6f} L"
    print(f"  {'  ⚡ Energy / query':<30} {d(eq_str)}")
    print(f"  {'  🌱 CO₂ / query':<30} {d(cq_str)}")
    print(f"  {'  💧 Water / query':<30} {d(wq_str)}")

    # Model usage
    print()
    print(f"  {CYAN}{'─' * 40}{RESET}")
    print(f"  {c('MODEL USAGE')}")
    print(f"  {CYAN}{'─' * 40}{RESET}")
    usage = stats.get("model_usage", {})
    for model_id, count in sorted(usage.items(), key=lambda x: -x[1]):
        pct = round(count / n * 100)
        bar_len = pct // 4
        bar = "█" * bar_len + "░" * (25 - bar_len)
        name = model_id.replace("_", " ").title()
        color = g if "small" in model_id else (c if "medium" in model_id else m)
        print(f"  {name:<18} {color(bar)} {pct}% ({count})")

    # Complexity
    print()
    print(f"  {MAGENTA}{'─' * 40}{RESET}")
    print(f"  {m('COMPLEXITY BREAKDOWN')}")
    print(f"  {MAGENTA}{'─' * 40}{RESET}")
    cx = stats.get("complexity_breakdown", {})
    for level in ["LOW", "MEDIUM", "HIGH"]:
        count = cx.get(level, 0)
        pct = round(count / n * 100) if n else 0
        color = g if level == "LOW" else (y if level == "MEDIUM" else r)
        print(f"  {level:<10} {color(f'{pct:>3}%')}  {d(f'({count} queries)')}")

    print(f"\n{GREEN}{'═' * 60}{RESET}\n")


# ─── Recent queries table ─────────────────────────────────────────────────────

def print_queries(limit=20):
    queries = get_recent_queries(limit)

    print_header()
    print(f"  {w('RECENT QUERIES')}  {d(f'(last {len(queries)})')}\n")

    if not queries:
        print(f"  {d('No queries yet.')}\n")
        return

    # Header row
    print(f"  {BOLD}{'#':<4} {'TIME':<10} {'TASK':<12} {'CMPLX':<8} {'MODEL':<16} {'ENERGY':<14} {'CO₂':<12} {'PREVIEW'}{RESET}")
    print(f"  {'─'*4} {'─'*10} {'─'*12} {'─'*8} {'─'*16} {'─'*14} {'─'*12} {'─'*25}")

    for i, q in enumerate(reversed(queries), 1):
        ts = q.get("timestamp", "")[:16].replace("T", " ")
        task = q.get("task", "—")[:10]
        cx = q.get("complexity", "—")
        model = q.get("model_name", "—")[:14]
        energy = f"{q.get('energy_kwh', 0):.5f} kWh"
        carbon = f"{q.get('carbon_kg', 0):.5f} kg"
        preview = q.get("query_preview", "")[:30]

        cx_color = g if cx == "LOW" else (y if cx == "MEDIUM" else r)
        model_color = g if "Small" in model else (c if "Medium" in model else m)

        print(f"  {d(str(i)):<4} {d(ts):<10} {c(task):<12} {cx_color(cx):<8} {model_color(model):<16} {g(energy):<14} {g(carbon):<12} {d(preview)}")

    print(f"\n{GREEN}{'═' * 60}{RESET}\n")


# ─── Live watch mode ─────────────────────────────────────────────────────────

def watch_mode(interval=3):
    print(f"\n{g('  Watching for new queries... (Ctrl+C to exit)')}\n")
    last_count = 0
    try:
        while True:
            stats = get_stats()
            current_count = stats["total_queries"]
            if current_count != last_count:
                os.system("clear" if os.name == "posix" else "cls")
                print_stats()
                queries = get_recent_queries(5)
                if queries:
                    print(f"  {w('LAST 5 QUERIES')}\n")
                    for q in reversed(queries):
                        ts = q.get("timestamp", "")[:16].replace("T", " ")
                        model = q.get("model_name", "—")
                        task = q.get("task", "—")
                        energy = q.get("energy_kwh", 0)
                        preview = q.get("query_preview", "")[:50]
                        print(f"  {d(ts)}  {c(task.upper())}  {g(model)}")
                        print(f"  {d(preview)}")
                        print(f"  {g(f'⚡ {energy:.5f} kWh')}  {d('|')}  {d('Press Ctrl+C to exit')}\n")
                last_count = current_count
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n  {d('Dashboard stopped.')}\n")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroRoute CLI Dashboard")
    parser.add_argument("--stats",   action="store_true", help="Show aggregated stats")
    parser.add_argument("--queries", action="store_true", help="Show recent queries")
    parser.add_argument("--watch",   action="store_true", help="Auto-refresh watch mode")
    parser.add_argument("--limit",   type=int, default=20, help="Number of queries to show")
    args = parser.parse_args()

    if args.watch:
        watch_mode()
    elif args.queries:
        print_queries(args.limit)
    else:
        # Default: show both
        print_stats()
        print_queries(args.limit)
