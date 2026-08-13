from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass

from ai_pacman.maze import Maze


_DIRS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

_REVERSE: dict[str, str] = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


@dataclass
class Ghost:
    name: str
    row: int
    col: int
    direction: str
    speed_tiles_per_s: float
    spawn_row: int
    spawn_col: int
    move_accumulator: float = 0.0
    mode: str = "normal"
    regen_until_s: float = 0.0

    def update(
        self,
        dt_s: float,
        maze: Maze,
        *,
        now_s: float,
        pacman_row: int,
        pacman_col: int,
        frightened_active: bool,
        frightened_remaining_s: float,
        frightened_speed_multiplier: float,
        rng: random.Random,
    ) -> None:
        if self.mode == "regenerating":
            if now_s >= self.regen_until_s:
                self.mode = "normal"
            else:
                return

        if self.mode == "eyes":
            self.move_accumulator += (self.speed_tiles_per_s * 1.4) * dt_s
            while self.move_accumulator >= 1.0:
                self._choose_direction_towards(maze, target_row=self.spawn_row, target_col=self.spawn_col)
                next_pos = maze.next_position(self.row, self.col, self.direction)
                if next_pos is None:
                    break
                self.row, self.col = next_pos
                self.move_accumulator -= 1.0
                if (self.row, self.col) == (self.spawn_row, self.spawn_col):
                    self.mode = "regenerating"
                    self.regen_until_s = now_s + 0.8
                    self.direction = "left"
                    self.move_accumulator = 0.0
                    break
            return

        if frightened_active and frightened_remaining_s <= 2.0:
            new_mode = "frightened_flash"
        else:
            new_mode = "frightened" if frightened_active else "normal"
        if new_mode != self.mode:
            self.mode = new_mode
            if self.direction in _REVERSE:
                self.direction = _REVERSE[self.direction]

        speed_multiplier = frightened_speed_multiplier if self.mode in {"frightened", "frightened_flash"} else 1.0
        self.move_accumulator += (self.speed_tiles_per_s * speed_multiplier) * dt_s

        while self.move_accumulator >= 1.0:
            if maze.ghost_house_exit is not None and maze.in_ghost_house(self.row, self.col):
                self._choose_direction_towards(maze, target_row=maze.ghost_house_exit[0], target_col=maze.ghost_house_exit[1])
            else:
                self._choose_direction(
                    maze,
                    target_row=pacman_row,
                    target_col=pacman_col,
                    rng=rng,
                )
            next_pos = maze.next_position(self.row, self.col, self.direction)
            if next_pos is None:
                break

            self.row, self.col = next_pos
            self.move_accumulator -= 1.0

    def reset_to_spawn(self) -> None:
        self.row = self.spawn_row
        self.col = self.spawn_col
        self.direction = "left"
        self.move_accumulator = 0.0
        self.mode = "normal"
        self.regen_until_s = 0.0

    def become_eyes(self) -> None:
        self.mode = "eyes"
        self.move_accumulator = 0.0

    def _choose_direction(self, maze: Maze, *, target_row: int, target_col: int, rng: random.Random) -> None:
        available = maze.available_directions(self.row, self.col)
        if not available:
            return

        reverse = _REVERSE.get(self.direction)

        if self.direction not in available:
            self.direction = rng.choice(available)
            return

        can_continue = self.direction in available
        is_intersection = len(available) >= 3 or (len(available) == 2 and not can_continue)
        if not is_intersection:
            return

        candidates = [d for d in available if d != reverse]
        if not candidates:
            candidates = available

        if self.mode in {"frightened", "frightened_flash"}:
            self.direction = rng.choice(candidates)
            return

        dist_map = _distance_map(maze, target_row=target_row, target_col=target_col)
        best: list[str] = []
        best_dist: int | None = None
        for d in candidates:
            nxt = maze.next_position(self.row, self.col, d)
            if nxt is None:
                continue
            dist = dist_map.get(nxt)
            if dist is None:
                continue
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = [d]
            elif dist == best_dist:
                best.append(d)

        if best:
            self.direction = rng.choice(best)
            return

        self.direction = rng.choice(candidates)

    def _choose_direction_towards(self, maze: Maze, *, target_row: int, target_col: int) -> None:
        available = maze.available_directions(self.row, self.col)
        if not available:
            return
        start = (self.row, self.col)
        target = (target_row, target_col)
        if start == target:
            return

        queue: deque[tuple[int, int]] = deque([start])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        parent_dir: dict[tuple[int, int], str] = {}

        found = False
        while queue:
            cur = queue.popleft()
            if cur == target:
                found = True
                break

            for d in maze.available_directions(cur[0], cur[1]):
                nxt = maze.next_position(cur[0], cur[1], d)
                if nxt is None or nxt in parent:
                    continue
                parent[nxt] = cur
                parent_dir[nxt] = d
                queue.append(nxt)

        if not found:
            if self.direction not in available:
                self.direction = available[0]
            return

        cur = target
        while True:
            p = parent.get(cur)
            if p is None:
                break
            if p == start:
                self.direction = parent_dir[cur]
                return
            cur = p


def _can_step(maze: Maze, row: int, col: int, direction: str) -> bool:
    return maze.next_position(row, col, direction) is not None


def _distance_map(maze: Maze, *, target_row: int, target_col: int) -> dict[tuple[int, int], int]:
    target = (target_row, target_col)
    queue: deque[tuple[int, int]] = deque([target])
    dist: dict[tuple[int, int], int] = {target: 0}

    while queue:
        cur = queue.popleft()
        cur_dist = dist[cur]
        for d in maze.available_directions(cur[0], cur[1]):
            nxt = maze.next_position(cur[0], cur[1], d)
            if nxt is None or nxt in dist:
                continue
            dist[nxt] = cur_dist + 1
            queue.append(nxt)

    return dist
