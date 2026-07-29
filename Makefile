.PHONY: import
import:
	cp /run/media/hff/GARMIN/Garmin/Activity/*-Hike.fit ./data/

.PHONY: analyse
analyse:
	uv run main.py
