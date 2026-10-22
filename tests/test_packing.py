import pytest

import random

from app.core.models import Cargo, Vehicle, PlacedItem
from app.core.checks import inside, overlaps, validate
from app.core.packing import expand, pack_layers, orientations, candidate_points, pack


def make_box(l=1, w=1, h=1, weight=1, **kwargs):
    return Cargo(length=l, width=w, height=h, weight=weight, **kwargs)


# expand


def test_expand_quantity():
    items = expand([make_box(quantity=3)])
    assert len(items) == 3
    assert all(item.quantity == 1 for item in items)


def test_expand_keeps_fields():
    items = expand([make_box(name="A", max_load_above=30, quantity=2)])
    assert all(i.name == "A" and i.max_load_above == 30 for i in items)


def test_expand_does_not_change_original():
    box = make_box(quantity=3)
    expand([box])
    assert box.quantity == 3


def test_expand_empty():
    assert expand([]) == []


def test_expand_several_cargos():
    items = expand([make_box(quantity=2), make_box(2, 2, 2, quantity=3)])
    assert len(items) == 5


# pack


def test_pack_layers_empty():
    assert pack_layers(Vehicle(3, 1, 1, 1000), []) == ([], [])


def test_pack_layers_single_box_at_origin():
    placed, not_placed = pack_layers(Vehicle(3, 2, 2, 1000), [make_box()])
    assert not_placed == []
    assert (placed[0].x, placed[0].y, placed[0].z) == (0, 0, 0)


def test_pack_layers_row_along_x():
    placed, not_placed = pack_layers(Vehicle(3, 1, 1, 1000), [make_box(quantity=3)])
    assert [p.x for p in placed] == [0, 1, 2]
    assert not_placed == []


def test_pack_layers_new_row():
    placed, _ = pack_layers(Vehicle(3, 2, 1, 1000), [make_box(quantity=4)])
    last = placed[3]
    assert (last.x, last.y, last.z) == (0, 1, 0)


def test_pack_layers_new_layer():
    placed, _ = pack_layers(Vehicle(1, 1, 2, 1000), [make_box(quantity=2)])
    assert (placed[1].x, placed[1].y, placed[1].z) == (0, 0, 1)


def test_pack_layers_layer_uses_tallest_box():
    truck = Vehicle(2, 1, 3, 1000)
    placed, not_placed = pack_layers(
        truck, [make_box(1, 1, 2), make_box(1, 1, 1, quantity=2)]
    )
    assert not_placed == []
    assert placed[2].z == 2


def test_pack_layers_box_larger_than_vehicle():
    placed, not_placed = pack_layers(Vehicle(3, 2, 2, 1000), [make_box(4, 1, 1)])
    assert placed == []
    assert len(not_placed) == 1


def test_pack_layers_vehicle_full():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    placed, not_placed = pack_layers(truck, [Cargo(0.5, 0.4, 0.3, 1, quantity=150)])
    assert len(placed) == 144  # 6 × 4 × 6
    assert len(not_placed) == 6


def test_pack_layers_example_from_plan():
    truck = Vehicle(3.0, 1.9, 1.8, 1500)
    placed, not_placed = pack_layers(truck, [Cargo(0.5, 0.4, 0.3, 10, quantity=20)])
    assert len(placed) == 20
    assert not_placed == []


def test_pack_layers_biggest_first():
    truck = Vehicle(2, 1, 1, 1000)
    small = make_box(1, 1, 1, name="small")
    big = make_box(1.5, 1, 1, name="big")
    placed, _ = pack_layers(truck, [small, big])
    assert placed[0].cargo.name == "big"
    assert placed[0].x == 0


def test_pack_layers_keeps_all_items():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    cargos = [
        Cargo(0.5, 0.4, 0.3, 10, quantity=200),
        Cargo(1.2, 0.8, 1.5, 100, quantity=3),
        Cargo(4, 1, 1, 5),
    ]
    placed, not_placed = pack_layers(truck, cargos)
    assert len(placed) + len(not_placed) == 204


