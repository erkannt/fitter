import csv
import datetime as dt
from dataclasses import astuple, dataclass, fields
from pathlib import Path


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


def write_runs(path: Path, runs: list[Run]) -> None:
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
            rows.append(
                Run(
                    date=dt.date.fromisoformat(row["date"]),
                    file=row["file"],
                    distance_km=float(row["distance_km"]),
                    duration_s=float(row["duration_s"]),
                    avg_hr=int(row["avg_hr"]) if row.get("avg_hr") else 0,
                    max_hr=int(row["max_hr"]) if row.get("max_hr") else 0,
                    pace_min_km=float(row["pace_min_km"]),
                    ascent=int(row["ascent"]) if row.get("ascent") else 0,
                    calories=int(row["calories"]) if row.get("calories") else 0,
                    trimp=float(row["trimp"]),
                    run_type=row["run_type"],
                    zone_1_min=float(row["zone_1_min"]),
                    zone_2_min=float(row["zone_2_min"]),
                    zone_3_min=float(row["zone_3_min"]),
                    zone_4_min=float(row["zone_4_min"]),
                    zone_5_min=float(row["zone_5_min"]),
                )
            )
    return rows
