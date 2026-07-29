.PHONY: report
report:
	uv run main.py

.PHONY: import
import:
	cp /run/media/hff/GARMIN/Garmin/Activity/*Run.fit ./data/

.PHONY: test
test:
	uv run pytest -v

.PHONY: lint
lint:
	uv run ruff check

.PHONY: format
format:
	uv run ruff format

.PHONY: typecheck
typecheck:
	uv run python3 -m mypy . --no-incremental --cache-dir /tmp/mypy-cache

.PHONY: check
check: lint typecheck test
	@echo "All checks passed!"
