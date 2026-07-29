from pathlib import Path

from importer import decode_fit
from metrics import compute_trimp_and_zones, classify_run_type
from store import Run
import datetime as dt


def test_trimp_and_zones_on_sample():
    path = Path("data/2026-07-28-12-53-43-Hike.fit")
    run, records = decode_fit(path)
    run = compute_trimp_and_zones(run, records)

    assert run.trimp > 0
    total_zone_min = (
        run.zone_1_min + run.zone_2_min + run.zone_3_min
        + run.zone_4_min + run.zone_5_min
    )
    assert abs(total_zone_min - 30.5) < 0.2


def test_classify_sample_as_easy():
    path = Path("data/2026-07-28-12-53-43-Hike.fit")
    run, records = decode_fit(path)
    run = compute_trimp_and_zones(run, records)
    run = classify_run_type(run)

    assert run.run_type == "easy"


def test_classify_recovery():
    run = Run(
        date=dt.date(2026, 7, 28), file="recovery.fit",
        distance_km=1.0, duration_s=600, avg_hr=85, max_hr=100,
        pace_min_km=10.0, ascent=0, calories=30,
        trimp=5.0, run_type="unknown",
        zone_1_min=10.0, zone_2_min=0.0, zone_3_min=0.0,
        zone_4_min=0.0, zone_5_min=0.0,
    )
    run = classify_run_type(run)
    assert run.run_type == "recovery"


def test_classify_long():
    run = Run(
        date=dt.date(2026, 7, 28), file="long.fit",
        distance_km=10.0, duration_s=3600, avg_hr=120, max_hr=140,
        pace_min_km=6.0, ascent=50, calories=500,
        trimp=50.0, run_type="unknown",
        zone_1_min=0.0, zone_2_min=60.0, zone_3_min=0.0,
        zone_4_min=0.0, zone_5_min=0.0,
    )
    run = classify_run_type(run)
    assert run.run_type == "long"
