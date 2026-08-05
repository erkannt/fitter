.PHONY: report import mount eject test lint format typecheck check

GARMIN_DEV := $(shell lsblk -dno PATH,LABEL | awk '$$2 == "GARMIN" {print $$1; exit}')
GARMIN_MP  := /run/media/hff/GARMIN

report:
	uv run main.py

mount:
	test -n "$(GARMIN_DEV)"                    # fail loudly: device not plugged in
	@if ! mountpoint -q $(GARMIN_MP); then udisksctl mount -b $(GARMIN_DEV); fi

import: mount
	@cp $(GARMIN_MP)/Garmin/Activity/*Run.fit ./data/; \
	rc=$$?; \
	udisksctl unmount -b $(GARMIN_DEV); \
	exit $$rc

eject:
	udisksctl unmount -b $(GARMIN_DEV)

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
