from dataclasses import dataclass


@dataclass
class Cargo:
    length: float | int  # meters
    width: float | int  # meters
    height: float | int  # meters
    weight: float | int  # kg
    name: str = ""
    max_load_above: float | int = 0.0  # kg
    quantity: int = 1

    def __post_init__(self):
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Cargo dimensions must be positive.")
        if self.weight <= 0:
            raise ValueError("Cargo weight must be positive.")

    @property
    def volume(self) -> float:
        """m^3"""
        return self.length * self.width * self.height


@dataclass
class Vehicle:
    length: float | int  # meters
    width: float | int  # meters
    height: float | int  # meters
    max_weight: float | int  # kg

    def __post_init__(self):
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Vehicle dimensions must be positive.")
        if self.max_weight <= 0:
            raise ValueError("Vehicle weight must be positive.")

    @property
    def volume(self) -> float:
        """m^3"""
        return self.length * self.width * self.height


@dataclass(frozen=True)
class PlacedItem:
    cargo: Cargo
    x: float | int
    y: float | int
    z: float | int

    def __post_init__(self):
        if self.x < 0 or self.y < 0 or self.z < 0:
            raise ValueError("Coordinates must be non-negative.")


@dataclass
class LoadResult:
    fits: bool
    volume_percent: float
    weight_percent: float
