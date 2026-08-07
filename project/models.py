from dataclasses import dataclass


@dataclass
class ColorDefinition:
    name: str
    rgb: tuple[int, int, int]
    tolerance: int = 20
    enabled: bool = True