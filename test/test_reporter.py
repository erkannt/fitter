import datetime as dt

from reporter import compute_acwr, suggest_next_run
from store import Run


def _make_run(
    date: dt.date,
    distance_km: float = 5.0,
    duration_s: float = 1800,
    avg_hr: int = 130,
    max_hr: int = 160,
    trimp: float = 30.0,
    run_type: str = "easy",
) -> Run:
    return Run(
        date=date,
        file="test.fit",
        distance_km=distance_km,
        duration_s=duration_s,
        avg_hr=avg_hr,
        max_hr=max_hr,
        pace_min_km=duration_s / 60 / distance_km,
        ascent=10,
        calories=200,
        trimp=trimp,
        run_type=run_type,
        zone_1_min=10.0,
        zone_2_min=20.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
        ef=0.0,
    )


def test_compute_acwr_no_data() -> None:
    assert compute_acwr([]) == 0


def test_compute_acwr_equal() -> None:
    today = dt.date.today()
    runs = [_make_run(today - dt.timedelta(days=i), trimp=40.0) for i in range(10)]
    acwr = compute_acwr(runs)
    assert acwr > 0


def test_suggest_start() -> None:
    suggestion = suggest_next_run([], 0)
    assert "START" in suggestion


def test_suggest_rest_on_high_acwr() -> None:
    today = dt.date.today()
    runs = [_make_run(today - dt.timedelta(days=1), trimp=50.0)]
    suggestion = suggest_next_run(runs, 1.6)
    assert "REST" in suggestion
