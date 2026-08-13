from __future__ import annotations

from dataclasses import dataclass

from ai_pacman.maze import Maze


_DIRS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


@dataclass
class PacMan:
    row: int
    col: int
    direction: str
    queued_direction: str | None
    speed_tiles_per_s: float
    move_accumulator: float = 0.0
    mouth_phase: float = 0.0

    def queue_direction(self, direction: str) -> None:
        if direction in _DIRS:
            self.queued_direction = direction

    def update(self, dt_s: float, maze: Maze, mouth_speed_hz: float) -> bool:
        moved = False

        if self.direction == "none":
            if self.queued_direction is not None and maze.next_position(self.row, self.col, self.queued_direction) is not None:
                self.direction = self.queued_direction
            else:
                return False

        self.move_accumulator += self.speed_tiles_per_s * dt_s

        while self.move_accumulator >= 1.0:
            if self.queued_direction is not None and maze.next_position(self.row, self.col, self.queued_direction) is not None:
                self.direction = self.queued_direction

            next_pos = maze.next_position(self.row, self.col, self.direction)
            if next_pos is None:
                self.move_accumulator = 0.0
                break

            self.row, self.col = next_pos
            self.move_accumulator -= 1.0
            moved = True

        if moved:
            self.mouth_phase = (self.mouth_phase + dt_s * mouth_speed_hz) % 1.0

        return moved

    def reset(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.direction = "none"
        self.queued_direction = None
        self.move_accumulator = 0.0
        self.mouth_phase = 0.0


def _can_step(maze: Maze, row: int, col: int, direction: str) -> bool:
    return maze.next_position(row, col, direction) is not None
