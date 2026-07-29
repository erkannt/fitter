.PHONY: report
report:
	uv run main.py

.PHONY: import
import:
	cp /run/media/hff/GARMIN/Garmin/Activity/*.fit ./data/

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
	uv run mypy .

.PHONY: check
check: lint typecheck test
	@echo "All checks passed!"
