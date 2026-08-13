from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Bunker:
    x: int
    y: int
    cell_size: int
    cells: set[tuple[int, int]]

    @classmethod
    def from_pattern(cls, pattern: list[str], *, x: int, y: int, cell_size: int) -> 'Bunker':
        cells: set[tuple[int, int]] = set()
        for row, line in enumerate(pattern):
            for col, char in enumerate(line):
                if char == '#':
                    cells.add((row, col))
        return cls(x=x, y=y, cell_size=cell_size, cells=cells)

    def block_rects(self) -> list[tuple[int, int, int, int]]:
        rects: list[tuple[int, int, int, int]] = []
        for row, col in sorted(self.cells):
            rects.append((
                self.x + col * self.cell_size,
                self.y + row * self.cell_size,
                self.cell_size,
                self.cell_size,
            ))
        return rects

    def damage_point(self, x: float, y: float) -> bool:
        local_col = int((x - self.x) // self.cell_size)
        local_row = int((y - self.y) // self.cell_size)
        target = (local_row, local_col)
        if target not in self.cells:
            return False
        blast = {
            target,
            (local_row - 1, local_col),
            (local_row + 1, local_col),
            (local_row, local_col - 1),
            (local_row, local_col + 1),
        }
        self.cells.difference_update(blast)
        return True
