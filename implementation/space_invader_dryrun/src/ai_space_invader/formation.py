from __future__ import annotations

from dataclasses import dataclass
from random import Random

from ai_space_invader.alien import Alien
from ai_space_invader.projectile import Projectile
from ai_space_invader.projectile import rects_overlap


@dataclass
class AlienFormation:
    aliens: list[Alien]
    total_aliens: int
    direction: int
    last_step_s: float
    base_interval_s: float
    min_interval_s: float
    step_px: int
    step_down_px: int

    @classmethod
    def from_config(
        cls,
        formation_config: dict,
        *,
        interval_multiplier: float,
        now_s: float,
    ) -> 'AlienFormation':
        fleet = formation_config['fleet']
        rows = int(fleet['rows'])
        cols = int(fleet['cols'])
        start_x = float(fleet['start_x_px'])
        start_y = float(fleet['start_y_px'])
        alien_width = int(fleet['alien_width_px'])
        alien_height = int(fleet['alien_height_px'])
        h_spacing = int(fleet['h_spacing_px'])
        v_spacing = int(fleet['v_spacing_px'])
        row_types = list(fleet['row_types'])
        aliens: list[Alien] = []
        for row in range(rows):
            row_cfg = row_types[row]
            for col in range(cols):
                x = start_x + col * (alien_width + h_spacing)
                y = start_y + row * (alien_height + v_spacing)
                aliens.append(
                    Alien(
                        row=row,
                        col=col,
                        kind=str(row_cfg['kind']),
                        score=int(row_cfg['score']),
                        x=x,
                        y=y,
                        width=alien_width,
                        height=alien_height,
                    )
                )
        return cls(
            aliens=aliens,
            total_aliens=len(aliens),
            direction=1,
            last_step_s=now_s,
            base_interval_s=float(fleet['base_interval_s']) * interval_multiplier,
            min_interval_s=float(fleet['min_interval_s']) * min(1.0, interval_multiplier),
            step_px=int(fleet['step_px']),
            step_down_px=int(fleet['step_down_px']),
        )

    def alive_aliens(self) -> list[Alien]:
        return [alien for alien in self.aliens if alien.alive]

    def alive_count(self) -> int:
        return len(self.alive_aliens())

    def current_interval_s(self) -> float:
        if self.total_aliens <= 1:
            return self.min_interval_s
        alive = self.alive_count()
        ratio = max(0.0, float(alive - 1) / float(self.total_aliens - 1))
        return self.min_interval_s + (self.base_interval_s - self.min_interval_s) * ratio

    def bounds(self) -> tuple[float, float, float, float]:
        alive = self.alive_aliens()
        if not alive:
            return (0.0, 0.0, 0.0, 0.0)
        left = min(alien.x for alien in alive)
        right = max(alien.x + alien.width for alien in alive)
        top = min(alien.y for alien in alive)
        bottom = max(alien.y + alien.height for alien in alive)
        return (left, top, right, bottom)

    def update(self, now_s: float, *, arena_left_px: float, arena_right_px: float) -> bool:
        if now_s - self.last_step_s < self.current_interval_s():
            return False
        self.last_step_s = now_s
        left, _, right, _ = self.bounds()
        step_x = self.step_px * self.direction
        next_left = left + step_x
        next_right = right + step_x
        descended = False
        if next_left < arena_left_px or next_right > arena_right_px:
            self.direction *= -1
            for alien in self.alive_aliens():
                alien.shift(0.0, float(self.step_down_px))
                alien.toggle_frame()
            descended = True
        else:
            for alien in self.alive_aliens():
                alien.shift(float(step_x), 0.0)
                alien.toggle_frame()
        return descended

    def choose_shooter(self, rng: Random) -> Alien | None:
        columns: dict[int, Alien] = {}
        for alien in self.alive_aliens():
            prev = columns.get(alien.col)
            if prev is None or alien.y > prev.y:
                columns[alien.col] = alien
        if not columns:
            return None
        return columns[rng.choice(sorted(columns.keys()))]

    def hit(self, projectile: Projectile) -> Alien | None:
        for alien in self.alive_aliens():
            if rects_overlap(alien.bounds(), projectile.bounds()):
                alien.alive = False
                return alien
        return None

    def invasion_reached(self, invade_line_y: float) -> bool:
        _, _, _, bottom = self.bounds()
        return bottom >= invade_line_y
