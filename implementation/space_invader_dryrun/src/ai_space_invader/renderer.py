from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from ai_space_invader.alien import Alien
from ai_space_invader.bunker import Bunker
from ai_space_invader.formation import AlienFormation
from ai_space_invader.player import Player
from ai_space_invader.projectile import Projectile
from ai_space_invader.ufo import UFO


@dataclass
class Renderer:
    screen: pygame.Surface
    colours: dict
    stars_config: dict
    hud_height_px: int
    arena_top_px: int

    def __post_init__(self) -> None:
        width, height = self.screen.get_size()
        rng = random.Random(int(self.stars_config.get('seed', 0)))
        count = int(self.stars_config.get('count', 0))
        self.star_positions = [
            (rng.randint(0, width - 1), rng.randint(self.arena_top_px, height - 1))
            for _ in range(max(0, count))
        ]

    def draw_world(
        self,
        *,
        player: Player,
        formation: AlienFormation,
        bunkers: list[Bunker],
        player_shot: Projectile | None,
        enemy_shots: list[Projectile],
        ufo: UFO,
        invade_line_y: int,
    ) -> None:
        self.screen.fill(_hex_to_rgb(self.colours['background']))
        self._draw_stars()
        self._draw_invade_line(invade_line_y)
        self._draw_bunkers(bunkers)
        self._draw_player(player)
        self._draw_formation(formation)
        self._draw_projectiles(player_shot, enemy_shots)
        self._draw_ufo(ufo)

    def _draw_stars(self) -> None:
        colour = _hex_to_rgb(self.colours['star'])
        for x, y in self.star_positions:
            self.screen.set_at((x, y), colour)

    def _draw_invade_line(self, y: int) -> None:
        colour = _hex_to_rgb(self.colours['invade_line'])
        pygame.draw.line(self.screen, colour, (20, y), (self.screen.get_width() - 20, y), 1)

    def _draw_player(self, player: Player) -> None:
        hull = _hex_to_rgb(self.colours['player'])
        cockpit = _hex_to_rgb(self.colours['player_cockpit'])
        x = int(player.x)
        y = int(player.y)
        w = player.width
        h = player.height
        pygame.draw.rect(self.screen, hull, pygame.Rect(x, y + h // 3, w, h // 2))
        pygame.draw.polygon(
            self.screen,
            hull,
            [(x + w // 2, y), (x + w, y + h // 2), (x, y + h // 2)],
        )
        pygame.draw.rect(self.screen, cockpit, pygame.Rect(x + w // 2 - 3, y + h // 4, 6, h // 3))

    def _draw_formation(self, formation: AlienFormation) -> None:
        for alien in formation.alive_aliens():
            self._draw_alien(alien)

    def _draw_alien(self, alien: Alien) -> None:
        colour = _alien_colour(self.colours, alien.kind)
        x = int(alien.x)
        y = int(alien.y)
        w = alien.width
        h = alien.height
        if alien.kind == 'squid':
            pygame.draw.ellipse(self.screen, colour, pygame.Rect(x + 4, y, w - 8, h - 6))
            pygame.draw.rect(self.screen, colour, pygame.Rect(x + 6, y + h // 2, w - 12, 5))
            offset = 1 if alien.frame else 0
            pygame.draw.line(self.screen, colour, (x + 8, y + h - 2), (x + 10, y + h - 7 + offset), 2)
            pygame.draw.line(self.screen, colour, (x + w - 8, y + h - 2), (x + w - 10, y + h - 7 + offset), 2)
        elif alien.kind == 'crab':
            pygame.draw.rect(self.screen, colour, pygame.Rect(x + 5, y + 4, w - 10, h - 10))
            claw_y = y + (2 if alien.frame else 5)
            pygame.draw.line(self.screen, colour, (x + 3, claw_y), (x + 9, y + 8), 3)
            pygame.draw.line(self.screen, colour, (x + w - 3, claw_y), (x + w - 9, y + 8), 3)
            pygame.draw.line(self.screen, colour, (x + 10, y + h - 2), (x + 8, y + h - 7), 2)
            pygame.draw.line(self.screen, colour, (x + w - 10, y + h - 2), (x + w - 8, y + h - 7), 2)
        else:
            pygame.draw.rect(self.screen, colour, pygame.Rect(x + 4, y + 2, w - 8, h - 8), border_radius=4)
            wobble = 2 if alien.frame else 0
            for leg in range(4):
                lx = x + 6 + leg * 6
                pygame.draw.line(self.screen, colour, (lx, y + h - 2), (lx + wobble, y + h - 8), 2)
        eye_y = y + h // 3
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(x + w // 3 - 2, eye_y, 4, 3))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(x + (2 * w) // 3 - 2, eye_y, 4, 3))

    def _draw_bunkers(self, bunkers: list[Bunker]) -> None:
        colour = _hex_to_rgb(self.colours['bunker'])
        for bunker in bunkers:
            for x, y, w, h in bunker.block_rects():
                pygame.draw.rect(self.screen, colour, pygame.Rect(x, y, w, h))

    def _draw_projectiles(self, player_shot: Projectile | None, enemy_shots: list[Projectile]) -> None:
        if player_shot is not None:
            self._draw_projectile(player_shot, self.colours['projectile_player'])
        for shot in enemy_shots:
            self._draw_projectile(shot, self.colours['projectile_enemy'])

    def _draw_projectile(self, projectile: Projectile, colour_hex: str) -> None:
        colour = _hex_to_rgb(colour_hex)
        pygame.draw.rect(
            self.screen,
            colour,
            pygame.Rect(int(projectile.x), int(projectile.y), projectile.width, projectile.height),
        )

    def _draw_ufo(self, ufo: UFO) -> None:
        if not ufo.active:
            return
        colour = _hex_to_rgb(self.colours['ufo'])
        x = int(ufo.x)
        y = int(ufo.y_px)
        w = ufo.width
        h = ufo.height
        pygame.draw.ellipse(self.screen, colour, pygame.Rect(x, y + h // 4, w, h // 2))
        pygame.draw.ellipse(self.screen, colour, pygame.Rect(x + w // 4, y, w // 2, h // 2))
        pygame.draw.circle(self.screen, (255, 255, 255), (x + w // 2, y + h // 2), 2)


def _alien_colour(colours: dict, kind: str) -> tuple[int, int, int]:
    if kind == 'squid':
        return _hex_to_rgb(colours['invader_top'])
    if kind == 'crab':
        return _hex_to_rgb(colours['invader_mid'])
    return _hex_to_rgb(colours['invader_bottom'])


def _hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    if not isinstance(hex_colour, str) or not hex_colour.startswith('#') or len(hex_colour) != 7:
        raise ValueError(f'Invalid colour hex: {hex_colour!r}')
    return (int(hex_colour[1:3], 16), int(hex_colour[3:5], 16), int(hex_colour[5:7], 16))
