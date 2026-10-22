import pytest
from app.core.models import Cargo, Vehicle, PlacedItem
from app.core.balance import center_of_mass, axle_loads, balance_warnings


def make_box(l=1, w=1, h=1, weight=1, **kwargs):
    return Cargo(length=l, width=w, height=h, weight=weight, **kwargs)


def test_center_of_mass_empty():
    assert center_of_mass([]) == (0.0, 0.0, 0.0)


def test_center_of_mass_single_box():
    item = PlacedItem(make_box(2, 4, 6), 1, 1, 1)
    assert center_of_mass([item]) == pytest.approx((2, 3, 4))


def test_center_of_mass_two_equal_boxes():
    a = PlacedItem(make_box(1, 2, 1), 0, 0, 0)
    b = PlacedItem(make_box(1, 2, 1), 2, 0, 0)
    cx, cy, cz = center_of_mass([a, b])
    assert cx == pytest.approx(1.5)  # посередине между центрами 0.5 и 2.5


def test_center_of_mass_closer_to_heavy_box():
    light = PlacedItem(make_box(1, 2, 1, weight=10), 0, 0, 0)    # центр x=0.5
    heavy = PlacedItem(make_box(1, 2, 1, weight=30), 2, 0, 0)    # центр x=2.5
    cx, _, _ = center_of_mass([light, heavy])
    assert cx == pytest.approx((10 * 0.5 + 30 * 2.5) / 40)


#оси

AXLES = Vehicle(3, 2, 2, 1000, front_axle_x=0.5, rear_axle_x=2.5)


def test_axle_loads_none_without_axles():
    item = PlacedItem(make_box(), 0, 0, 0)
    assert axle_loads(Vehicle(3, 2, 2, 1000), [item]) is None


def test_axle_loads_empty():
    assert axle_loads(AXLES, []) == (0.0, 0.0)


def test_axle_loads_even():
    item = PlacedItem(make_box(1, 2, 1, weight=100), 1, 0, 0)  # центр x=1.5
    assert axle_loads(AXLES, [item]) == pytest.approx((50, 50))


def test_axle_loads_over_rear_axle():
    item = PlacedItem(make_box(1, 2, 1, weight=100), 2, 0, 0)  # центр x=2.5
    assert axle_loads(AXLES, [item]) == pytest.approx((0, 100))


def test_axle_loads_over_front_axle():
    item = PlacedItem(make_box(1, 2, 1, weight=100), 0, 0, 0)  # центр x=0.5
    assert axle_loads(AXLES, [item]) == pytest.approx((100, 0))


def test_axle_loads_sum_equals_total_weight():
    a = PlacedItem(make_box(1, 2, 1, weight=30), 0, 0, 0)
    b = PlacedItem(make_box(1, 2, 1, weight=70), 1.7, 0, 0)
    front, rear = axle_loads(AXLES, [a, b])
    assert front + rear == pytest.approx(100)


#боковой баланс

def test_balance_warning_when_off_center():
    truck = Vehicle(3, 2, 2, 1000)
    item = PlacedItem(make_box(1, 0.5, 0.5), 0, 0, 0)  # у стенки, центр y=0.25
    warnings = balance_warnings(truck, [item])
    assert len(warnings) == 1 and "off-center" in warnings[0]


def test_no_balance_warning_when_symmetric():
    truck = Vehicle(3, 2, 2, 1000)
    a = PlacedItem(make_box(1, 0.5, 0.5), 0, 0, 0)
    b = PlacedItem(make_box(1, 0.5, 0.5), 0, 1.5, 0)
    assert balance_warnings(truck, [a, b]) == []


def test_no_balance_warning_when_empty():
    assert balance_warnings(Vehicle(3, 2, 2, 1000), []) == []
