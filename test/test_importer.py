import datetime as dt
from pathlib import Path

from importer import decode_fit


def test_decode_sample_fit() -> None:
    path = Path("data/2026-07-28-12-53-43-Hike.fit")
    run, records = decode_fit(path)

    assert run.date == dt.date(2026, 7, 28)
    assert run.file == "2026-07-28-12-53-43-Hike.fit"
    assert run.distance_km == 2.275
    assert run.duration_s == 1831.0
    assert run.avg_hr == 109
    assert run.max_hr == 167
    assert run.pace_min_km == 13.42
    assert run.ascent == 13
    assert run.calories == 161
    assert len(records) == 370
