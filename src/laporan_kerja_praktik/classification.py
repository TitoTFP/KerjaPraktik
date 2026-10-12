"""Classification helpers for report maps."""

import math

import pandas as pd


def natural_breaks(
    values: pd.Series, class_count: int = 5
) -> tuple[tuple[float, ...], tuple[str, ...]]:
    """Find weighted Jenks class bounds minimizing within-class squared deviation."""
    frequencies = values.value_counts().sort_index()
    unique_values = [float(value) for value in frequencies.index]
    weights = [float(weight) for weight in frequencies]
    unique_count = len(unique_values)
    if unique_count < class_count:
        raise ValueError(
            f"Natural Breaks memerlukan setidaknya {class_count} nilai unik; "
            f"ditemukan {unique_count}."
        )

    prefix_weights = [0.0]
    prefix_sums = [0.0]
    prefix_squares = [0.0]
    for value, weight in zip(unique_values, weights, strict=True):
        prefix_weights.append(prefix_weights[-1] + weight)
        prefix_sums.append(prefix_sums[-1] + value * weight)
        prefix_squares.append(prefix_squares[-1] + value * value * weight)

    costs = [[math.inf] * (unique_count + 1) for _ in range(class_count + 1)]
    split_points = [[-1] * (unique_count + 1) for _ in range(class_count + 1)]
    costs[0][0] = 0.0
    for classes in range(1, class_count + 1):
        for end in range(classes, unique_count + 1):
            for start in range(classes - 1, end):
                weight = prefix_weights[end] - prefix_weights[start]
                total = prefix_sums[end] - prefix_sums[start]
                sum_squares = prefix_squares[end] - prefix_squares[start]
                within_class = max(0.0, sum_squares - total * total / weight)
                candidate = costs[classes - 1][start] + within_class
                if candidate < costs[classes][end]:
                    costs[classes][end] = candidate
                    split_points[classes][end] = start

    bounds = []
    end = unique_count
    for classes in range(class_count, 1, -1):
        start = split_points[classes][end]
        bounds.append(unique_values[start - 1])
        end = start
    bounds.reverse()
    breakpoints = tuple(bounds)

    labels = [f"{float(values.min()):.2f}–≤{breakpoints[0]:.2f}%"]
    labels.extend(
        f">{lower:.2f}–≤{upper:.2f}%"
        for lower, upper in zip(breakpoints[:-1], breakpoints[1:], strict=True)
    )
    labels.append(f">{breakpoints[-1]:.2f}–{float(values.max()):.2f}%")
    return breakpoints, tuple(labels)
