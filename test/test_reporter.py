import datetime as dt

from store import Run
from reporter import compute_acwr, suggest_next_run


def _make_run(date, distance_km=5.0, duration_s=1800, avg_hr=130, max_hr=160,
              trimp=30.0, run_type="easy"):
    return Run(
        date=date, file="test.fit",
        distance_km=distance_km, duration_s=duration_s,
        avg_hr=avg_hr, max_hr=max_hr,
        pace_min_km=duration_s / 60 / distance_km,
        ascent=10, calories=200,
        trimp=trimp, run_type=run_type,
        zone_1_min=10.0, zone_2_min=20.0, zone_3_min=0.0,
        zone_4_min=0.0, zone_5_min=0.0,
    )


def test_compute_acwr_no_data():
    assert compute_acwr([]) == 0


def test_compute_acwr_equal():
    today = dt.date.today()
    runs = [_make_run(today - dt.timedelta(days=i), trimp=40.0) for i in range(10)]
    acwr = compute_acwr(runs)
    assert acwr > 0


def test_suggest_start():
    suggestion = suggest_next_run([], 0)
    assert "START" in suggestion


def test_suggest_rest_on_high_acwr():
    today = dt.date.today()
    runs = [_make_run(today - dt.timedelta(days=1), trimp=50.0)]
    suggestion = suggest_next_run(runs, 1.6)
    assert "REST" in suggestion
