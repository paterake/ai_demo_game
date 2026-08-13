from __future__ import annotations

from dataclasses import dataclass

from ai_space_invader.projectile import Projectile
from ai_space_invader.projectile import Rect
from ai_space_invader.projectile import rects_overlap


@dataclass
class UFO:
    width: int
    height: int
    speed_px_per_s: float
    spawn_interval_s: float
    respawn_delay_s: float
    y_px: int
    score_cycle: list[int]
    active: bool = False
    x: float = 0.0
    direction: int = 1
    next_spawn_s: float = 0.0

    def bounds(self) -> Rect:
        return (self.x, float(self.y_px), float(self.width), float(self.height))

    def current_score(self, shots_fired: int) -> int:
        if not self.score_cycle:
            return 100
        index = 0 if shots_fired <= 0 else (shots_fired - 1) % len(self.score_cycle)
        return int(self.score_cycle[index])

    def update(self, dt_s: float, now_s: float, *, arena_left_px: float, arena_right_px: float) -> None:
        if self.active:
            self.x += self.direction * self.speed_px_per_s * dt_s
            if self.direction > 0 and self.x > arena_right_px + self.width:
                self.active = False
                self.next_spawn_s = now_s + self.spawn_interval_s
            elif self.direction < 0 and self.x + self.width < arena_left_px - self.width:
                self.active = False
                self.next_spawn_s = now_s + self.spawn_interval_s
            return
        if now_s < self.next_spawn_s:
            return
        self.active = True
        self.direction = 1 if int(now_s) % 2 == 0 else -1
        self.x = arena_left_px - self.width if self.direction > 0 else arena_right_px

    def try_hit(self, projectile: Projectile, *, shots_fired: int, now_s: float) -> int | None:
        if not self.active:
            return None
        if not rects_overlap(self.bounds(), projectile.bounds()):
            return None
        self.active = False
        self.next_spawn_s = now_s + self.respawn_delay_s
        return self.current_score(shots_fired)
