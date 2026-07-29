#!/usr/bin/env python3
"""
run_tracker.py — Track running progress toward making the 1.2-mile commute trivial.

USAGE:
  1. Log runs in runs.csv (columns below). Export from your watch or enter manually.
  2. Run: python run_tracker.py

CSV columns:
  date,         distance_mi, duration_min, avg_hr, max_hr, rpe, type
  (date = YYYY-MM-DD, rpe = 1-10 perceived effort, type = commute|easy|long|tempo|intervals|recovery)
"""

import csv
import datetime as dt
from pathlib import Path
from statistics import mean

# ---- CONFIG ----
CSV_PATH = Path(__file__).parent / "runs.csv"
COMMUTE_DISTANCE = 1.2  # miles, one-way to the gym
MAX_HR = 190  # <<< SET THIS: your estimated max heart rate
Z2_LOW = 0.60 * MAX_HR  # Zone 2 floor (60% HRmax)
Z2_HIGH = 0.70 * MAX_HR  # Zone 2 ceiling (70% HRmax)
RECENT_WINDOW_DAYS = 28  # rolling window for "recent" stats

WORKOUT_TYPES = {
    "commute": "Run to/from the gym — this is your benchmark route.",
    "easy": "Zone 2, conversational. The bread & butter of aerobic base.",
    "long": "Easy pace, gradually extending beyond commute distance.",
    "tempo": "Comfortably hard, ~80-85% HRmax, sustained 15-25 min.",
    "intervals": "Hard intervals (e.g. 6x30s sprint / 90s easy) for speed.",
    "recovery": "Very easy, Zone 1, short. For active recovery days.",
}


# ---- DATA LOADING ----
def load_runs(path: Path) -> list[dict]:
    if not path.exists():
        print(f"No {path.name} found. Creating a template...")
        path.write_text(
            "date,distance_mi,duration_min,avg_hr,max_hr,rpe,type\n"
            "2026-07-29,1.2,12,165,178,5,commute\n"
        )
        print(f"Template created at {path}. Add your runs and re-run.\n")
        return []
    runs = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["date"] = dt.date.fromisoformat(row["date"])
            for k in ("distance_mi", "duration_min", "avg_hr", "max_hr", "rpe"):
                row[k] = float(row[k]) if row.get(k) else None
            runs.append(row)
    return runs


# ---- METRIC CALCULATIONS ----
def pace_min_per_mi(run: dict) -> float:
    """Returns pace in minutes per mile."""
    if run["distance_mi"] and run["duration_min"]:
        return run["duration_min"] / run["distance_mi"]
    return None


def pct_hrmax(run: dict) -> float:
    """Average HR as % of estimated max HR."""
    if run["avg_hr"]:
        return run["avg_hr"] / MAX_HR * 100
    return None


def in_zone2(run: dict) -> bool:
    hr = run["avg_hr"]
    return hr is not None and Z2_LOW <= hr <= Z2_HIGH


