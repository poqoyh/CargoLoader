from dataclasses import asdict

import pytest
from app.core.models import Cargo, Vehicle
from app.core.service import pack_cargo


def test_pack_cargo_example_from_plan():
    truck = Vehicle(3.0, 1.9, 1.8, 1500)
    box = Cargo(0.5, 0.4, 0.3, 10, quantity=20)

    result = pack_cargo(truck, [box])

    assert len(result.placed) == 20
    assert result.not_placed == []
    assert result.problems == []
    assert result.volume_percent == pytest.approx(1.2 / 10.26 * 100)
    assert result.weight_percent == pytest.approx(200 / 1500 * 100)


def test_pack_cargo_empty():
    result = pack_cargo(Vehicle(3, 2, 2, 1000), [])
    assert result.placed == [] and result.not_placed == []
    assert result.volume_percent == 0 and result.weight_percent == 0
    assert result.center_of_mass == (0.0, 0.0, 0.0)
    assert result.axle_loads is None
    assert result.problems == [] and result.warnings == []


def test_pack_cargo_reports_not_placed():
    truck = Vehicle(3, 2, 2, 5)  # грузоподъёмность 5 кг
    result = pack_cargo(truck, [Cargo(1, 2, 3, 2, quantity=10, max_load_above=100)])
    assert len(result.placed) == 2
    assert len(result.not_placed) == 8
    assert result.weight_percent == pytest.approx(4 / 5 * 100)


def test_pack_cargo_has_axle_loads_when_axles_given():
    truck = Vehicle(3, 2, 2, 1000, front_axle_x=0.5, rear_axle_x=2.5)
    result = pack_cargo(truck, [Cargo(1, 2, 1, 100)])
    front, rear = result.axle_loads
    assert front + rear == pytest.approx(100)


def test_pack_cargo_warns_when_load_is_off_center():
    result = pack_cargo(Vehicle(3, 2, 2, 1000), [Cargo(1, 0.5, 0.5, 10)])
    assert len(result.warnings) == 1


def test_pack_cargo_result_converts_to_dict():
    truck = Vehicle(3, 2, 2, 1000)
    result = pack_cargo(truck, [Cargo(1, 2, 1, 10, name="A")])

    data = asdict(result)

    assert data["placed"][0]["cargo"]["name"] == "A"
    assert data["placed"][0]["x"] == 0
    assert data["problems"] == []
    assert set(data) == {
        "placed", "not_placed", "volume_percent", "weight_percent",
        "center_of_mass", "axle_loads", "problems", "warnings",
    }