def test_pack_layers_respects_max_weight():
    truck = Vehicle(10, 10, 10, 5)
    placed, not_placed = pack_layers(truck, [make_box(weight=2, quantity=10)])
    assert len(placed) == 2
    assert len(not_placed) == 8


def test_pack_layers_float_sizes_touching_wall():
    truck = Vehicle(0.3, 1, 1, 1000)
    placed, _ = pack_layers(truck, [Cargo(0.1, 1, 1, 1, quantity=3)])
    assert len(placed) == 3


def test_pack_layers_invariant_no_overlaps_and_inside():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    cargos = [
        Cargo(0.5, 0.4, 0.3, 10, quantity=40),
        Cargo(1.2, 0.8, 1.5, 100, quantity=3),
        Cargo(0.7, 0.3, 0.9, 5, quantity=7),
    ]
    placed, _ = pack_layers(truck, cargos)

    assert len(placed) > 0
    for item in placed:
        assert inside(truck, item)
    for i, a in enumerate(placed):
        for b in placed[i + 1 :]:
            assert not overlaps(a, b)


# известный дефект послойной укладки


@pytest.mark.xfail(reason="послойная укладка не проверяет опору")
def test_pack_layers_leaves_no_floating_boxes():
    truck = Vehicle(2, 1, 4, 1000)
    cargos = [
        Cargo(1.5, 1, 1, 1, name="flat"),
        Cargo(0.5, 1, 2, 1, name="tall"),
        Cargo(0.9, 1, 1, 1, name="top"),
    ]
    placed, _ = pack_layers(truck, cargos)
    assert validate(truck, placed) == []


# orientations


def sizes(cargos):
    return {(c.length, c.width, c.height) for c in cargos}


def test_orientations_cube():
    assert len(orientations(make_box(1, 1, 1))) == 1


def test_orientations_regular_box():
    assert len(orientations(make_box(1, 2, 3))) == 6


def test_orientations_two_equal_sides():
    assert len(orientations(make_box(1, 1, 2))) == 3


def test_orientations_upright():
    result = orientations(make_box(1, 2, 3, upright=True))
    assert sizes(result) == {(1, 2, 3), (2, 1, 3)}


def test_orientations_upright_square_base():
    assert len(orientations(make_box(1, 1, 3, upright=True))) == 1


def test_orientations_keep_volume_and_fields():
    box = make_box(1, 2, 3, weight=7, name="A")
    for o in orientations(box):
        assert o.volume == pytest.approx(box.volume)
        assert o.weight == 7 and o.name == "A"


def test_orientations_do_not_change_original():
    box = make_box(1, 2, 3)
    orientations(box)
    assert (box.length, box.width, box.height) == (1, 2, 3)


# candidate_points


def test_candidate_points_empty():
    assert candidate_points([]) == [(0, 0, 0)]


def test_candidate_points_after_one_box():
    box = PlacedItem(make_box(1, 2, 3), 0, 0, 0)
    assert candidate_points([box]) == [(0, 0, 0), (1, 0, 0), (0, 2, 0), (0, 0, 3)]


# pack
def test_pack_empty():
    assert pack(Vehicle(3, 1, 1, 1000), []) == ([], [])


def test_pack_single_box_lies_flat_at_origin():
    placed, not_placed = pack(Vehicle(3, 2, 2, 1000), [make_box(2, 1, 0.5)])
    assert not_placed == []
    assert (placed[0].x, placed[0].y, placed[0].z) == (0, 0, 0)
    assert placed[0].cargo.height == 0.5  # лежит плашмя


def test_pack_two_boxes_in_row():
    truck = Vehicle(3, 1, 0.5, 1000)
    placed, not_placed = pack(truck, [make_box(1.5, 1, 0.5, quantity=2)])
    assert not_placed == []
    assert [p.x for p in placed] == [0, 1.5]


def test_pack_stacks_on_strong_box():
    truck = Vehicle(1, 2, 1, 1000)
    bottom = make_box(1, 2, 0.5, weight=10, max_load_above=10, name="bottom")
    top = make_box(1, 2, 0.5, weight=5, name="top")
    placed, not_placed = pack(truck, [bottom, top])
    assert not_placed == []
    assert placed[0].cargo.name == "bottom"
    assert placed[1].z == 0.5


