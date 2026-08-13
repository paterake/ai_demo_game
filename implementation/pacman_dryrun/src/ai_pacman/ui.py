from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class UI:
    screen: pygame.Surface
    hud_height_px: int
    font_size_px: int
    colours: dict

    def __post_init__(self) -> None:
        pygame.font.init()
        self.font = pygame.font.SysFont(None, self.font_size_px)

    def draw_hud(self, *, score: int, lives: int, level: int, fruit_label: str | None = None) -> None:
        text_colour = _hex_to_rgb(self.colours["hud_text"])
        label = f"Score: {score}   Lives: {lives}   Level: {level}"
        if fruit_label:
            label = f"{label}   {fruit_label}"
        surf = self.font.render(label, True, text_colour)
        self.screen.blit(surf, (12, (self.hud_height_px - surf.get_height()) // 2))

    def draw_right_banner(self, *, maze_right_px: int, maze_top_px: int, lines: list[str]) -> None:
        if not lines:
            return
        text_colour = _hex_to_rgb(self.colours["hud_text"])
        x = maze_right_px + 10
        y = maze_top_px + 6
        for line in lines[:3]:
            surf = self.font.render(line, True, text_colour)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 4

    def draw_start_screen(self, *, difficulty_names: list[str], selected_index: int) -> None:
        w, h = self.screen.get_size()
        text_colour = _hex_to_rgb(self.colours["hud_text"])
        title_font = pygame.font.SysFont(None, int(self.font_size_px * 2.4))
        subtitle_font = pygame.font.SysFont(None, int(self.font_size_px * 1.2))

        title = "PAC-MAN"
        title_surf = title_font.render(title, True, text_colour)
        self.screen.blit(title_surf, ((w - title_surf.get_width()) // 2, int(h * 0.18)))

        subtitle = "Select difficulty, then press Enter"
        subtitle_surf = subtitle_font.render(subtitle, True, text_colour)
        self.screen.blit(subtitle_surf, ((w - subtitle_surf.get_width()) // 2, int(h * 0.30)))

        instructions = "Arrow keys to move • Esc to quit"
        inst_surf = self.font.render(instructions, True, text_colour)
        self.screen.blit(inst_surf, ((w - inst_surf.get_width()) // 2, int(h * 0.82)))

        base_y = int(h * 0.42)
        line_h = int(self.font_size_px * 1.6)
        for i, name in enumerate(difficulty_names):
            prefix = "▶ " if i == selected_index else "  "
            label = f"{prefix}{name}"
            surf = self.font.render(label, True, text_colour)
            self.screen.blit(surf, ((w - surf.get_width()) // 2, base_y + i * line_h))

    def draw_countdown(self, *, remaining_s: float) -> None:
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        text_colour = _hex_to_rgb(self.colours["hud_text"])
        big_font = pygame.font.SysFont(None, int(self.font_size_px * 4.0))
        mid_font = pygame.font.SysFont(None, int(self.font_size_px * 1.6))

        if remaining_s >= 2.4:
            label = "READY!"
        elif remaining_s <= 0.4:
            label = "GO!"
        else:
            label = str(int(remaining_s) + 1)

        label_surf = big_font.render(label, True, text_colour)
        hint_surf = mid_font.render("Get Ready...", True, text_colour)

        self.screen.blit(label_surf, ((w - label_surf.get_width()) // 2, (h - label_surf.get_height()) // 2 - 12))
        self.screen.blit(hint_surf, ((w - hint_surf.get_width()) // 2, (h - hint_surf.get_height()) // 2 + 90))

    def draw_overlay(self, *, mode: str) -> None:
        if mode not in {"game_over", "victory", "paused", "level_complete"}:
            return

        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        text_colour = _hex_to_rgb(self.colours["hud_text"])
        big_font = pygame.font.SysFont(None, int(self.font_size_px * 2.0))

        if mode == "paused":
            title = "PAUSED"
            hint = "Press P to resume, Esc to quit"
        elif mode == "level_complete":
            title = "LEVEL COMPLETE"
            hint = "Next level..."
        else:
            title = "GAME OVER" if mode == "game_over" else "VICTORY"
            hint = "Press R to restart, Esc to quit"

        title_surf = big_font.render(title, True, text_colour)
        hint_surf = self.font.render(hint, True, text_colour)

        self.screen.blit(title_surf, ((w - title_surf.get_width()) // 2, (h - title_surf.get_height()) // 2 - 24))
        self.screen.blit(hint_surf, ((w - hint_surf.get_width()) // 2, (h - hint_surf.get_height()) // 2 + 24))


def _hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    if not isinstance(hex_colour, str) or not hex_colour.startswith("#") or len(hex_colour) != 7:
        raise ValueError(f"Invalid colour hex: {hex_colour!r}")
    r = int(hex_colour[1:3], 16)
    g = int(hex_colour[3:5], 16)
    b = int(hex_colour[5:7], 16)
    return r, g, b
