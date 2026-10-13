import pytest
from app.core.models import Cargo, Vehicle
from app.core.checks import check_load


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
