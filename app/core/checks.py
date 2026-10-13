from dataclasses import dataclass
from typing import List

from app.core.models import Cargo, Vehicle


@dataclass
class LoadResult:
    fits: bool
    volume_percent: float
    weight_percent: float


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
