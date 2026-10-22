from app.core.balance import axle_loads, balance_warnings, center_of_mass
from app.core.checks import validate
from app.core.models import Cargo, PackResult, Vehicle
from app.core.packing import pack


def pack_cargo(vehicle: Vehicle, cargos: list[Cargo]) -> PackResult:
    """
    Единая точка входа для API
    """
    placed, not_placed = pack(vehicle, cargos)

    placed_volume = sum(p.cargo.volume for p in placed)
    placed_weight = sum(p.cargo.weight for p in placed)

    return PackResult(
        placed=placed,
        not_placed=not_placed,
        volume_percent=placed_volume / vehicle.volume * 100,
        weight_percent=placed_weight / vehicle.max_weight * 100,
        center_of_mass=center_of_mass(placed),
        axle_loads=axle_loads(vehicle, placed),
        problems=validate(vehicle, placed),
        warnings=balance_warnings(vehicle, placed),
    )
