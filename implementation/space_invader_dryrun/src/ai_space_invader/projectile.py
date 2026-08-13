from __future__ import annotations

from dataclasses import dataclass


Rect = tuple[float, float, float, float]


def rects_overlap(a: Rect, b: Rect) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


@dataclass
class Projectile:
    x: float
    y: float
    width: int
    height: int
    velocity_px_per_s: float
    owner: str

    def update(self, dt_s: float) -> None:
        self.y += self.velocity_px_per_s * dt_s

    def bounds(self) -> Rect:
        return (self.x, self.y, float(self.width), float(self.height))

    def tip(self) -> tuple[float, float]:
        cx = self.x + self.width / 2.0
        if self.velocity_px_per_s < 0:
            return (cx, self.y)
        return (cx, self.y + self.height)

    def offscreen(self, *, min_y: float, max_y: float) -> bool:
        return self.y + self.height < min_y or self.y > max_y
