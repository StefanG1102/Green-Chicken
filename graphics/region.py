from dataclasses import dataclass, field
from typing import List, Tuple


Point = Tuple[float, float]


@dataclass
class Region:
    region_id: int
    points: List[Point] = field(default_factory=list)
    dead_zones: List[List[Point]] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"Bereich {self.region_id}"