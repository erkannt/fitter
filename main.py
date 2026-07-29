from pathlib import Path

from importer import decode_fit
from metrics import classify_run_type, compute_trimp_and_zones
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
            print(f"  skipping {path.name} (already imported)")
            continue
        print(f"  importing {path.name}...")
        run, records = decode_fit(path)
        run = compute_trimp_and_zones(run, records)
        run = classify_run_type(run)
        new_runs.append(run)

    if new_runs:
        existing = existing + new_runs
        write_runs(CSV_PATH, existing)
        print(f"Imported {len(new_runs)} run(s). Total runs: {len(existing)}")

    print_report(existing)


if __name__ == "__main__":
    main()
