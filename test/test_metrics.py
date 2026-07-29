import datetime as dt
from pathlib import Path

from importer import decode_fit
from metrics import classify_run_type, compute_ef, compute_trimp_and_zones
from store import Run


def test_trimp_and_zones_on_sample() -> None:
    path = Path("test/test_data/dummy_activity.fit")
    run, records = decode_fit(path)
    run = compute_trimp_and_zones(run, records)

    assert run.trimp > 0
    total_zone_min = (
        run.zone_1_min + run.zone_2_min + run.zone_3_min + run.zone_4_min + run.zone_5_min
    )
    assert abs(total_zone_min - 30.5) < 0.2


def test_classify_sample_as_easy() -> None:
    path = Path("test/test_data/dummy_activity.fit")
    run, records = decode_fit(path)
    run = compute_trimp_and_zones(run, records)
    run = classify_run_type(run)

    assert run.run_type == "easy"


def test_ef_on_dummy_fit() -> None:
    path = Path("test/test_data/dummy_activity.fit")
    run, records = decode_fit(path)
    run = compute_trimp_and_zones(run, records)
    run = compute_ef(run, records)

    assert run.ef > 0


def test_ef_missing_data() -> None:
    run = Run(
        date=dt.date(2026, 7, 28),
        file="no_data.fit",
        distance_km=5.0,
        duration_s=1800,
        avg_hr=140,
        max_hr=170,
        pace_min_km=6.0,
        ascent=0,
        calories=300,
        trimp=30.0,
        run_type="easy",
        zone_1_min=10.0,
        zone_2_min=20.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
        ef=0.0,
    )
    records = [{"heart_rate": 130}, {"heart_rate": 140}]
    assert compute_ef(run, records).ef == 0


def test_ef_zero_hr() -> None:
    run = Run(
        date=dt.date(2026, 7, 28),
        file="no_hr.fit",
        distance_km=5.0,
        duration_s=1800,
        avg_hr=0,
        max_hr=0,
        pace_min_km=6.0,
        ascent=0,
        calories=300,
        trimp=0.0,
        run_type="easy",
        zone_1_min=0.0,
        zone_2_min=0.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
        ef=0.0,
    )
    assert compute_ef(run, []).ef == 0


def test_classify_recovery() -> None:
    run = Run(
        date=dt.date(2026, 7, 28),
        file="recovery.fit",
        distance_km=1.0,
        duration_s=600,
        avg_hr=85,
        max_hr=100,
        pace_min_km=10.0,
        ascent=0,
        calories=30,
        trimp=5.0,
        run_type="unknown",
        zone_1_min=10.0,
        zone_2_min=0.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
        ef=0.0,
    )
    run = classify_run_type(run)
    assert run.run_type == "recovery"


def test_classify_long() -> None:
    run = Run(
        date=dt.date(2026, 7, 28),
        file="long.fit",
        distance_km=10.0,
        duration_s=3600,
        avg_hr=120,
        max_hr=140,
        pace_min_km=6.0,
        ascent=50,
        calories=500,
        trimp=50.0,
        run_type="unknown",
        zone_1_min=0.0,
        zone_2_min=60.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
        ef=0.0,
    )
    run = classify_run_type(run)
    assert run.run_type == "long"
