from __future__ import annotations

from dataclasses import dataclass


_DIRS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


@dataclass(frozen=True)
class Maze:
    rows: int
    cols: int
    walls: frozenset[tuple[int, int]]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    pacman_spawn: tuple[int, int]
    ghost_spawns: dict[str, tuple[int, int]]
    tunnel_wrap_rows: frozenset[int]
    ghost_house_bounds: tuple[int, int, int, int] | None
    ghost_house_exit: tuple[int, int] | None

    @classmethod
    def from_config(cls, maze_config: dict) -> "Maze":
        legend = maze_config.get("legend", {})
        grid = maze_config.get("grid", [])
        if not isinstance(grid, list) or not all(isinstance(r, str) for r in grid):
            raise ValueError("maze.yaml must contain grid: [<row strings>]")
        if not grid:
            raise ValueError("maze.yaml grid is empty")

        wall_ch = _require_str(legend, "wall")
        pellet_ch = _require_str(legend, "pellet")
        power_pellet_ch = _require_str(legend, "power_pellet")
        empty_ch = _require_str(legend, "empty")
        pacman_spawn_ch = _require_str(legend, "pacman_spawn")
        ghost_spawn_map = legend.get("ghost_spawns", {})
        if not isinstance(ghost_spawn_map, dict) or not ghost_spawn_map:
            raise ValueError("maze.yaml legend.ghost_spawns must be a non-empty mapping")
        ghost_spawn_tokens: dict[str, str] = {}
        for name, token in ghost_spawn_map.items():
            if not isinstance(name, str) or not isinstance(token, str) or len(token) != 1:
                raise ValueError("maze.yaml legend.ghost_spawns must map name -> single-character token")
            ghost_spawn_tokens[name] = token

        cols = len(grid[0])
        if any(len(r) != cols for r in grid):
            raise ValueError("maze.yaml grid rows must all be the same length")

        walls: set[tuple[int, int]] = set()
        pellets: set[tuple[int, int]] = set()
        power_pellets: set[tuple[int, int]] = set()
        pacman_spawn: tuple[int, int] | None = None
        ghost_spawns: dict[str, tuple[int, int]] = {}

        token_to_ghost: dict[str, str] = {token: name for name, token in ghost_spawn_tokens.items()}

        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                pos = (r, c)
                if ch == wall_ch:
                    walls.add(pos)
                    continue
                if ch == pellet_ch:
                    pellets.add(pos)
                    continue
                if ch == power_pellet_ch:
                    power_pellets.add(pos)
                    continue
                if ch == pacman_spawn_ch:
                    if pacman_spawn is not None:
                        raise ValueError("maze.yaml contains more than one pacman spawn token")
                    pacman_spawn = pos
                    continue
                if ch in token_to_ghost:
                    ghost_name = token_to_ghost[ch]
                    if ghost_name in ghost_spawns:
                        raise ValueError(f"maze.yaml contains more than one spawn token for ghost: {ghost_name}")
                    ghost_spawns[ghost_name] = pos
                    continue
                if ch == empty_ch:
                    continue
                raise ValueError(f"maze.yaml grid contains unknown character: {ch!r}")

        if pacman_spawn is None:
            raise ValueError("maze.yaml must include one pacman spawn token in grid")
        if set(ghost_spawns.keys()) != set(ghost_spawn_tokens.keys()):
            missing = sorted(set(ghost_spawn_tokens.keys()) - set(ghost_spawns.keys()))
            raise ValueError(f"maze.yaml missing ghost spawn token(s) in grid: {missing}")

        tunnel_wrap_rows = _parse_tunnel_wrap_rows(maze_config.get("tunnels", {}), rows=len(grid))
        ghost_house_bounds, ghost_house_exit = _parse_ghost_house(maze_config.get("ghost_house", None), rows=len(grid), cols=cols)

        return cls(
            rows=len(grid),
            cols=cols,
            walls=frozenset(walls),
            pellets=frozenset(pellets),
            power_pellets=frozenset(power_pellets),
            pacman_spawn=pacman_spawn,
            ghost_spawns=ghost_spawns,
            tunnel_wrap_rows=tunnel_wrap_rows,
            ghost_house_bounds=ghost_house_bounds,
            ghost_house_exit=ghost_house_exit,
        )

    def is_wall(self, row: int, col: int) -> bool:
        return (row, col) in self.walls

    def in_ghost_house(self, row: int, col: int) -> bool:
        if self.ghost_house_bounds is None:
            return False
        top, left, bottom, right = self.ghost_house_bounds
        return top <= row <= bottom and left <= col <= right and not self.is_wall(row, col)

    def has_pellet(self, row: int, col: int) -> bool:
        return (row, col) in self.pellets or (row, col) in self.power_pellets

    def pellet_kind(self, row: int, col: int) -> str | None:
        pos = (row, col)
        if pos in self.power_pellets:
            return "power"
        if pos in self.pellets:
            return "normal"
        return None

    def next_position(self, row: int, col: int, direction: str) -> tuple[int, int] | None:
        if direction not in _DIRS:
            return None
        dr, dc = _DIRS[direction]
        nr, nc = row + dr, col + dc

        if direction in {"left", "right"} and row in self.tunnel_wrap_rows:
            if nc < 0:
                nc = self.cols - 1
            elif nc >= self.cols:
                nc = 0

        if nr < 0 or nc < 0 or nr >= self.rows or nc >= self.cols:
            return None
        if self.is_wall(nr, nc):
            return None
        return nr, nc

    def eat_pellet(self, row: int, col: int) -> tuple["Maze", str | None]:
        pos = (row, col)
        if pos in self.power_pellets:
            new_power = set(self.power_pellets)
            new_power.remove(pos)
            return (
                Maze(
                    rows=self.rows,
                    cols=self.cols,
                    walls=self.walls,
                    pellets=self.pellets,
                    power_pellets=frozenset(new_power),
                    pacman_spawn=self.pacman_spawn,
                    ghost_spawns=self.ghost_spawns,
                    tunnel_wrap_rows=self.tunnel_wrap_rows,
                    ghost_house_bounds=self.ghost_house_bounds,
                    ghost_house_exit=self.ghost_house_exit,
                ),
                "power",
            )
        if pos in self.pellets:
            new_pellets = set(self.pellets)
            new_pellets.remove(pos)
            return (
                Maze(
                    rows=self.rows,
                    cols=self.cols,
                    walls=self.walls,
                    pellets=frozenset(new_pellets),
                    power_pellets=self.power_pellets,
                    pacman_spawn=self.pacman_spawn,
                    ghost_spawns=self.ghost_spawns,
                    tunnel_wrap_rows=self.tunnel_wrap_rows,
                    ghost_house_bounds=self.ghost_house_bounds,
                    ghost_house_exit=self.ghost_house_exit,
                ),
                "normal",
            )
        return self, None

    def pellet_count(self) -> int:
        return len(self.pellets) + len(self.power_pellets)

    def available_directions(self, row: int, col: int) -> list[str]:
        dirs: list[str] = []
        for name in _DIRS.keys():
            if self.next_position(row, col, name) is not None:
                dirs.append(name)
        return dirs


