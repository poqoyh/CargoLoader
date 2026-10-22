from typing import List
from dataclasses import replace
from itertools import permutations

from app.core.checks import EPS, can_place

from app.core.models import Cargo, Vehicle, PlacedItem


def expand(cargos: List[Cargo]) -> List[Cargo]:
    items = []

    for cargo in cargos:
        for _ in range(cargo.quantity):
            items.append(replace(cargo, quantity=1))

    return items


def orientations(cargo: Cargo) -> List[Cargo]:
    """
    Все допустимые повороты груза (без повторов)
    """
    if cargo.upright:
        sizes = {
            (cargo.length, cargo.width, cargo.height),
            (cargo.width, cargo.length, cargo.height),
        }
    else:
        sizes = set(permutations((cargo.length, cargo.width, cargo.height)))

    return [replace(cargo, length=l, width=w, height=h) for l, w, h in sorted(sizes)]


def pack_layers(
    vehicle: Vehicle, cargos: List[Cargo]
) -> tuple[list[PlacedItem], list[Cargo]]:

    items = sorted(expand(cargos), key=lambda c: c.volume, reverse=True)

    placed = []
    not_placed = []

    x = 0
    y = 0
    z = 0

    row_width = 0
    layer_height = 0
    total_weight = 0

    for item in items:
        if (
            item.width > vehicle.width + EPS
            or item.height > vehicle.height + EPS
            or item.length > vehicle.length + EPS
            or total_weight + item.weight > vehicle.max_weight + EPS
        ):
            not_placed.append(item)
            continue

        if x + item.length > vehicle.length + EPS:
            x = 0
            y = y + row_width
            row_width = 0

        if y + item.width > vehicle.width + EPS:
            x = 0
            y = 0
            z = z + layer_height

            row_width = 0
            layer_height = 0

        if z + item.height > vehicle.height + EPS:
            not_placed.append(item)
            continue

        placed.append(PlacedItem(item, x, y, z))
        total_weight += item.weight

        x = x + item.length

        row_width = max(row_width, item.width)
        layer_height = max(layer_height, item.height)

    return placed, not_placed


def candidate_points(placed: List[PlacedItem]) -> list[tuple]:
    """
    Точки, где можно попробовать поставить следующую коробку.
    """

    points = {(0, 0, 0)}

    for p in placed:
        points.add((p.x + p.cargo.length, p.y, p.z))  # справа
        points.add((p.x, p.y + p.cargo.width, p.z))  # спереди
        points.add((p.x, p.y, p.z + p.cargo.height))  # сверху

    return sorted(points, key=lambda pt: (pt[2], pt[1], pt[0]))


def pack(vehicle: Vehicle, cargos: List[Cargo]) -> tuple[list[PlacedItem], list[Cargo]]:
    # сначала грузы с поздней выгрузкой (они лягут глубже), внутри - крупные вперёд
    items = sorted(expand(cargos), key=lambda c: (-c.stop, -c.volume))

    placed = []
    not_placed = []
    total_weight = 0

    for item in items:
        best = None
        points = candidate_points(placed)

        variants = sorted(orientations(item), key=lambda o: (o.height, -o.length))

        for oriented in variants:
            for x, y, z in points:
                key = (z, y, x)
                if best is not None and key >= best[0]:
                    break

                candidate = PlacedItem(oriented, x, y, z)
                if can_place(vehicle, candidate, placed, total_weight):
                    best = (key, candidate)
                    break

        if best is None:
            not_placed.append(item)
        else:
            placed.append(best[1])
            total_weight += item.weight

    return placed, not_placed
