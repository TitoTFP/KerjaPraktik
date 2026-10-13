import pytest

from laporan_kerja_praktik.geometry import (
    area_weighted_centroid,
    grouped_boundary_segments,
    point_on_surface,
    polygon_group_label_point,
)


def test_point_on_surface_handles_concave_polygon():
    outer = ((0, 0), (4, 0), (4, 1), (1, 1), (1, 4), (0, 4), (0, 0))

    assert point_on_surface((outer,)) == pytest.approx((2, 0.5))


def test_point_on_surface_avoids_polygon_hole():
    outer = ((0, 0), (10, 0), (10, 10), (0, 10), (0, 0))
    hole = ((4, 4), (6, 4), (6, 6), (4, 6), (4, 4))

    assert point_on_surface((outer, hole)) == pytest.approx((5, 2))


def test_grouped_boundary_segments_dissolve_internal_edges():
    left_ring = ((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))
    right_ring = ((1, 0), (2, 0), (2, 1), (1, 1), (1, 0))
    left = {
        "properties": {"kode_kec": "01"},
        "geometry": {"type": "Polygon", "coordinates": [left_ring]},
    }
    right = {
        "properties": {"kode_kec": "01"},
        "geometry": {"type": "Polygon", "coordinates": [right_ring]},
    }
    shared_edge = ((1.0, 0.0), (1.0, 1.0))

    dissolved = grouped_boundary_segments([left, right], "kode_kec")

    assert len(dissolved) == 6
    assert shared_edge not in dissolved

    right["properties"]["kode_kec"] = "02"
    district_border = grouped_boundary_segments([left, right], "kode_kec")

    assert len(district_border) == 7
    assert shared_edge in district_border


def test_area_weighted_centroid_uses_polygon_group_area():
    left = ((0, 0), (1, 0), (1, 2), (0, 2), (0, 0))
    right = ((1, 0), (5, 0), (5, 2), (1, 2), (1, 0))

    assert area_weighted_centroid(((left,), (right,))) == pytest.approx((2.5, 1))


def test_area_weighted_centroid_subtracts_holes():
    outer = ((0, 0), (10, 0), (10, 10), (0, 10), (0, 0))
    hole = ((1, 1), (3, 1), (3, 3), (1, 3), (1, 1))

    assert area_weighted_centroid(((outer, hole),)) == pytest.approx((5.125, 5.125))


def test_polygon_group_label_point_falls_back_inside_concave_group():
    concave = ((0, 0), (4, 0), (4, 1), (1, 1), (1, 4), (0, 4), (0, 0))

    assert polygon_group_label_point(((concave,),)) == pytest.approx((2, 0.5))
