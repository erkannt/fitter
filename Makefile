.PHONY: report
report:
	uv run main.py

.PHONY: import
import:
	cp /run/media/hff/GARMIN/Garmin/Activity/*.fit ./data/


.PHONY: test
test:
	uv run pytest -v
