MAX_HR = 190

ZONE_BOUNDS = [
    (0.50 * MAX_HR, 0.60 * MAX_HR),  # Z1: 50-60%
    (0.60 * MAX_HR, 0.70 * MAX_HR),  # Z2: 60-70%
    (0.70 * MAX_HR, 0.80 * MAX_HR),  # Z3: 70-80%
    (0.80 * MAX_HR, 0.90 * MAX_HR),  # Z4: 80-90%
    (0.90 * MAX_HR, MAX_HR),  # Z5: 90-100%
]

ZONE_WEIGHTS = [1, 2, 3, 4, 5]

ZONE_LABELS = ["zone_1_min", "zone_2_min", "zone_3_min", "zone_4_min", "zone_5_min"]


def hr_zone_index(hr: int) -> int:
    for i, (lo, hi) in enumerate(ZONE_BOUNDS):
        if lo <= hr < hi:
            return i
    return 4 if hr >= 0.90 * MAX_HR else 0
