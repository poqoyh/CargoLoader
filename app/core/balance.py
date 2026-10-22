from app.core.models import Vehicle, PlacedItem

MAX_OFFSET_RATIO = 0.1  # допустимый боковой перекос: доля ширины кузова


def center_of_mass(placed: list[PlacedItem]) -> tuple[float, float, float]:
    """Центр тяжести груза (x, y, z). Для пустой раскладки (0, 0, 0)."""
    total_weight = sum(p.cargo.weight for p in placed)
    if total_weight == 0:
        return (0.0, 0.0, 0.0)

    cx = sum(p.cargo.weight * (p.x + p.cargo.length / 2) for p in placed)
    cy = sum(p.cargo.weight * (p.y + p.cargo.width / 2) for p in placed)
    cz = sum(p.cargo.weight * (p.z + p.cargo.height / 2) for p in placed)
    return (cx / total_weight, cy / total_weight, cz / total_weight)


def axle_loads(
    vehicle: Vehicle, placed: list[PlacedItem]
) -> tuple[float, float] | None:
    """Нагрузка груза на (переднюю, заднюю) ось по правилу рычага.
    None, если положение осей не задано."""
    if vehicle.front_axle_x is None or vehicle.rear_axle_x is None:
        return None

    total_weight = sum(p.cargo.weight for p in placed)
    if total_weight == 0:
        return (0.0, 0.0)

    cx, _, _ = center_of_mass(placed)
    span = vehicle.rear_axle_x - vehicle.front_axle_x
    rear = total_weight * (cx - vehicle.front_axle_x) / span
    front = total_weight - rear
    return (front, rear)


def balance_warnings(vehicle: Vehicle, placed: list[PlacedItem]) -> list[str]:
    """Замечания по балансу (не ошибки раскладки)."""
    if not placed:
        return []

    _, cy, _ = center_of_mass(placed)
    offset = abs(cy - vehicle.width / 2)
    if offset > vehicle.width * MAX_OFFSET_RATIO:
        return [f"load is off-center by {offset:.2f} m"]
    return []
