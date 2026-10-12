"""Collision-aware placement for compact map labels."""

import math
from collections.abc import Sequence

Point = tuple[float, float]
BoxSize = tuple[float, float]
Bounds = tuple[float, float, float, float]


def place_label_centers(
    anchors: Sequence[Point],
    sizes: Sequence[BoxSize],
    bounds: Bounds,
    *,
    padding: float = 1.0,
    step: float = 8.0,
    max_offset: float = 112.0,
) -> list[Point]:
    """Greedily place label boxes without overlap; return centers in input order."""
    if len(anchors) != len(sizes):
        raise ValueError("Jumlah anchor dan ukuran label harus sama.")
    if not anchors:
        return []

    min_x, min_y, max_x, max_y = bounds
    nearest_distances = []
    for index, (x, y) in enumerate(anchors):
        distances = [
            (x - other_x) ** 2 + (y - other_y) ** 2
            for other_index, (other_x, other_y) in enumerate(anchors)
            if other_index != index
        ]
        nearest_distances.append(min(distances, default=math.inf))
    order = sorted(
        range(len(anchors)),
        key=lambda index: (nearest_distances[index], -sizes[index][0] * sizes[index][1], index),
    )
    directions = tuple(
        (math.cos(math.tau * index / 16), math.sin(math.tau * index / 16))
        for index in range(16)
    )
    radii = (0.0, *map(float, range(int(step), int(max_offset) + 1, int(step))))
    placed_boxes: list[tuple[float, float, float, float]] = []
    placements: list[Point | None] = [None] * len(anchors)

    for index in order:
        width, height = sizes[index]
        half_width = width / 2 + padding
        half_height = height / 2 + padding
        anchor_x, anchor_y = anchors[index]
        best_center = None
        best_score = (math.inf, math.inf)
        for radius in radii:
            candidates = ((0.0, 0.0),) if radius == 0 else (
                (dx * radius, dy * radius) for dx, dy in directions
            )
            free_centers = []
            for offset_x, offset_y in candidates:
                center_x = anchor_x + offset_x
                center_y = anchor_y + offset_y
                if (
                    center_x - half_width < min_x
                    or center_x + half_width > max_x
                    or center_y - half_height < min_y
                    or center_y + half_height > max_y
                ):
                    continue
                box = (
                    center_x - half_width,
                    center_y - half_height,
                    center_x + half_width,
                    center_y + half_height,
                )
                overlap_area = 0.0
                for left, bottom, right, top in placed_boxes:
                    overlap_width = max(0.0, min(box[2], right) - max(box[0], left))
                    overlap_height = max(0.0, min(box[3], top) - max(box[1], bottom))
                    overlap_area += overlap_width * overlap_height
                if overlap_area == 0:
                    free_centers.append((center_x, center_y))
                elif (overlap_area, radius) < best_score:
                    best_score = overlap_area, radius
                    best_center = center_x, center_y
            if free_centers:
                best_center = free_centers[0]
                break

        if best_center is None:
            best_center = (
                min(max(anchor_x, min_x + half_width), max_x - half_width),
                min(max(anchor_y, min_y + half_height), max_y - half_height),
            )
        placements[index] = best_center
        center_x, center_y = best_center
        placed_boxes.append(
            (
                center_x - half_width,
                center_y - half_height,
                center_x + half_width,
                center_y + half_height,
            )
        )

    return [center for center in placements if center is not None]
