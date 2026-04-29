from dataclasses import dataclass


@dataclass
class BBox:
    x1: int
    y1: int
    x2: int
    y2: int

    def center(self):
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


@dataclass
class Detection:
    cls: str
    conf: float
    bbox: BBox
