import pytest
from app.core.models import Cargo, Vehicle

# Cargo


def test_cargo_volume():
    box = Cargo(
        length=0.5,
        width=0.4,
        height=0.3,
        weight=10,
    )

    assert box.volume == pytest.approx(0.06)


def test_cargo_non_positive_dimensions():
    with pytest.raises(ValueError) as exc_info:
        box = Cargo(
            length=0,
            width=0.4,
            height=0.3,
            weight=10,
        )

    assert "Cargo dimensions must be positive." in str(exc_info.value)


def test_cargo_non_positive_weight():
    with pytest.raises(ValueError) as exc_info:
        box = Cargo(
            length=0.5,
            width=0.4,
            height=0.3,
            weight=0,
        )

    assert "Cargo weight must be positive." in str(exc_info.value)


# Vehicle


def test_vehicle_volume():
    truck = Vehicle(
        length=5.0,
        width=2.5,
        height=2.0,
        max_weight=5000,
    )

    assert truck.volume == pytest.approx(25.0)


def test_vehicle_non_positive_dimensions():
    with pytest.raises(ValueError) as exc_info:
        truck = Vehicle(
            length=0,
            width=2.5,
            height=2.0,
            max_weight=5000,
        )

    assert "Vehicle dimensions must be positive." in str(exc_info.value)


def test_vehicle_non_positive_max_weight():
    with pytest.raises(ValueError) as exc_info:
        truck = Vehicle(
            length=5.0,
            width=2.5,
            height=2.0,
            max_weight=0,
        )

    assert "Vehicle weight must be positive." in str(exc_info.value)
