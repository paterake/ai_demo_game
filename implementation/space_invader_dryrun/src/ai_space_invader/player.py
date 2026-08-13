from __future__ import annotations

from dataclasses import dataclass

from ai_space_invader.projectile import Projectile
from ai_space_invader.projectile import Rect


@dataclass
class Player:
    x: float
    y: float
    width: int
    height: int
    speed_px_per_s: float
    shot_cooldown_s: float
    baseline_x: float
    last_shot_s: float = -999.0

    def move(self, direction: int, dt_s: float, *, min_x: float, max_x: float) -> None:
        self.x += float(direction) * self.speed_px_per_s * dt_s
        self.x = max(min_x, min(self.x, max_x - self.width))

    def bounds(self) -> Rect:
        return (self.x, self.y, float(self.width), float(self.height))

    def can_fire(self, *, now_s: float, active_player_shot: bool) -> bool:
        return (not active_player_shot) and (now_s - self.last_shot_s >= self.shot_cooldown_s)

    def fire(
        self,
        *,
        now_s: float,
        projectile_width: int,
        projectile_height: int,
        projectile_speed_px_per_s: float,
    ) -> Projectile | None:
        if not self.can_fire(now_s=now_s, active_player_shot=False):
            return None
        self.last_shot_s = now_s
        projectile_x = self.x + (self.width - projectile_width) / 2.0
        projectile_y = self.y - projectile_height
        return Projectile(
            x=projectile_x,
            y=projectile_y,
            width=projectile_width,
            height=projectile_height,
            velocity_px_per_s=projectile_speed_px_per_s,
            owner='player',
        )

    def reset_position(self) -> None:
        self.x = self.baseline_x
