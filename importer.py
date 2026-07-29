from pathlib import Path
import datetime as dt

from garmin_fit_sdk import Decoder, Stream

from store import Run


def decode_fit(path: Path) -> tuple[Run, list[dict]]:
    stream = Stream.from_file(str(path))
    decoder = Decoder(stream)
    messages, errors = decoder.read()

    if errors:
        raise RuntimeError(f"FIT decode errors for {path.name}: {errors}")

    session = messages["session_mesgs"][0]
    records = messages["record_mesgs"]

    date = session["start_time"].date()
    total_distance_m = session["total_distance"]
    total_timer_s = session["total_timer_time"]
    ascent = session.get("total_ascent") or 0

    hrs = [r["heart_rate"] for r in records if r.get("heart_rate") is not None]
    avg_hr = round(sum(hrs) / len(hrs)) if hrs else 0
    max_hr = max(hrs) if hrs else 0

    distance_km = total_distance_m / 1000
    pace_min_km = (total_timer_s / 60) / distance_km if distance_km > 0 else 0

    run = Run(
        date=date,
        file=path.name,
        distance_km=round(distance_km, 3),
        duration_s=total_timer_s,
        avg_hr=avg_hr,
        max_hr=max_hr,
        pace_min_km=round(pace_min_km, 2),
        ascent=ascent,
        calories=session.get("total_calories") or 0,
        trimp=0.0,
        run_type="unknown",
        zone_1_min=0.0,
        zone_2_min=0.0,
        zone_3_min=0.0,
        zone_4_min=0.0,
        zone_5_min=0.0,
    )

    return run, records