def test_pack_does_not_stack_on_fragile_box():
    truck = Vehicle(1, 2, 1, 1000)
    bottom = make_box(1, 2, 0.5, weight=10, max_load_above=0)
    top = make_box(1, 2, 0.5, weight=5)
    placed, not_placed = pack(truck, [bottom, top])
    assert len(placed) == 1
    assert len(not_placed) == 1


def test_pack_rotates_box_to_fit():
    # коробка 2x1x1 влезает в кузов 1x2x1 только развёрнутой
    placed, not_placed = pack(Vehicle(1, 2, 1, 1000), [make_box(2, 1, 1)])
    assert not_placed == []
    assert (placed[0].cargo.length, placed[0].cargo.width) == (1, 2)


def test_pack_lies_down_when_not_upright():
    # коробка высотой 2 в кузове высотой 1: можно только положить на бок
    truck = Vehicle(3, 1, 1, 1000)
    placed, not_placed = pack(truck, [make_box(1, 1, 2)])
    assert not_placed == []
    assert placed[0].cargo.height == 1


def test_pack_upright_box_cannot_lie_down():
    truck = Vehicle(3, 1, 1, 1000)
    placed, not_placed = pack(truck, [make_box(1, 1, 2, upright=True)])
    assert placed == []
    assert len(not_placed) == 1


def test_pack_leaves_no_floating_boxes():
    truck = Vehicle(2, 1, 4, 1000)
    cargos = [
        Cargo(1.5, 1, 1, 1, name="flat", max_load_above=50),
        Cargo(0.5, 1, 2, 1, name="tall", max_load_above=50),
        Cargo(0.9, 1, 1, 1, name="top"),
    ]
    placed, not_placed = pack(truck, cargos)
    assert not_placed == []
    assert validate(truck, placed) == []


def test_pack_respects_max_weight():
    truck = Vehicle(10, 10, 10, 5)
    placed, not_placed = pack(truck, [make_box(1, 2, 3, weight=2, quantity=10)])
    assert len(placed) == 2
    assert len(not_placed) == 8


def test_pack_random_cargos_always_valid():
    random.seed(1)
    truck = Vehicle(3.0, 1.9, 1.8, 600)

    for _ in range(20):
        cargos = [
            Cargo(
                length=round(random.uniform(0.2, 1.2), 1),
                width=round(random.uniform(0.2, 1.0), 1),
                height=round(random.uniform(0.2, 1.0), 1),
                weight=random.randint(1, 40),
                quantity=random.randint(1, 6),
                max_load_above=random.choice([0, 30, 100]),
                stop=random.randint(1, 3),
            )
            for _ in range(10)
        ]
        placed, not_placed = pack(truck, cargos)

        assert validate(truck, placed) == []
        assert sum(p.cargo.weight for p in placed) <= truck.max_weight
        assert len(placed) + len(not_placed) == sum(c.quantity for c in cargos)


# порядок выгрузки
def test_pack_later_stop_goes_deeper():
    truck = Vehicle(2, 1, 0.5, 1000)
    first = make_box(1, 1, 0.5, name="first", stop=1)
    second = make_box(1, 1, 0.5, name="second", stop=2)
    placed, not_placed = pack(truck, [first, second])
    assert not_placed == []
    assert placed[0].cargo.name == "second" and placed[0].x == 0   # ближе к кабине
    assert placed[1].cargo.name == "first" and placed[1].x == 1    # ближе к дверям
    assert validate(truck, placed) == []


def test_pack_three_stops_in_row():
    truck = Vehicle(3, 1, 0.5, 1000)
    cargos = [make_box(1, 1, 0.5, stop=s) for s in (1, 3, 2)]
    placed, _ = pack(truck, cargos)
    assert [p.cargo.stop for p in placed] == [3, 2, 1]
    assert [p.x for p in placed] == [0, 1, 2]
