import datetime as dt

from config import ZONE_BOUNDS, ZONE_LABELS
from store import Run

RECENT_WINDOW = 28


def print_report(runs: list[Run]) -> None:
    if not runs:
        print("No runs in database. Import some FIT files first.")
        return

    today = dt.date.today()
    cutoff = today - dt.timedelta(days=RECENT_WINDOW)
    recent = [r for r in runs if r.date >= cutoff]

    print("=" * 60)
    print("  RUN DATABASE REPORT")
    print("=" * 60)

    print(f"\nAll-time: {len(runs)} runs, {sum(r.distance_km for r in runs):.1f} km")
    recent_km = sum(r.distance_km for r in recent)
    print(f"Recent ({RECENT_WINDOW}d): {len(recent)} runs, {recent_km:.1f} km")

    print_weekly_volume(runs)
    print_zone_breakdown(recent)
    print_type_distribution(runs)

    acwr = compute_acwr(runs)
    print_acwr(acwr)
    suggestion = suggest_next_run(runs, acwr)
    print_suggestion(suggestion)


def print_weekly_volume(runs: list[Run]) -> None:
    weeks: dict[int, float] = {}
    for r in runs:
        week = r.date.isocalendar()[1]
        weeks[week] = weeks.get(week, 0) + r.distance_km

    print(f"\n{'─' * 60}")
    print("WEEKLY VOLUME (km)")
    print(f"{'─' * 60}")
    for week, km in sorted(weeks.items()):
        bar = "█" * int(km)
        print(f"  Week {week}: {km:5.1f} km  {bar}")


def print_zone_breakdown(runs: list[Run]) -> None:
    print(f"\n{'─' * 60}")
    print("HEART RATE ZONE TIME (recent)")
    print(f"{'─' * 60}")

    if not runs:
        print("  No recent runs.")
        return

    totals = [0.0] * 5
    for r in runs:
        for i, label in enumerate(ZONE_LABELS):
            totals[i] += getattr(r, label)

    total_min = sum(totals)
    if total_min == 0:
        print("  No zone data available.")
        return

    for i, label in enumerate(ZONE_LABELS):
        lo = int(ZONE_BOUNDS[i][0])
        hi = int(ZONE_BOUNDS[i][1])
        pct = totals[i] / total_min * 100
        bar = "█" * int(pct / 5)
        print(f"  {label:12s} ({lo:3d}-{hi:3d} bpm): {totals[i]:6.1f} min  {pct:5.1f}%  {bar}")


def print_type_distribution(runs: list[Run]) -> None:
    print(f"\n{'─' * 60}")
    print("RUN TYPE DISTRIBUTION")
    print(f"{'─' * 60}")

    counts: dict[str, int] = {}
    for r in runs:
        counts[r.run_type] = counts.get(r.run_type, 0) + 1

    for t, c in sorted(counts.items()):
        bar = "█" * c
        print(f"  {t:12s}: {c}  {bar}")


def compute_acwr(runs: list[Run]) -> float:
    today = dt.date.today()
    acute = sum(r.trimp for r in runs if r.date >= today - dt.timedelta(days=7))
    chronic = sum(r.trimp for r in runs if r.date >= today - dt.timedelta(days=28))
    chronic_weekly = chronic / 4
    if chronic_weekly == 0:
        return 0
    return acute / chronic_weekly


def print_acwr(acwr: float) -> None:
    print(f"\n{'─' * 60}")
    print("RECOVERY & READINESS")
    print(f"{'─' * 60}")
    print(f"  ACWR (acute:chronic workload ratio): {acwr:.2f}")

    if acwr == 0:
        print("  Not enough data to assess. Keep training.")
    elif acwr < 0.8:
        print("  ⚠️  Low workload — consider increasing volume gradually.")
    elif acwr < 1.3:
        print("  ✅ Optimal training load — you're in the sweet spot.")
    elif acwr < 1.5:
        print("  ⚡ High workload — monitor fatigue, consider an easy day.")
    else:
        print("  🔴 Overreaching — high injury risk. Take a rest day.")


def suggest_next_run(runs: list[Run], acwr: float) -> str:
    today = dt.date.today()
    recent = [r for r in runs if r.date >= today - dt.timedelta(days=7)]

    if not recent:
        return "🚀 START: Do an EASY run (Zone 2, 60-70% HRmax) of 2-3 km."

    if acwr >= 1.5:
        return "🛑 REST DAY: ACWR indicates overreaching. Take a full rest day."

    days_7 = [r for r in recent if (today - r.date).days <= 7]
    days_ran = len(days_7)
    if days_ran >= 5:
        return "🛑 REST DAY: You've run 5+ times in the last 7 days. Recover."

    last_run_date = max(r.date for r in recent)
    rest_days = (today - last_run_date).days

    week_types = {r.run_type for r in days_7}
    has_long = "long" in week_types
    has_hard = {"tempo", "intervals"} & week_types
    easy_count = sum(1 for r in days_7 if r.run_type in ("easy", "recovery"))

    if not has_long and rest_days >= 1:
        longest = max((r.distance_km for r in runs if r.run_type == "long"), default=3.0)
        target = min(longest + 1.0, 10.0)
        z1_lo = int(ZONE_BOUNDS[0][0])
        z1_hi = int(ZONE_BOUNDS[1][1])
        return (
            f"🟢 LONG RUN: {target:.1f} km at EASY pace (Zone 2, {z1_lo}-{z1_hi} bpm).\n"
            f"    Previous longest long run: {longest:.1f} km."
        )

    if not has_hard and easy_count >= 2 and rest_days >= 1:
        return (
            "🔴 SPEED SESSION: 6 x 30s sprints with 90s jog recovery.\n"
            "    Or a TEMPO run: 15 min warmup, 15 min at 80-85% HRmax, 5 min cooldown."
        )

    if rest_days >= 1:
        z1_lo = int(ZONE_BOUNDS[0][0])
        z1_hi = int(ZONE_BOUNDS[1][1])
        return f"🔵 EASY RUN: 3-5 km at Zone 2 ({z1_lo}-{z1_hi} bpm)."

    return "🟡 RECOVERY: You ran yesterday. Short easy jog or rest."


def print_suggestion(suggestion: str) -> None:
    print(f"\n{'═' * 60}")
    print("  WHAT TO RUN NEXT")
    print(f"{'═' * 60}")
    print()
    print(suggestion)
    print()
