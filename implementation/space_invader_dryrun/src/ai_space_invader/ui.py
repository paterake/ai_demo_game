from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ai_space_invader.high_scores import HighScoreEntry


@dataclass
class UI:
    screen: pygame.Surface
    font_size_px: int
    colours: dict
    hud_height_px: int

    def __post_init__(self) -> None:
        pygame.font.init()
        self.font = pygame.font.SysFont(None, self.font_size_px)
        self.title_font = pygame.font.SysFont(None, int(self.font_size_px * 2.6))
        self.big_font = pygame.font.SysFont(None, int(self.font_size_px * 2.0))

    def draw_hud(self, *, score: int, lives: int, level: int, difficulty: str) -> None:
        colour = _hex_to_rgb(self.colours['hud_text'])
        label = f'Score: {score}   Lives: {lives}   Level: {level}   Difficulty: {difficulty}'
        surf = self.font.render(label, True, colour)
        self.screen.blit(surf, (14, (self.hud_height_px - surf.get_height()) // 2))

    def draw_start_screen(
        self,
        *,
        difficulty_names: list[str],
        selected_index: int,
        high_scores: list[HighScoreEntry],
        attract_hint: str | None = None,
    ) -> None:
        width, height = self.screen.get_size()
        colour = _hex_to_rgb(self.colours['hud_text'])
        title = self.title_font.render('SPACE INVADERS', True, colour)
        subtitle = self.font.render('Select difficulty, then press Enter', True, colour)
        controls = self.font.render('Move: Left / Right   Fire: Space   Pause: P', True, colour)
        self.screen.blit(title, ((width - title.get_width()) // 2, int(height * 0.20)))
        self.screen.blit(subtitle, ((width - subtitle.get_width()) // 2, int(height * 0.33)))
        if attract_hint:
            hint = self.font.render(attract_hint, True, colour)
            self.screen.blit(hint, ((width - hint.get_width()) // 2, int(height * 0.37)))
        self.screen.blit(controls, ((width - controls.get_width()) // 2, int(height * 0.78)))
        base_y = int(height * 0.43)
        line_height = int(self.font_size_px * 1.6)
        for idx, name in enumerate(difficulty_names):
            prefix = '▶ ' if idx == selected_index else '  '
            surf = self.font.render(prefix + name, True, colour)
            self.screen.blit(surf, (int(width * 0.22), base_y + idx * line_height))
        self._draw_high_score_table(
            high_scores=high_scores,
            title='HIGH SCORES',
            left_px=int(width * 0.48),
            top_px=int(height * 0.40),
        )

    def draw_countdown(self, *, remaining_s: float) -> None:
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        colour = _hex_to_rgb(self.colours['hud_text'])
        label = 'READY' if remaining_s > 0.5 else 'GO!'
        surf = self.big_font.render(label, True, colour)
        self.screen.blit(surf, ((width - surf.get_width()) // 2, (height - surf.get_height()) // 2))

    def draw_overlay(
        self,
        *,
        mode: str,
        high_scores: list[HighScoreEntry],
        high_score_saved: bool,
        attract_mode: bool = False,
    ) -> None:
        if mode not in {'paused', 'wave_clear', 'game_over', 'victory'}:
            return
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        colour = _hex_to_rgb(self.colours['hud_text'])
        if mode == 'paused':
            title = 'PAUSED'
            hint = 'Press P to resume'
        elif mode == 'wave_clear':
            title = 'WAVE CLEAR'
            hint = 'Incoming formation...'
        elif mode == 'victory':
            title = 'VICTORY'
            hint = 'Press R to restart'
        else:
            title = 'GAME OVER'
            hint = 'Press R to restart'
        if attract_mode and mode in {'game_over', 'victory'}:
            hint = 'Demo restarting. Press any key for start'
        if mode in {'game_over', 'victory'} and high_score_saved:
            hint = 'High score saved. Press R to restart'
        title_surf = self.big_font.render(title, True, colour)
        hint_surf = self.font.render(hint, True, colour)
        title_y = int(height * 0.16)
        self.screen.blit(title_surf, ((width - title_surf.get_width()) // 2, title_y))
        self._draw_high_score_table(
            high_scores=high_scores,
            title='HIGH SCORES',
            left_px=int(width * 0.18),
            top_px=int(height * 0.32),
        )
        self.screen.blit(hint_surf, ((width - hint_surf.get_width()) // 2, int(height * 0.80)))

    def _draw_high_score_table(
        self,
        *,
        high_scores: list[HighScoreEntry],
        title: str,
        left_px: int,
        top_px: int,
    ) -> None:
        colour = _hex_to_rgb(self.colours['hud_text'])
        title_surf = self.font.render(title, True, colour)
        header_surf = self.font.render('#  NAME      SCORE  DIF  LVL  DATE', True, colour)
        self.screen.blit(title_surf, (left_px, top_px))
        self.screen.blit(header_surf, (left_px, top_px + int(self.font_size_px * 1.4)))
        if not high_scores:
            empty_surf = self.font.render('No scores yet', True, colour)
            self.screen.blit(empty_surf, (left_px, top_px + int(self.font_size_px * 2.8)))
            return
        row_y = top_px + int(self.font_size_px * 2.8)
        line_height = int(self.font_size_px * 1.25)
        for index, entry in enumerate(high_scores, start=1):
            name = entry.name[:8].ljust(8)
            difficulty = entry.difficulty[:4].upper().ljust(4)
            date = entry.date[2:] if len(entry.date) >= 10 else entry.date
            label = f'{index:>2} {name} {entry.score:>7} {difficulty} {entry.level:>4} {date}'
            row_surf = self.font.render(label, True, colour)
            self.screen.blit(row_surf, (left_px, row_y))
            row_y += line_height


def _hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    if not isinstance(hex_colour, str) or not hex_colour.startswith('#') or len(hex_colour) != 7:
        raise ValueError(f'Invalid colour hex: {hex_colour!r}')
    return (int(hex_colour[1:3], 16), int(hex_colour[3:5], 16), int(hex_colour[5:7], 16))
