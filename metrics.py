from typing import Any

from config import ZONE_BOUNDS, ZONE_LABELS, ZONE_WEIGHTS, hr_zone_index
from store import Run


def compute_trimp_and_zones(run: Run, records: list[dict[str, Any]]) -> Run:
    zone_seconds = [0.0] * 5

    for i in range(len(records) - 1):
        hr = records[i].get("heart_rate")
        if hr is None:
            continue
        dt_sec = records[i + 1]["timestamp"].timestamp() - records[i]["timestamp"].timestamp()
        zone_seconds[hr_zone_index(hr)] += dt_sec

    zone_minutes = [s / 60 for s in zone_seconds]
    trimp = sum(m * w for m, w in zip(zone_minutes, ZONE_WEIGHTS))

    run.trimp = round(trimp, 1)
    for label, minutes in zip(ZONE_LABELS, zone_minutes):
        setattr(run, label, round(minutes, 1))

    return run


def classify_run_type(run: Run) -> Run:
    duration_min = run.duration_s / 60
    z1_low = ZONE_BOUNDS[0][0]

    if duration_min < 25 and run.avg_hr < z1_low:
        run.run_type = "recovery"
    elif duration_min >= 50 and run.avg_hr <= ZONE_BOUNDS[1][1]:
        run.run_type = "long"
    else:
        run.run_type = "easy"

    return run
