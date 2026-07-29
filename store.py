from dataclasses import dataclass, fields, astuple
from pathlib import Path
import csv
import datetime as dt


@dataclass
class Run:
    date: dt.date
    file: str
    distance_km: float
    duration_s: float
    avg_hr: int
    max_hr: int
    pace_min_km: float
    ascent: int
    calories: int
    trimp: float
    run_type: str
    zone_1_min: float
    zone_2_min: float
    zone_3_min: float
    zone_4_min: float
    zone_5_min: float


FIELD_NAMES = [f.name for f in fields(Run)]


def write_runs(path: Path, runs: list[Run]):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FIELD_NAMES)
        for run in runs:
            writer.writerow(astuple(run))


def read_runs(path: Path) -> list[Run]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            row["date"] = dt.date.fromisoformat(row["date"])
            for k in ("distance_km", "duration_s", "pace_min_km", "trimp"):
                row[k] = float(row[k])
            for k in ("avg_hr", "max_hr", "ascent", "calories"):
                row[k] = int(row[k]) if row.get(k) else 0
            for k in ("zone_1_min", "zone_2_min", "zone_3_min", "zone_4_min", "zone_5_min"):
                row[k] = float(row[k])
            rows.append(Run(**row))
    return rows
