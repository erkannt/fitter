from config import hr_zone_index, ZONE_BOUNDS, MAX_HR


def test_hr_zone_index_below_z1():
    assert hr_zone_index(0) == 0


def test_hr_zone_index_boundary():
    z1_top = int(ZONE_BOUNDS[0][1])
    assert hr_zone_index(z1_top - 1) == 0
    assert hr_zone_index(z1_top) == 1


def test_hr_zone_index_max():
    assert hr_zone_index(MAX_HR - 1) == 4
    assert hr_zone_index(MAX_HR) == 4


def test_hr_zone_index_mid_z3():
    z3_lo = int(ZONE_BOUNDS[2][0])
    z3_hi = int(ZONE_BOUNDS[2][1])
    mid = (z3_lo + z3_hi) // 2
    assert hr_zone_index(mid) == 2


def test_hr_zone_index_at_z1_boundary():
    z1_lo = int(ZONE_BOUNDS[0][0])
    assert hr_zone_index(z1_lo) == 0
