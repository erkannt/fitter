import datetime as dt

from config import ZONE_BOUNDS, ZONE_LABELS
from store import Run

RECENT_WINDOW = 28


def _pace_mmss(pace_min_km: float) -> str:
    minutes = int(pace_min_km)
    seconds = int((pace_min_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


def _dur_hhmm(seconds: float) -> str:
    minutes = int(seconds // 60)
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02d}"


def _zone_str(run: Run) -> str:
    parts = []
    for label in ZONE_LABELS:
        v = getattr(run, label)
        parts.append(f"{int(v):>2d}" if v > 0 else "--")
    return " ".join(parts)


def print_report(runs: list[Run], import_msg: str | None = None) -> None:
    if not runs:
        print("No runs in database. Import some FIT files first.")
        return

    today = dt.date.today()
    cutoff_recent = today - dt.timedelta(days=RECENT_WINDOW)
    recent = [r for r in runs if r.date >= cutoff_recent]
    cutoff_7d = today - dt.timedelta(days=7)
    week = [r for r in runs if r.date >= cutoff_7d]

    all_runs = len(runs)
    all_km = sum(r.distance_km for r in runs)
    all_dur = sum(r.duration_s for r in runs)
    recent_runs = len(recent)
    recent_km = sum(r.distance_km for r in recent)
    recent_dur = sum(r.duration_s for r in recent)
    week_runs = len(week)
    week_km = sum(r.distance_km for r in week)
    week_dur = sum(r.duration_s for r in week)

    print("=" * 60)
    print("  YOUR RUNNING")
    print("=" * 60)
    if import_msg:
        print(import_msg)
    print()
    print(f"    {'RUNS':>5s}  {'KM':>5s}  {'DURATION':>7s}")
    print(f"all  {all_runs:>5d}  {all_km:>5.1f}  {_dur_hhmm(all_dur):>7s}")
    print(f"28d  {recent_runs:>5d}  {recent_km:>5.1f}  {_dur_hhmm(recent_dur):>7s}")
    print(f" 7d  {week_runs:>5d}  {week_km:>5.1f}  {_dur_hhmm(week_dur):>7s}")

    print(f"\n{'─' * 60}")
    print("LAST SEVEN DAYS")
    print(f"{'─' * 60}")

    if not week:
        print("  No runs in the last 7 days.")
    else:
        _print_last_seven_days(week)

    if week:
        print()
        _print_zone_histogram(week)

    print(f"\n{'═' * 60}")
    print("  RECOVERY & NEXT RUN")
    print(f"{'═' * 60}")
    print()
    acwr = compute_acwr(runs)
    suggestion = suggest_next_run(runs, acwr)
    print_acwr(acwr)
    print()
    print_suggestion(suggestion)


def _print_last_seven_days(week: list[Run]) -> None:
    show_ef = any(r.ef > 0 for r in week)
    sep = "  "

    cols: list[tuple[str, int, str]] = [
        ("", 6, "left"),
        ("KM", 5, "right"),
        ("TRIMP", 5, "right"),
        ("PACE", 5, "right"),
        ("MINUTES/HRZONE", 14, "right"),
        ("TYPE", 6, "left"),
    ]
    if show_ef:
        cols.append(("EF", 5, "right"))

    def _cell(s: str, w: int, a: str) -> str:
        return f"{s:>{w}s}" if a == "right" else f"{s:<{w}s}"

    print(" " + sep.join(_cell(label, w, a) for label, w, a in cols))

    for r in sorted(week, key=lambda x: x.date):
        day_label = f"  {r.date:%a}:"
        pace_str = _pace_mmss(r.pace_min_km)
        zones = _zone_str(r)

        vals = [
            day_label,
            f"{r.distance_km:.1f}",
            f"{r.trimp:.0f}",
            pace_str,
            zones,
            r.run_type,
        ]
        if show_ef:
            ef_str = f"{r.ef:.2f}" if r.ef > 0 else "--"
            vals.append(ef_str)

        row = sep.join(_cell(v, w, a) for v, (_, w, a) in zip(vals, cols))
        print(" " + row)


def _print_zone_histogram(week: list[Run]) -> None:
    zone_mins = [0.0] * 5
    for r in week:
        for i, label in enumerate(ZONE_LABELS):
            zone_mins[i] += getattr(r, label)

    total = sum(zone_mins)

    if total == 0:
        print("  No HR zone data available.")
        return

    print(f"          MIN  {'%':>3s}  BAR")

    for i in range(5):
        mins = zone_mins[i]
        pct = mins / total * 100
        bar_len = int(pct / 5)
        lo = int(ZONE_BOUNDS[i][0])
        hi = int(ZONE_BOUNDS[i][1])
        print(
            f"  Z{i+1} ({lo:>3d}-{hi:>3d})  {int(mins):>3d}  {int(pct):>3d}%  {'█' * bar_len}"
        )


def compute_acwr(runs: list[Run]) -> float:
    today = dt.date.today()
    acute = sum(r.trimp for r in runs if r.date >= today - dt.timedelta(days=7))
    chronic = sum(r.trimp for r in runs if r.date >= today - dt.timedelta(days=28))
    chronic_weekly = chronic / 4
    if chronic_weekly == 0:
        return 0
    return acute / chronic_weekly


def print_acwr(acwr: float) -> None:
    print(f"  ACWR: {acwr:.2f}")

    if acwr == 0:
        print("  Not enough data to assess. Keep training.")
    elif acwr < 0.8:
        print("\u26a0\ufe0f  Low workload \u2014 consider increasing volume gradually.")
    elif acwr < 1.3:
        print("\u2705 Optimal training load \u2014 you're in the sweet spot.")
    elif acwr < 1.5:
        print("\u26a1 High workload \u2014 monitor fatigue, consider an easy day.")
    else:
        print("\U0001f534 Overreaching \u2014 high injury risk. Take a rest day.")


def suggest_next_run(runs: list[Run], acwr: float) -> str:
    today = dt.date.today()
    recent = [r for r in runs if r.date >= today - dt.timedelta(days=7)]

    if not recent:
        return "  START: Do an EASY run (Zone 2, 60-70% HRmax) of 2-3 km."

    if acwr >= 1.5:
        return "  REST DAY: ACWR indicates overreaching. Take a rest day."

    days_7 = [r for r in recent if (today - r.date).days <= 7]
    days_ran = len(days_7)
    if days_ran >= 5:
        return "  REST DAY: You've run 5+ times in the last 7 days. Recover."

    last_run_date = max(r.date for r in recent)
    rest_days = (today - last_run_date).days

    week_types = {r.run_type for r in days_7}
    has_long = "long" in week_types
    has_hard = {"tempo", "intervals"} & week_types
    easy_count = sum(1 for r in days_7 if r.run_type in ("easy", "recovery"))

    if not has_long and rest_days >= 1:
        longest = max(
            (r.distance_km for r in runs if r.run_type == "long"), default=3.0
        )
        target = min(longest + 1.0, 10.0)
        z1_lo = int(ZONE_BOUNDS[0][0])
        z1_hi = int(ZONE_BOUNDS[1][1])
        return (
            f"  LONG RUN: {target:.1f} km at EASY pace (Zone 2, {z1_lo}-{z1_hi} bpm).\n"
            f"    Previous longest long run: {longest:.1f} km."
        )

    if not has_hard and easy_count >= 2 and rest_days >= 1:
        return (
            "  SPEED SESSION: 6 x 30s sprints with 90s jog recovery.\n"
            "    Or a TEMPO run: 15 min warmup, 15 min at 80-85% HRmax, 5 min cooldown."
        )

    if rest_days >= 1:
        z1_lo = int(ZONE_BOUNDS[0][0])
        z1_hi = int(ZONE_BOUNDS[1][1])
        return f" EASY RUN: 3-5 km at Zone 2 ({z1_lo}-{z1_hi} bpm)."

    return "  RECOVERY: You ran yesterday. Short easy jog or rest."


def print_suggestion(suggestion: str) -> None:
    print(suggestion)
    print()
