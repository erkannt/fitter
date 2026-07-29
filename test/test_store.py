import datetime as dt
from pathlib import Path
from tempfile import mkdtemp

from store import FIELD_NAMES, Run, read_runs, write_runs


def test_round_trip() -> None:
    runs = [
        Run(
            date=dt.date(2026, 7, 28),
            file="2026-07-28-12-53-43-Hike.fit",
            distance_km=2.275,
            duration_s=1831.0,
            avg_hr=109,
            max_hr=167,
            pace_min_km=13.42,
            ascent=13,
            calories=161,
            trimp=45.0,
            run_type="easy",
            zone_1_min=10.0,
            zone_2_min=15.0,
            zone_3_min=5.0,
            zone_4_min=0.0,
            zone_5_min=0.0,
        ),
    ]

    tmp = Path(mkdtemp()) / "runs.csv"
    write_runs(tmp, runs)
    loaded = read_runs(tmp)

    assert len(loaded) == 1
    for run in loaded:
        assert run.date == dt.date(2026, 7, 28)
        assert run.file == "2026-07-28-12-53-43-Hike.fit"
        assert run.distance_km == 2.275
        assert run.trimp == 45.0
        assert run.run_type == "easy"
        assert run.zone_1_min == 10.0


def test_field_names_order() -> None:
    assert FIELD_NAMES == [
        "date",
        "file",
        "distance_km",
        "duration_s",
        "avg_hr",
        "max_hr",
        "pace_min_km",
        "ascent",
        "calories",
        "trimp",
        "run_type",
        "zone_1_min",
        "zone_2_min",
        "zone_3_min",
        "zone_4_min",
        "zone_5_min",
    ]


def test_read_empty_file() -> None:
    tmp = Path(mkdtemp()) / "runs.csv"
    assert read_runs(tmp) == []
