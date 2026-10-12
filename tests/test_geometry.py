import pytest

from laporan_kerja_praktik.geometry import point_on_surface


def test_point_on_surface_handles_concave_polygon():
    outer = ((0, 0), (4, 0), (4, 1), (1, 1), (1, 4), (0, 4), (0, 0))

    assert point_on_surface((outer,)) == pytest.approx((2, 0.5))


def test_point_on_surface_avoids_polygon_hole():
    outer = ((0, 0), (10, 0), (10, 10), (0, 10), (0, 0))
    hole = ((4, 4), (6, 4), (6, 6), (4, 6), (4, 4))

    assert point_on_surface((outer, hole)) == pytest.approx((5, 2))
