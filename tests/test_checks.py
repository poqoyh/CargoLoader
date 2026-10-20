import pytest
from app.core.models import Cargo, Vehicle, PlacedItem
from app.core.checks import (
    check_load,
    inside,
    overlaps,
    contact_area,
    is_supported,
    load_on,
    is_overloaded,
    validate,
)


def make_box(l=1, w=1, h=1, weight=1, **kwargs):
    return Cargo(length=l, width=w, height=h, weight=weight, **kwargs)


TRUCK = Vehicle(length=3, width=2, height=2, max_weight=1000)
A = PlacedItem(make_box(), 0, 0, 0)


def test_check_load_positive():
    box = Cargo(
        length=0.5,
        width=0.4,
        height=0.3,
        weight=10,
        quantity=20,
    )

    truck = Vehicle(
        length=3.0,
        width=1.9,
        height=1.8,
        max_weight=1500,
    )

    result = check_load(vehicle=truck, cargos=[box])

    assert result.fits == True
    assert result.volume_percent == pytest.approx((1.2 / 10.26) * 100)
    assert result.weight_percent == pytest.approx((200 / 1500) * 100)


def test_check_load_volume_exceeded():
    box = Cargo(
        length=0.5,
        width=0.4,
        height=0.3,
        weight=1,
        quantity=200,
    )

    truck = Vehicle(
        length=3.0,
        width=1.9,
        height=1.8,
        max_weight=1500,
    )

    result = check_load(vehicle=truck, cargos=[box])

    assert result.fits == False
    assert result.volume_percent == pytest.approx((12.0 / 10.26) * 100)
    assert result.weight_percent == pytest.approx((200 / 1500) * 100)


def test_check_load_weight_exceeded():
    box = Cargo(
        length=0.5,
        width=0.4,
        height=0.3,
        weight=200,
        quantity=10,
    )

    truck = Vehicle(
        length=3.0,
        width=1.9,
        height=1.8,
        max_weight=1500,
    )

    result = check_load(vehicle=truck, cargos=[box])

    assert result.fits == False
    assert result.volume_percent == pytest.approx((0.6 / 10.26) * 100)
    assert result.weight_percent == pytest.approx((2000 / 1500) * 100)


def test_check_load_empty_cargos():
    truck = Vehicle(
        length=3.0,
        width=1.9,
        height=1.8,
        max_weight=1500,
    )

    result = check_load(vehicle=truck, cargos=[])

    assert result.fits == True
    assert result.volume_percent == 0
    assert result.weight_percent == 0


def test_check_load_two_cargos():
    truck = Vehicle(3.0, 1.9, 1.8, 1500)
    small = Cargo(0.5, 0.4, 0.3, 10, quantity=10)
    pallet = Cargo(1.2, 0.8, 1.5, 100, quantity=3)
    result = check_load(truck, [small, pallet])
    assert result.volume_percent == pytest.approx((0.6 + 4.32) / 10.26 * 100)
    assert result.weight_percent == pytest.approx((100 + 300) / 1500 * 100)


def test_check_load_invalid_dimensions():
    with pytest.raises(ValueError):
        Cargo(
            length=0,
            width=0.4,
            height=0.3,
            weight=10,
        )

    with pytest.raises(ValueError):
        Cargo(
            length=0.5,
            width=-1,
            height=0.3,
            weight=10,
        )

    with pytest.raises(ValueError):
        Cargo(
            length=0.5,
            width=0.4,
            height=0,
            weight=10,
        )


# inside
def test_inside_at_origin():
    assert inside(TRUCK, PlacedItem(make_box(), 0, 0, 0)) is True


def test_inside_touching_far_walls():
    assert inside(TRUCK, PlacedItem(make_box(), 2, 1, 1)) is True


def test_inside_out_by_length():
    assert inside(TRUCK, PlacedItem(make_box(), 2.1, 0, 0)) is False


def test_inside_out_by_width():
    assert inside(TRUCK, PlacedItem(make_box(), 0, 1.1, 0)) is False


def test_inside_out_by_height():
    assert inside(TRUCK, PlacedItem(make_box(), 0, 0, 1.1)) is False


# overlaps
def test_overlap_partial():
    assert overlaps(A, PlacedItem(make_box(), 0.5, 0, 0)) is True


def test_overlap_touching_is_not_overlap():
    assert overlaps(A, PlacedItem(make_box(), 1, 0, 0)) is False


def test_overlap_far_away():
    assert overlaps(A, PlacedItem(make_box(), 5, 5, 5)) is False


def test_overlap_same_place():
    assert overlaps(A, PlacedItem(make_box(), 0, 0, 0)) is True


def test_overlap_stacked_on_z():
    assert overlaps(A, PlacedItem(make_box(), 0, 0, 1)) is False


def test_overlap_small_inside_big():
    big = PlacedItem(make_box(3, 3, 3), 0, 0, 0)
    small = PlacedItem(make_box(0.5, 0.5, 0.5), 1, 1, 1)
    assert overlaps(big, small) is True


