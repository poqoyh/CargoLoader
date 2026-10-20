from typing import List
from dataclasses import replace
from itertools import permutations

from app.core.checks import EPS

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


def pack(vehicle: Vehicle, cargos: List[Cargo]) -> tuple[list[PlacedItem], list[Cargo]]:

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
