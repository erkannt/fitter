.PHONY: import
import:
	cp /run/media/hff/GARMIN/Garmin/Activity/*.fit ./data/

.PHONY: analyse
analyse:
	uv run main.py

.PHONY: test
test:
	uv run pytest -v
