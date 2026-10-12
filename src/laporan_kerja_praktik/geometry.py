"""Lightweight polygon helpers for placing map labels inside boundaries."""

from collections.abc import Sequence

Point = tuple[float, float]
Ring = Sequence[Point]


def signed_ring_area(ring: Ring) -> float:
    """Return the signed area of a closed polygon ring."""
    return sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:], strict=True)
    ) / 2


def _inside_ring(point: Point, ring: Ring) -> bool:
    x, y = point
    inside = False
    for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:], strict=True):
        if (y1 > y) != (y2 > y):
            intersection_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < intersection_x:
                inside = not inside
    return inside


def _inside_polygon(point: Point, rings: Sequence[Ring]) -> bool:
    return _inside_ring(point, rings[0]) and not any(
        _inside_ring(point, hole) for hole in rings[1:]
    )


def point_on_surface(rings: Sequence[Ring]) -> Point:
    """Return an interior point, including for concave polygons and polygons with holes."""
    outer = rings[0]
    twice_area = centroid_x = centroid_y = 0.0
    for (x1, y1), (x2, y2) in zip(outer[:-1], outer[1:], strict=True):
        cross = x1 * y2 - x2 * y1
        twice_area += cross
        centroid_x += (x1 + x2) * cross
        centroid_y += (y1 + y2) * cross
    if twice_area:
        centroid = (centroid_x / (3 * twice_area), centroid_y / (3 * twice_area))
        if _inside_polygon(centroid, rings):
            return centroid

    levels = sorted({y for ring in rings for _, y in ring})
    widest_interval = 0.0
    best_point = None
    for lower, upper in zip(levels[:-1], levels[1:], strict=True):
        y = (lower + upper) / 2
        intersections = []
        for ring in rings:
            for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:], strict=True):
                if (y1 < y < y2) or (y2 < y < y1):
                    intersections.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        intersections.sort()
        for index in range(0, len(intersections) - 1, 2):
            left, right = intersections[index], intersections[index + 1]
            if right - left > widest_interval:
                widest_interval = right - left
                best_point = ((left + right) / 2, y)
    if best_point is None:
        raise ValueError("Tidak menemukan titik interior pada poligon.")
    return best_point
