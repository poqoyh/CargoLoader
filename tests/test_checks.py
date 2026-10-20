import pytest
from app.core.models import Cargo, Vehicle, PlacedItem
from app.core.checks import check_load, inside, overlaps


def make_box(l=1, w=1, h=1, weight=1):
    return Cargo(length=l, width=w, height=h, weight=weight)


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
