from app.core.models import Cargo, Vehicle
from app.core.checks import inside, overlaps
from app.core.packing import expand, pack


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


def test_pack_empty():
    assert pack(Vehicle(3, 1, 1, 1000), []) == ([], [])


def test_pack_single_box_at_origin():
    placed, not_placed = pack(Vehicle(3, 2, 2, 1000), [make_box()])
    assert not_placed == []
    assert (placed[0].x, placed[0].y, placed[0].z) == (0, 0, 0)


def test_pack_row_along_x():
    placed, not_placed = pack(Vehicle(3, 1, 1, 1000), [make_box(quantity=3)])
    assert [p.x for p in placed] == [0, 1, 2]
    assert not_placed == []


def test_pack_new_row():
    placed, _ = pack(Vehicle(3, 2, 1, 1000), [make_box(quantity=4)])
    last = placed[3]
    assert (last.x, last.y, last.z) == (0, 1, 0)


def test_pack_new_layer():
    placed, _ = pack(Vehicle(1, 1, 2, 1000), [make_box(quantity=2)])
    assert (placed[1].x, placed[1].y, placed[1].z) == (0, 0, 1)


def test_pack_layer_uses_tallest_box():
    truck = Vehicle(2, 1, 3, 1000)
    placed, not_placed = pack(truck, [make_box(1, 1, 2), make_box(1, 1, 1, quantity=2)])
    assert not_placed == []
    assert placed[2].z == 2


def test_pack_box_larger_than_vehicle():
    placed, not_placed = pack(Vehicle(3, 2, 2, 1000), [make_box(4, 1, 1)])
    assert placed == []
    assert len(not_placed) == 1


def test_pack_vehicle_full():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    placed, not_placed = pack(truck, [Cargo(0.5, 0.4, 0.3, 1, quantity=150)])
    assert len(placed) == 144  # 6 × 4 × 6
    assert len(not_placed) == 6


def test_pack_example_from_plan():
    truck = Vehicle(3.0, 1.9, 1.8, 1500)
    placed, not_placed = pack(truck, [Cargo(0.5, 0.4, 0.3, 10, quantity=20)])
    assert len(placed) == 20
    assert not_placed == []


def test_pack_biggest_first():
    truck = Vehicle(2, 1, 1, 1000)
    small = make_box(1, 1, 1, name="small")
    big = make_box(1.5, 1, 1, name="big")
    placed, _ = pack(truck, [small, big])
    assert placed[0].cargo.name == "big"
    assert placed[0].x == 0


def test_pack_keeps_all_items():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    cargos = [
        Cargo(0.5, 0.4, 0.3, 10, quantity=200),
        Cargo(1.2, 0.8, 1.5, 100, quantity=3),
        Cargo(4, 1, 1, 5),
    ]
    placed, not_placed = pack(truck, cargos)
    assert len(placed) + len(not_placed) == 204


def test_pack_respects_max_weight():
    truck = Vehicle(10, 10, 10, 5)
    placed, not_placed = pack(truck, [make_box(weight=2, quantity=10)])
    assert len(placed) == 2
    assert len(not_placed) == 8


def test_pack_float_sizes_touching_wall():
    truck = Vehicle(0.3, 1, 1, 1000)
    placed, _ = pack(truck, [Cargo(0.1, 1, 1, 1, quantity=3)])
    assert len(placed) == 3


def test_pack_invariant_no_overlaps_and_inside():
    truck = Vehicle(3.0, 1.9, 1.8, 100000)
    cargos = [
        Cargo(0.5, 0.4, 0.3, 10, quantity=40),
        Cargo(1.2, 0.8, 1.5, 100, quantity=3),
        Cargo(0.7, 0.3, 0.9, 5, quantity=7),
    ]
    placed, _ = pack(truck, cargos)

    assert len(placed) > 0
    for item in placed:
        assert inside(truck, item)
    for i, a in enumerate(placed):
        for b in placed[i + 1 :]:
            assert not overlaps(a, b)
