from ai_space_invader.bunker import Bunker


def test_bunker_damage_removes_hit_cell_and_neighbours() -> None:
    bunker = Bunker.from_pattern(['###', '###', '###'], x=100, y=200, cell_size=8)
    before = len(bunker.cells)
    hit = bunker.damage_point(108, 208)
    assert hit is True
    assert len(bunker.cells) < before


def test_bunker_damage_returns_false_for_empty_space() -> None:
    bunker = Bunker.from_pattern([' # ', '###'], x=100, y=200, cell_size=8)
    assert bunker.damage_point(100, 200) is False
