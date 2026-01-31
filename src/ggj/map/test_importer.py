from ggj.map.importer import surface_blocks


def test_surface_blocks():
    blocks = surface_blocks()
    assert len(blocks) > 0
    assert len(blocks) < 100 * 1000
