from __future__ import annotations

from dataclasses import dataclass

from ai_space_invader.projectile import Rect


@dataclass
class Alien:
    row: int
    col: int
    kind: str
    score: int
    x: float
    y: float
    width: int
    height: int
    frame: int = 0
    alive: bool = True

    def bounds(self) -> Rect:
        return (self.x, self.y, float(self.width), float(self.height))

    def shift(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def toggle_frame(self) -> None:
        self.frame = 1 - self.frame
