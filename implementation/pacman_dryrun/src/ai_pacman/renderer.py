from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from ai_pacman.ghost import Ghost
from ai_pacman.maze import Maze
from ai_pacman.pacman import PacMan


@dataclass
class Renderer:
    screen: pygame.Surface
    window_width_px: int
    window_height_px: int
    hud_height_px: int
    colours: dict
    sizes: dict
    animation: dict

    def __post_init__(self) -> None:
        play_height_px = self.window_height_px - self.hud_height_px
        self.tile_size_px = int(min(self.window_width_px / 1, play_height_px / 1))
        self.origin_x_px = 0
        self.origin_y_px = self.hud_height_px

    def configure_for_maze(self, maze: Maze) -> None:
        play_height_px = self.window_height_px - self.hud_height_px
        tile = int(min(self.window_width_px / maze.cols, play_height_px / maze.rows))
        self.tile_size_px = max(tile, 1)
        maze_width_px = self.tile_size_px * maze.cols
        maze_height_px = self.tile_size_px * maze.rows
        self.origin_x_px = (self.window_width_px - maze_width_px) // 2
        self.origin_y_px = self.hud_height_px + (play_height_px - maze_height_px) // 2

    def maze_rect(self, maze: Maze) -> pygame.Rect:
        return pygame.Rect(
            self.origin_x_px,
            self.origin_y_px,
            self.tile_size_px * maze.cols,
            self.tile_size_px * maze.rows,
        )

    def draw_world(
        self,
        maze: Maze,
        pacman: PacMan,
        ghosts: list[Ghost],
        *,
        now_s: float,
        fruit: tuple[int, int, str] | None,
    ) -> None:
        self.screen.fill(_hex_to_rgb(self.colours["background"]))
        self._draw_walls(maze)
        self._draw_pellets(maze, now_s=now_s)
        if fruit is not None:
            self._draw_fruit(fruit[0], fruit[1], fruit[2])
        self._draw_pacman(pacman)
        for ghost in ghosts:
            self._draw_ghost(ghost, now_s=now_s)

    def tile_center_px(self, row: int, col: int) -> tuple[int, int]:
        x = self.origin_x_px + col * self.tile_size_px + self.tile_size_px // 2
        y = self.origin_y_px + row * self.tile_size_px + self.tile_size_px // 2
        return x, y

    def _draw_walls(self, maze: Maze) -> None:
        wall_colour = _hex_to_rgb(self.colours["walls"])
        thickness = int(self.sizes.get("wall_thickness_px", 2))
        thickness = max(thickness, 1)
        for row, col in maze.walls:
            x = self.origin_x_px + col * self.tile_size_px
            y = self.origin_y_px + row * self.tile_size_px

            x0 = x
            y0 = y
            x1 = x + self.tile_size_px
            y1 = y + self.tile_size_px

            if row == 0 or not maze.is_wall(row - 1, col):
                pygame.draw.line(self.screen, wall_colour, (x0, y0), (x1, y0), thickness)
            if row == maze.rows - 1 or not maze.is_wall(row + 1, col):
                pygame.draw.line(self.screen, wall_colour, (x0, y1), (x1, y1), thickness)
            if col == 0 or not maze.is_wall(row, col - 1):
                pygame.draw.line(self.screen, wall_colour, (x0, y0), (x0, y1), thickness)
            if col == maze.cols - 1 or not maze.is_wall(row, col + 1):
                pygame.draw.line(self.screen, wall_colour, (x1, y0), (x1, y1), thickness)

    def _draw_pellets(self, maze: Maze, *, now_s: float) -> None:
        pellet_colour = _hex_to_rgb(self.colours["pellets"])
        power_colour = _hex_to_rgb(self.colours["power_pellets"])
        pellet_radius = int(self.sizes["pellet_radius_px"])
        power_radius = int(self.sizes["power_pellet_radius_px"])

        for row, col in maze.pellets:
            x, y = self.tile_center_px(row, col)
            pygame.draw.circle(self.screen, pellet_colour, (x, y), pellet_radius)

        blink_on = int(now_s * 4.0) % 2 == 0
        if blink_on:
            for row, col in maze.power_pellets:
                x, y = self.tile_center_px(row, col)
                pygame.draw.circle(self.screen, power_colour, (x, y), power_radius)

    def _draw_pacman(self, pacman: PacMan) -> None:
        colour = _hex_to_rgb(self.colours["pacman"])
        bg = _hex_to_rgb(self.colours["background"])
        radius = int(self.sizes["pacman_radius_px"])
        x, y = self.tile_center_px(pacman.row, pacman.col)

        pygame.draw.circle(self.screen, colour, (x, y), radius)

        mouth_open_degrees = float(self.animation["pacman_mouth_open_degrees"])
        open_fraction = 0.25 + 0.75 * abs(math.sin(pacman.mouth_phase * 2 * math.pi))
        open_angle = math.radians(mouth_open_degrees * open_fraction)
        direction_angle = _direction_angle_rad(pacman.direction)
        start = direction_angle - open_angle / 2
        end = direction_angle + open_angle / 2

        points = [(x, y)]
        points.append((x + int(math.cos(start) * radius), y + int(math.sin(start) * radius)))
        points.append((x + int(math.cos(end) * radius), y + int(math.sin(end) * radius)))
        pygame.draw.polygon(self.screen, bg, points)

    def _draw_fruit(self, row: int, col: int, name: str) -> None:
        palette = self.colours.get("fruit_palette", {})
        if isinstance(palette, dict) and str(name).lower() in palette:
            colour = _hex_to_rgb(palette[str(name).lower()])
        else:
            colour = _hex_to_rgb(self.colours["fruit"])
        stem = _hex_to_rgb(self.colours.get("fruit_stem", "#2ECC71"))
        leaf = _hex_to_rgb(self.colours.get("fruit_leaf", "#2ECC71"))
        bg = _hex_to_rgb(self.colours["background"])
        radius = int(self.sizes.get("fruit_radius_px", self.sizes.get("power_pellet_radius_px", 7)))
        x, y = self.tile_center_px(row, col)
        r = max(2, radius)

        def shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
            return (
                max(0, min(255, int(rgb[0] * factor))),
                max(0, min(255, int(rgb[1] * factor))),
                max(0, min(255, int(rgb[2] * factor))),
            )

        n = str(name).lower().strip()
        if n == "cherry":
            rr = max(2, int(r * 0.55))
            left_x = x - rr
            right_x = x + rr
            cy = y + max(1, rr // 2)
            pygame.draw.circle(self.screen, colour, (left_x, cy), rr)
            pygame.draw.circle(self.screen, colour, (right_x, cy), rr)
            t = max(1, rr // 3)
            pygame.draw.line(self.screen, stem, (left_x, cy - rr), (x, y - r), t)
            pygame.draw.line(self.screen, stem, (right_x, cy - rr), (x, y - r), t)
            leaf_pts = [(x, y - r), (x + rr, y - r - rr // 2), (x + rr // 2, y - r + rr // 2)]
            pygame.draw.polygon(self.screen, leaf, leaf_pts)
            return

        if n == "strawberry":
            body = pygame.Rect(x - r, y - r, r * 2, r * 2)
            pygame.draw.ellipse(self.screen, colour, body)
            notch = pygame.Rect(x - int(r * 0.6), y - int(r * 1.05), int(r * 1.2), int(r * 0.9))
            pygame.draw.ellipse(self.screen, bg, notch)
            cap = shade(leaf, 0.95)
            cap_pts = [(x - r, y - r // 2), (x, y - r), (x + r, y - r // 2), (x, y - r // 3)]
            pygame.draw.polygon(self.screen, cap, cap_pts)
            return

        if n == "orange":
            pygame.draw.circle(self.screen, colour, (x, y), r)
            pygame.draw.circle(self.screen, shade(colour, 1.15), (x - r // 3, y - r // 3), max(1, r // 3))
            leaf_pts = [(x, y - r), (x + r, y - r + r // 3), (x + r // 4, y - r + r // 2)]
            pygame.draw.polygon(self.screen, leaf, leaf_pts)
            return

        if n == "apple":
            pygame.draw.circle(self.screen, colour, (x, y), r)
            pygame.draw.circle(self.screen, shade(colour, 0.95), (x - r // 2, y), max(1, r // 2))
            pygame.draw.circle(self.screen, bg, (x, y - r + max(1, r // 5)), max(1, r // 3))
            stem_w = max(1, r // 4)
            stem_h = max(2, r // 2)
            pygame.draw.rect(self.screen, stem, pygame.Rect(x - stem_w // 2, y - r - stem_h // 3, stem_w, stem_h))
            leaf_pts = [(x + stem_w, y - r), (x + r, y - r - r // 3), (x + r // 3, y - r + r // 6)]
            pygame.draw.polygon(self.screen, leaf, leaf_pts)
            return

        if n == "pineapple":
            body = pygame.Rect(x - r, y - r, r * 2, int(r * 2.2))
            pygame.draw.ellipse(self.screen, colour, body)
            crown = shade(leaf, 0.9)
            crown_pts = [(x - r, y - r), (x - r // 2, y - int(r * 1.6)), (x, y - r), (x + r // 2, y - int(r * 1.6)), (x + r, y - r)]
            pygame.draw.polygon(self.screen, crown, crown_pts)
            return

        if n == "bell":
            bell_colour = colour
            dome = pygame.Rect(x - r, y - r, r * 2, int(r * 1.8))
            pygame.draw.ellipse(self.screen, bell_colour, dome)
            cut = pygame.Rect(x - r, y - r, r * 2, r)
            pygame.draw.rect(self.screen, bg, cut)
            base_h = max(2, r // 3)
            pygame.draw.rect(self.screen, bell_colour, pygame.Rect(x - r, y + r // 2, r * 2, base_h))
            pygame.draw.circle(self.screen, shade(bell_colour, 0.7), (x, y + r // 2 + base_h), max(1, r // 5))
            return

        if n == "key":
            key_colour = colour
            ring_r = max(2, int(r * 0.55))
            pygame.draw.circle(self.screen, key_colour, (x - r // 3, y), ring_r)
            pygame.draw.circle(self.screen, bg, (x - r // 3, y), max(1, ring_r // 2))
            shaft = pygame.Rect(x - r // 3 + ring_r - 1, y - max(1, r // 8), int(r * 1.4), max(2, r // 4))
            pygame.draw.rect(self.screen, key_colour, shaft)
            tooth_w = max(2, r // 3)
            tooth_h = max(2, r // 3)
            pygame.draw.rect(self.screen, key_colour, pygame.Rect(shaft.right - tooth_w, shaft.bottom - 1, tooth_w // 2, tooth_h))
            pygame.draw.rect(self.screen, key_colour, pygame.Rect(shaft.right - tooth_w // 2, shaft.bottom - 1, tooth_w // 2, tooth_h // 2))
            return

        if n == "galaxian":
            ship = colour
            wing = shade(ship, 0.8)
            body_pts = [(x, y - r), (x - r, y + r // 2), (x, y + r // 4), (x + r, y + r // 2)]
            pygame.draw.polygon(self.screen, ship, body_pts)
            wing_pts = [(x - r, y + r // 2), (x - r // 2, y + r), (x, y + r // 4)]
            pygame.draw.polygon(self.screen, wing, wing_pts)
            wing_pts2 = [(x + r, y + r // 2), (x + r // 2, y + r), (x, y + r // 4)]
            pygame.draw.polygon(self.screen, wing, wing_pts2)
            pygame.draw.circle(self.screen, bg, (x, y), max(1, r // 5))
            return

        pygame.draw.circle(self.screen, colour, (x, y), r)

    def _draw_ghost(self, ghost: Ghost, *, now_s: float) -> None:
        radius = int(self.sizes["ghost_radius_px"])
        x, y = self.tile_center_px(ghost.row, ghost.col)

        if ghost.mode == "eyes":
            eye_white = (255, 255, 255)
            pupil = (0, 0, 0)
            eye_r = max(2, radius // 3)
            pupil_r = max(1, radius // 8)
            eye_y = y - radius // 3
            left_eye_x = x - radius // 3
            right_eye_x = x + radius // 3

            pygame.draw.circle(self.screen, eye_white, (left_eye_x, eye_y), eye_r)
            pygame.draw.circle(self.screen, eye_white, (right_eye_x, eye_y), eye_r)

            pygame.draw.circle(self.screen, pupil, (left_eye_x, eye_y), pupil_r)
            pygame.draw.circle(self.screen, pupil, (right_eye_x, eye_y), pupil_r)
            return

        if ghost.mode == "frightened":
            colour = _hex_to_rgb(self.colours["frightened_ghost"])
        elif ghost.mode == "frightened_flash":
            flash_on = int(now_s * 8.0) % 2 == 0
            colour = _hex_to_rgb(self.colours["frightened_ghost"]) if flash_on else (255, 255, 255)
        else:
            colour = _hex_to_rgb(self.colours["ghosts"][ghost.name])

        pygame.draw.circle(self.screen, colour, (x, y - radius // 3), radius)
        body_rect = pygame.Rect(x - radius, y - radius // 3, radius * 2, radius + radius // 2)
        pygame.draw.rect(self.screen, colour, body_rect)

        eye_white = (255, 255, 255)
        pupil = (0, 0, 0)
        eye_r = max(2, radius // 4)
        pupil_r = max(1, radius // 8)
        eye_y = y - radius // 2
        left_eye_x = x - radius // 3
        right_eye_x = x + radius // 3

        pygame.draw.circle(self.screen, eye_white, (left_eye_x, eye_y), eye_r)
        pygame.draw.circle(self.screen, eye_white, (right_eye_x, eye_y), eye_r)

        pygame.draw.circle(self.screen, pupil, (left_eye_x, eye_y), pupil_r)
        pygame.draw.circle(self.screen, pupil, (right_eye_x, eye_y), pupil_r)


def _direction_angle_rad(direction: str) -> float:
    if direction == "right":
        return 0.0
    if direction == "left":
        return math.pi
    if direction == "up":
        return -math.pi / 2
    if direction == "down":
        return math.pi / 2
    return 0.0


def _hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    if not isinstance(hex_colour, str) or not hex_colour.startswith("#") or len(hex_colour) != 7:
        raise ValueError(f"Invalid colour hex: {hex_colour!r}")
    r = int(hex_colour[1:3], 16)
    g = int(hex_colour[3:5], 16)
    b = int(hex_colour[5:7], 16)
    return r, g, b
