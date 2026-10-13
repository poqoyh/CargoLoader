from typing import List
from dataclasses import replace

from app.core.models import Cargo, Vehicle, PlacedItem


def expand(cargos: List[Cargo]) -> List[Cargo]:
    items = []

    for cargo in cargos:
        for _ in range(cargo.quantity):
            items.append(replace(cargo, quantity=1))

    return items


def pack(vehicle: Vehicle, cargos: List[Cargo]) -> tuple[list[PlacedItem], list[Cargo]]:

    items = sorted(expand(cargos), key=lambda c: c.volume, reverse=True)

    placed = []
    not_placed = []

    x = 0
    y = 0
    z = 0

    row_width = 0
    row_height = 0

    for item in items:
        if (
            item.width > vehicle.width
            or item.height > vehicle.height
            or item.length > vehicle.length
        ):
            not_placed.append(item)
            continue

        if x + item.length > vehicle.length:
            x = 0
            y = y + row_width
            row_width = 0

        if y + item.width > vehicle.width:
            x = 0
            y = 0
            z = z + row_height

            row_width = 0
            row_height = 0

        if z + item.height > vehicle.height:
            not_placed.append(item)
            continue

        placed.append(PlacedItem(item, x, y, z))

        x = x + item.length

        row_width = max(row_width, item.width)
        row_height = max(row_height, item.height)

    return placed, not_placed