def test_overlap_is_symmetric():
    b = PlacedItem(make_box(), 0.5, 0.5, 0.5)
    assert overlaps(A, b) == overlaps(b, A)


# contact_area


def test_contact_area_full():
    a = PlacedItem(make_box(), 0, 0, 0)
    assert contact_area(a, PlacedItem(make_box(), 0, 0, 1)) == pytest.approx(1)


def test_contact_area_half():
    a = PlacedItem(make_box(), 0, 0, 0)
    assert contact_area(a, PlacedItem(make_box(), 0.5, 0, 1)) == pytest.approx(0.5)


def test_contact_area_far_away():
    a = PlacedItem(make_box(), 0, 0, 0)
    assert contact_area(a, PlacedItem(make_box(), 5, 5, 1)) == 0


def test_contact_area_touching_by_edge():
    a = PlacedItem(make_box(), 0, 0, 0)
    assert contact_area(a, PlacedItem(make_box(), 1, 0, 1)) == 0


# is_supported


def test_supported_on_floor():
    item = PlacedItem(make_box(), 0, 0, 0)
    assert is_supported(item, [item]) is True


def test_supported_on_another_box():
    base = PlacedItem(make_box(), 0, 0, 0)
    item = PlacedItem(make_box(), 0, 0, 1)
    assert is_supported(item, [base, item]) is True


def test_not_supported_in_the_air():
    base = PlacedItem(make_box(), 0, 0, 0)
    item = PlacedItem(make_box(), 0, 0, 2)  # зазор в 1 м
    assert is_supported(item, [base, item]) is False


def test_not_supported_half_on_edge():
    base = PlacedItem(make_box(), 0, 0, 0)
    item = PlacedItem(make_box(), 0.5, 0, 1)  # опирается только половиной
    assert is_supported(item, [base, item]) is False


def test_supported_on_two_neighbours():
    left = PlacedItem(make_box(), 0, 0, 0)
    right = PlacedItem(make_box(), 1, 0, 0)
    item = PlacedItem(make_box(), 0.5, 0, 1)  # по половине на каждую
    assert is_supported(item, [left, right, item]) is True


# load_on / is_overloaded


def test_load_on_nothing_above():
    base = PlacedItem(make_box(max_load_above=30), 0, 0, 0)
    assert load_on(base, [base]) == 0
    assert is_overloaded(base, [base]) is False


def test_load_ok():
    base = PlacedItem(make_box(max_load_above=30), 0, 0, 0)
    top = PlacedItem(make_box(weight=20), 0, 0, 1)
    assert load_on(base, [base, top]) == 20
    assert is_overloaded(base, [base, top]) is False


def test_load_too_heavy():
    base = PlacedItem(make_box(max_load_above=30), 0, 0, 0)
    top = PlacedItem(make_box(weight=40), 0, 0, 1)
    assert is_overloaded(base, [base, top]) is True


def test_fragile_cannot_carry_anything():
    base = PlacedItem(make_box(max_load_above=0), 0, 0, 0)
    top = PlacedItem(make_box(weight=1), 0, 0, 1)
    assert is_overloaded(base, [base, top]) is True


def test_load_ignores_box_with_gap():
    base = PlacedItem(make_box(max_load_above=30), 0, 0, 0)
    far = PlacedItem(make_box(weight=40), 0, 0, 3)  # не на ней, а высоко
    assert load_on(base, [base, far]) == 0


# validate


def test_validate_ok():
    truck = Vehicle(3, 2, 2, 1000)
    base = PlacedItem(make_box(max_load_above=30), 0, 0, 0)
    top = PlacedItem(make_box(weight=20), 0, 0, 1)
    assert validate(truck, [base, top]) == []


def test_validate_outside():
    truck = Vehicle(3, 2, 2, 1000)
    item = PlacedItem(make_box(), 5, 0, 0)
    assert validate(truck, [item]) == ["item 0 is outside"]


def test_validate_overlap():
    truck = Vehicle(3, 2, 2, 1000)
    a = PlacedItem(make_box(), 0, 0, 0)
    b = PlacedItem(make_box(), 0.5, 0, 0)
    assert validate(truck, [a, b]) == ["items 0 and 1 overlap"]


def test_validate_not_supported():
    truck = Vehicle(3, 2, 4, 1000)
    base = PlacedItem(make_box(), 0, 0, 0)
    floating = PlacedItem(make_box(), 0, 0, 2)
    assert validate(truck, [base, floating]) == ["item 1 is not supported"]


def test_validate_overloaded():
    truck = Vehicle(3, 2, 2, 1000)
    fragile = PlacedItem(make_box(max_load_above=0), 0, 0, 0)
    top = PlacedItem(make_box(weight=1), 0, 0, 1)
    assert validate(truck, [fragile, top]) == ["item 0 is overloaded"]
