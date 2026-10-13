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


def area_weighted_centroid(polygons: Sequence[Sequence[Ring]]) -> Point:
    """Return the area-weighted centroid of polygon shells and holes."""
    total_area = total_x = total_y = 0.0
    for rings in polygons:
        for index, ring in enumerate(rings):
            twice_area = centroid_x = centroid_y = 0.0
            for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:], strict=True):
                cross = x1 * y2 - x2 * y1
                twice_area += cross
                centroid_x += (x1 + x2) * cross
                centroid_y += (y1 + y2) * cross
            if twice_area == 0:
                continue
            weight = abs(twice_area) / 2
            if index:
                weight = -weight
            total_area += weight
            total_x += centroid_x / (3 * twice_area) * weight
            total_y += centroid_y / (3 * twice_area) * weight
    if total_area <= 0:
        raise ValueError("Luas poligon harus positif untuk menghitung centroid.")
    return total_x / total_area, total_y / total_area


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


def polygon_group_label_point(polygons: Sequence[Sequence[Ring]]) -> Point:
    """Use the area centroid when interior; otherwise choose the representative nearest to it."""
    centroid = area_weighted_centroid(polygons)
    if any(_inside_polygon(centroid, rings) for rings in polygons):
        return centroid

    nearest_point = None
    nearest_distance = float("inf")
    for rings in polygons:
        point = point_on_surface(rings)
        distance = (point[0] - centroid[0]) ** 2 + (point[1] - centroid[1]) ** 2
        if distance < nearest_distance:
            nearest_point = point
            nearest_distance = distance
    if nearest_point is None:
        raise ValueError("Tidak menemukan titik label interior pada kelompok poligon.")
    return nearest_point


def grouped_boundary_segments(
    features: Sequence[dict], group_property: str
) -> list[tuple[Point, Point]]:
    """Keep polygon exterior edges and borders between different groups."""
    edge_groups: dict[tuple[Point, Point], list[str]] = {}
    for feature in features:
        group = str(feature["properties"][group_property])
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            raise ValueError(f"Tipe geometri tidak didukung: {geometry['type']}")

        for polygon in polygons:
            for ring in polygon:
                points = [(float(point[0]), float(point[1])) for point in ring]
                for start, end in zip(points[:-1], points[1:], strict=True):
                    if start == end:
                        continue
                    edge = tuple(sorted((start, end)))
                    edge_groups.setdefault(edge, []).append(group)

    return [
        edge
        for edge, groups in edge_groups.items()
        if len(groups) == 1 or len(set(groups)) > 1
    ]
