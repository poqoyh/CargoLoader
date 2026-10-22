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
    upright: bool = False
    stop: int = 1  # номер точки выгрузки

    def __post_init__(self):
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Cargo dimensions must be positive.")
        if self.weight <= 0:
            raise ValueError("Cargo weight must be positive.")
        if self.quantity < 1:
            raise ValueError("Cargo quantity must be at least 1.")
        if self.max_load_above < 0:
            raise ValueError("Cargo max load above must be non-negative.")
        if self.stop < 1:
            raise ValueError("Cargo stop must be at least 1.")

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
    front_axle_x: float | None = None  # положение передней оси вдоль кузова, м
    rear_axle_x: float | None = None  # положение задней оси вдоль кузова, м
    max_front_axle_load: float | None = None  # kg
    max_rear_axle_load: float | None = None  # kg

    def __post_init__(self):
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Vehicle dimensions must be positive.")
        if self.max_weight <= 0:
            raise ValueError("Vehicle weight must be positive.")
        if (
            self.front_axle_x is not None
            and self.rear_axle_x is not None
            and self.rear_axle_x <= self.front_axle_x
        ):
            raise ValueError("Rear axle must be behind the front axle.")

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


@dataclass
class PackResult:
    placed: list[PlacedItem]
    not_placed: list[Cargo]
    volume_percent: float  # по размещённым грузам
    weight_percent: float  # по размещённым грузам
    center_of_mass: tuple[float, float, float]
    axle_loads: tuple[float, float] | None  # (передняя, задняя) или None
    problems: list[str]  # нарушения: пусто = раскладка корректна
    warnings: list[str]  # замечания, не делающие раскладку невозможной
