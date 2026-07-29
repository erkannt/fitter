from pathlib import Path

from importer import decode_fit
from metrics import classify_run_type, compute_ef, compute_trimp_and_zones
from reporter import print_report
from store import read_runs, write_runs

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = Path(__file__).parent / "runs.csv"


def main() -> None:
    existing = read_runs(CSV_PATH)
    known_files = {r.file for r in existing}
    fit_files = sorted(DATA_DIR.glob("*.fit"))

    new_runs = []
    for path in fit_files:
        if path.name in known_files:
            continue
        run, records = decode_fit(path)
        run = compute_trimp_and_zones(run, records)
        run = compute_ef(run, records)
        run = classify_run_type(run)
        new_runs.append(run)

    n_skipped = len(fit_files) - len(new_runs)
    if new_runs:
        existing = existing + new_runs
        write_runs(CSV_PATH, existing)

    if fit_files:
        import_msg = f"Imported {len(new_runs)} new (skipped {n_skipped} existing)"
    else:
        import_msg = None
    print_report(existing, import_msg)


if __name__ == "__main__":
    main()