def split_recent_all(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    cutoff = dt.date.today() - dt.timedelta(days=RECENT_WINDOW_DAYS)
    recent = [r for r in runs if r["date"] >= cutoff]
    return recent, runs


def commute_runs(runs: list[dict]) -> list[dict]:
    return [r for r in runs if r["type"] == "commute"]


def early_vs_recent_commutes(commutes: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split commutes into first 3 and last 3 to show trend."""
    if len(commutes) < 4:
        return [], commutes
    return commutes[:3], commutes[-3:]


def weekly_volume(runs: list[dict]) -> dict:
    """Total miles per ISO week."""
    weeks = {}
    for r in runs:
        key = r["date"].isocalendar()[1]
        weeks.setdefault(key, 0.0)
        weeks[key] += r["distance_mi"]
    return weeks


def intensity_distribution(runs: list[dict]) -> dict:
    """Fraction of total time spent in low vs. high intensity (80/20 check)."""
    low_time = high_time = 0.0
    for r in runs:
        d = r["duration_min"] or 0
        p = pct_hrmax(r)
        if p is None:
            continue
        if p < 76:  # below Zone 3 = low intensity
            low_time += d
        else:  # Zone 3+ = moderate/high
            high_time += d
    total = low_time + high_time
    if total == 0:
        return {"low_pct": 0, "high_pct": 0}
    return {"low_pct": low_time / total * 100, "high_pct": high_time / total * 100}


# ---- SESSION RECOMMENDATION ENGINE ----
def recommend_session(recent: list[dict], all_runs: list[dict]) -> str:
    """Suggest what kind of run to do next based on recent training."""
    if not recent:
        return (
            "🚀 START: Do an EASY run (Zone 2, ~60-70% HRmax) of 1.5-2 miles.\n"
            "    Focus on keeping it conversational — you should be able to talk.\n"
            "    Log it and re-run this script next week."
        )

    last_7 = [r for r in recent if (dt.date.today() - r["date"]).days <= 7]
    days_run = len(last_7)
    last_run_date = max(r["date"] for r in recent)
    rest_days = (dt.date.today() - last_run_date).days

    # --- Check for rest needs ---
    if days_run >= 5:
        return (
            "🛑 REST DAY: You've run 5+ times in the last 7 days.\n"
            "    Take a rest or do a very short RECOVERY jog (Zone 1, <10 min).\n"
            "    Adaptation happens during recovery, not during the workout."
        )

    # --- Check what's missing this week ---
    week_types = {r["type"] for r in last_7}
    has_long = "long" in week_types
    has_hard = {"tempo", "intervals"} & week_types
    easy_count = sum(1 for r in last_7 if r["type"] in ("easy", "commute", "recovery"))

    # Priority 1: Weekly long run (most important for your goal)
    if not has_long and rest_days >= 1:
        longest = max(
            (r["distance_mi"] for r in all_runs if r["type"] == "long"), default=2.0
        )
        target = min(longest + 0.5, 6.0)  # cap at 6 miles for now
        return (
            f"🟢 LONG RUN: {target:.1f} miles at EASY pace (Zone 2).\n"
            f"    This is the #1 session for making {COMMUTE_DISTANCE} mi feel trivial.\n"
            f"    Keep HR in {Z2_LOW:.0f}-{Z2_HIGH:.0f} bpm. Talk the whole time.\n"
            f"    Your previous longest long run: {longest:.1f} mi."
        )

    # Priority 2: A speed session once a week (the "20" in 80/20)
    if not has_hard and easy_count >= 2 and rest_days >= 1:
        return (
            "🔴 SPEED SESSION: Do 6 x 30-second sprints with 90-second easy jog recovery.\n"
            "    Or a TEMPO run: 15 min easy warmup, 15 min at ~80-85% HRmax, 5 min cooldown.\n"
            "    This is your 20% hard effort for the week. Everything else should be easy."
        )

    # Priority 3: Easy aerobic base building
    if rest_days >= 1:
        return (
            f"🔵 EASY RUN: 2-3 miles at Zone 2 ({Z2_LOW:.0f}-{Z2_HIGH:.0f} bpm).\n"
            "    Conversational pace. This builds your aerobic engine.\n"
            "    Most of your runs should look like this."
        )

    return (
        "🟡 RECOVERY: You ran yesterday. If you run today, keep it to\n"
        "    a 10-15 min VERY easy jog (Zone 1) or take a rest/walk day."
    )


# ---- REPORTING ----
def print_report(runs: list[dict]):
    recent, all_runs = split_recent_all(runs)
    commutes = commute_runs(all_runs)
    early_c, recent_c = early_vs_recent_commutes(commutes)

    print("=" * 60)
    print("  🏃  RUN TRACKER — Commute Progress Report")
    print("=" * 60)

    # --- Overview ---
    total_mi = sum(r["distance_mi"] for r in all_runs)
    total_runs = len(all_runs)
    print(f"\n📊 ALL-TIME: {total_runs} runs, {total_mi:.1f} miles total")
    print(
        f"📅 Recent ({RECENT_WINDOW_DAYS}d): {len(recent)} runs, "
        f"{sum(r['distance_mi'] for r in recent):.1f} miles"
    )

    # --- Commute Benchmark (the key metric) ---
    print(f"\n{'─'*60}")
    print(f"🎯 COMMUTE BENCHMARK ({COMMUTE_DISTANCE} miles one-way)")
    print(f"{'─'*60}")
    if commutes:
        print(f"  Total commute runs logged: {len(commutes)}")
        avg_pace_all = mean(pace_min_per_mi(r) for r in commutes if pace_min_per_mi(r))
        avg_hr_all = mean(r["avg_hr"] for r in commutes if r["avg_hr"])
        print(
            f"  All-time avg pace: {fmt_pace(avg_pace_all)}  |  avg HR: {avg_hr_all:.0f} bpm"
        )

        if early_c and recent_c:
            ep = mean(pace_min_per_mi(r) for r in early_c if pace_min_per_mi(r))
            rp = mean(pace_min_per_mi(r) for r in recent_c if pace_min_per_mi(r))
            eh = mean(r["avg_hr"] for r in early_c if r["avg_hr"])
            rh = mean(r["avg_hr"] for r in recent_c if r["avg_hr"])
            er = mean(r["rpe"] for r in early_c if r["rpe"])
            rr_ = mean(r["rpe"] for r in recent_c if r["rpe"])

            print(f"\n  📈 TREND (first 3 vs last 3 commutes):")
            print(f"     {'':20s}{'Early':>10s}{'Recent':>10s}{'Δ':>10s}")
            print(
                f"     {'Pace (min/mi)':20s}{fmt_pace(ep):>10s}{fmt_pace(rp):>10s}"
                f"{fmt_pace(rp-ep)+'↑' if rp<ep else fmt_pace(rp-ep)+'↓':>10s}"
            )
            print(
                f"     {'Avg HR (bpm)':20s}{eh:>10.0f}{rh:>10.0f}" f"{(rh-eh):>+10.0f}"
            )
            print(
                f"     {'RPE (1-10)':20s}{er:>10.1f}{rr_:>10.1f}" f"{(rr_-er):>+10.1f}"
            )

            # Interpretation
            hr_drop = eh - rh
            if hr_drop > 3:
                print(
                    f"\n  ✅ Your heart rate dropped {hr_drop:.0f} bpm at similar pace."
                )
                print(
                    f"     The commute IS getting easier — your aerobic base is growing."
                )
            elif hr_drop < -3:
                print(
                    f"\n  ⚠️  Your HR increased {abs(hr_drop):.0f} bpm — you may be fatigued"
                )
                print(f"     or running harder. Consider more easy days and rest.")
            else:
                print(f"\n  ➡️  HR is stable — keep stacking easy miles and long runs.")
    else:
        print("  No commute runs logged yet. Log your gym jogs as type=commute!")

    # --- 80/20 Intensity Check ---
    print(f"\n{'─'*60}")
    print("⚖️  INTENSITY DISTRIBUTION (80/20 check, last 28 days)")
    print(f"{'─'*60}")
    dist = intensity_distribution(recent)
    print(f"  Low intensity:  {dist['low_pct']:.0f}%  (target: ~80%)")
    print(f"  Mod/High:       {dist['high_pct']:.0f}%  (target: ~20%)")
    if dist["low_pct"] < 70 and dist["low_pct"] > 0:
        print(
            "  ⚠️  You're running too hard too often! Slow down most of your runs to Zone 2."
        )
    elif dist["low_pct"] >= 75:
        print(
            "  ✅ Good — you're keeping most runs easy. This builds endurance safely."
        )

    # --- Weekly Volume ---
    print(f"\n{'─'*60}")
    print("📈 WEEKLY VOLUME (miles per week)")
    print(f"{'─'*60}")
    wv = weekly_volume(all_runs)
    for week, miles in sorted(wv.items()):
        bar = "█" * int(miles)
        print(f"  Week {week}: {miles:5.1f} mi {bar}")

    # --- Session Recommendation ---
    print(f"\n{'═'*60}")
    print("  🗓️  WHAT TO RUN NEXT")
    print(f"{'═'*60}")
    print()
    print(recommend_session(recent, all_runs))
    print()
    print("─" * 60)
    print("Workout type reference:")
    for wtype, desc in WORKOUT_TYPES.items():
        print(f"  {wtype:12s} — {desc}")
    print("─" * 60)


def fmt_pace(pace_min_per_mi: float) -> str:
    if pace_min_per_mi is None:
        return "--:--"
    mins = int(pace_min_per_mi)
    secs = int((pace_min_per_mi - mins) * 60)
    return f"{mins}:{secs:02d}"


# ---- MAIN ----
if __name__ == "__main__":
    runs = load_runs(CSV_PATH)
    if runs:
        print_report(runs)