def _require_str(mapping: dict, key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or len(value) != 1:
        raise ValueError(f"maze.yaml legend.{key} must be a single-character string")
    return value


def _parse_tunnel_wrap_rows(tunnels_config: dict, *, rows: int) -> frozenset[int]:
    if tunnels_config is None:
        return frozenset()
    if not isinstance(tunnels_config, dict):
        raise ValueError("maze.yaml tunnels must be a mapping when provided")
    wrap_rows = tunnels_config.get("wrap_rows", [])
    if wrap_rows is None:
        return frozenset()
    if not isinstance(wrap_rows, list) or not all(isinstance(v, int) for v in wrap_rows):
        raise ValueError("maze.yaml tunnels.wrap_rows must be a list of integers")

    unique_rows = sorted(set(wrap_rows))
    for r in unique_rows:
        if r < 0 or r >= rows:
            raise ValueError("maze.yaml tunnels.wrap_rows contains out-of-range row index")
    return frozenset(unique_rows)


def _parse_ghost_house(ghost_house_config: dict | None, *, rows: int, cols: int) -> tuple[tuple[int, int, int, int] | None, tuple[int, int] | None]:
    if ghost_house_config is None:
        return None, None
    if not isinstance(ghost_house_config, dict):
        raise ValueError("maze.yaml ghost_house must be a mapping when provided")

    bounds = ghost_house_config.get("bounds", None)
    exit_cfg = ghost_house_config.get("exit", None)
    if bounds is None or exit_cfg is None:
        raise ValueError("maze.yaml ghost_house must include bounds and exit")

    if not isinstance(bounds, dict):
        raise ValueError("maze.yaml ghost_house.bounds must be a mapping")
    if not isinstance(exit_cfg, dict):
        raise ValueError("maze.yaml ghost_house.exit must be a mapping")

    top = bounds.get("top")
    left = bounds.get("left")
    bottom = bounds.get("bottom")
    right = bounds.get("right")
    if not all(isinstance(v, int) for v in [top, left, bottom, right]):
        raise ValueError("maze.yaml ghost_house.bounds must contain integer top/left/bottom/right")
    if top < 0 or left < 0 or bottom >= rows or right >= cols or bottom < top or right < left:
        raise ValueError("maze.yaml ghost_house.bounds is out of range")

    exit_row = exit_cfg.get("row")
    exit_col = exit_cfg.get("col")
    if not isinstance(exit_row, int) or not isinstance(exit_col, int):
        raise ValueError("maze.yaml ghost_house.exit must contain integer row/col")
    if exit_row < 0 or exit_col < 0 or exit_row >= rows or exit_col >= cols:
        raise ValueError("maze.yaml ghost_house.exit is out of range")

    return (top, left, bottom, right), (exit_row, exit_col)
