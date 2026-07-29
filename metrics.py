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


def compute_ef(run: Run, records: list[dict[str, Any]]) -> Run:
    if run.avg_hr == 0:
        return run

    ngs_values: list[float] = []
    for i in range(len(records) - 1):
        speed = records[i].get("enhanced_speed") or records[i].get("speed")
        if speed is None or speed < 0.5:
            continue

        alt = records[i].get("enhanced_altitude") or records[i].get("altitude")
        alt_next = records[i + 1].get("enhanced_altitude") or records[i + 1].get("altitude")
        if alt is None or alt_next is None:
            continue

        dist = records[i].get("distance")
        dist_next = records[i + 1].get("distance")
        if dist is None or dist_next is None:
            continue

        dz = alt_next - alt
        dx = dist_next - dist
        if dx < 0.5:
            continue

        grade_pct = (dz / dx) * 100
        grade_pct = max(min(grade_pct, 50), -50)

        speed_m_min = speed * 60
        if grade_pct > 0:
            ngs = speed_m_min * (1 + grade_pct * 0.04)
        else:
            ngs = speed_m_min * (1 + grade_pct * 0.02)

        ngs_values.append(ngs)

    if not ngs_values:
        return run

    avg_ngs = sum(ngs_values) / len(ngs_values)
    run.ef = round(avg_ngs / run.avg_hr, 2)
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
