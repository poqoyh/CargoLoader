from typing import List

from app.core.models import Cargo, Vehicle, PlacedItem, LoadResult


def check_load(vehicle: Vehicle, cargos: List[Cargo]) -> LoadResult:
    total_volume = sum(cargo.volume * cargo.quantity for cargo in cargos)
    total_weight = sum(cargo.weight * cargo.quantity for cargo in cargos)

    volume_percent = (total_volume / vehicle.volume) * 100
    weight_percent = (total_weight / vehicle.max_weight) * 100

    fits = volume_percent <= 100 and weight_percent <= 100

    return LoadResult(
        fits,
        volume_percent,
        weight_percent,
    )


def inside(vehicle: Vehicle, item: PlacedItem) -> bool:
    return (
        item.x >= 0
        and item.x + item.cargo.length <= vehicle.length
        and item.y >= 0
        and item.y + item.cargo.width <= vehicle.width
        and item.z >= 0
        and item.z + item.cargo.height <= vehicle.height
    )


def segments_overlap(
    a_start: float | int,
    a_end: float | int,
    b_start: float | int,
    b_end: float | int,
) -> bool:
    return a_start < b_end and b_start < a_end


def overlaps(a: PlacedItem, b: PlacedItem) -> bool:
    overlap_x = segments_overlap(a.x, a.x + a.cargo.length, b.x, b.x + b.cargo.length)
    overlap_y = segments_overlap(a.y, a.y + a.cargo.width, b.y, b.y + b.cargo.width)
    overlap_z = segments_overlap(a.z, a.z + a.cargo.height, b.z, b.z + b.cargo.height)
    return overlap_x and overlap_y and overlap_z
