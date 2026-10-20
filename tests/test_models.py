import pytest
from dataclasses import FrozenInstanceError

from app.core.models import Cargo, Vehicle, PlacedItem

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


def test_cargo_defaults():
    c = Cargo(length=1, width=1, height=1, weight=1)

    assert c.name == ""
    assert c.quantity == 1
    assert c.max_load_above == 0


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


# parametrize
@pytest.mark.parametrize(
    "x,y,z",
    [
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
    ],
)
def test_placed_item_negative_coordinates(x, y, z):
    cargo = Cargo(length=1, width=1, height=1, weight=1)

    with pytest.raises(ValueError):
        PlacedItem(cargo, x, y, z)


def test_placed_item_is_frozen():
    item = PlacedItem(Cargo(length=1, width=1, height=1, weight=1), 0, 0, 0)
    with pytest.raises(FrozenInstanceError):
        item.x = 5
