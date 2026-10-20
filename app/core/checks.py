from typing import List

from app.core.models import Cargo, Vehicle, PlacedItem, LoadResult

EPS = 1e-9
MIN_SUPPORT_AREA = 0.7  # Минимум площади основания, которая должна на что-то опираться


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
        and item.x + item.cargo.length <= vehicle.length + EPS
        and item.y >= 0
        and item.y + item.cargo.width <= vehicle.width + EPS
        and item.z >= 0
        and item.z + item.cargo.height <= vehicle.height + EPS
    )


def segments_overlap(
    a_start: float | int,
    a_end: float | int,
    b_start: float | int,
    b_end: float | int,
) -> bool:
    return a_start < b_end - EPS and b_start < a_end - EPS


def overlaps(a: PlacedItem, b: PlacedItem) -> bool:
    overlap_x = segments_overlap(a.x, a.x + a.cargo.length, b.x, b.x + b.cargo.length)
    overlap_y = segments_overlap(a.y, a.y + a.cargo.width, b.y, b.y + b.cargo.width)
    overlap_z = segments_overlap(a.z, a.z + a.cargo.height, b.z, b.z + b.cargo.height)
    return overlap_x and overlap_y and overlap_z


def contact_area(a: PlacedItem, b: PlacedItem) -> float:
    """
    Площадь общей части двух коробок при взгляде сверху
    """

    total_length = min(a.x + a.cargo.length, b.x + b.cargo.length) - max(a.x, b.x)

    total_width = min(a.y + a.cargo.width, b.y + b.cargo.width) - max(a.y, b.y)

    if total_length <= 0 or total_width <= 0:
        return 0

    return total_length * total_width


def is_supported(item: PlacedItem, placed: list[PlacedItem]) -> bool:
    """
    Коробка стоит на полу или достаточной площадью опирается на другие
    """
    if item.z <= EPS:
        return True

    base_area = item.cargo.length * item.cargo.height
    supported_area = 0

    for other in placed:
        if other is item:
            continue
        other_top = other.z + other.cargo.height
        if abs(other_top - item.z) <= EPS:
            supported_area += contact_area(item, other)

    return supported_area >= base_area * MIN_SUPPORT_AREA - EPS


def load_on(item: PlacedItem, placed: list[PlacedItem]) -> float:
    """
    Вес коробок, стоящих прямо на этой коробке
    """

    item_top = item.z + item.cargo.height
    total = 0

    for other in placed:
        if other is item:
            continue
        if abs(other.z - item_top) <= EPS and contact_area(item, other) > EPS:
            total += other.cargo.weight

    return total


def is_overloaded(item: PlacedItem, placed: list[PlacedItem]) -> bool:
    return load_on(item, placed) > item.cargo.max_load_above + EPS


def validate(vehicle: Vehicle, placed: list[PlacedItem]) -> list[str]:
    """
    Список проблем раскладки
    Если пустой то всё в порядке
    """
    problems = []

    for i, item in enumerate(placed):
        if not inside(vehicle, item):
            problems.append(f"item {i} is outside")
        if not is_supported(item, placed):
            problems.append(f"item {i} is not supported")
        if is_overloaded(item, placed):
            problems.append(f"item {i} is overloaded")

    for i, a in enumerate(placed):
        for j in range(i + 1, len(placed)):
            if overlaps(a, placed[j]):
                problems.append(f"items {i} and {j} overlap")

    return problems
