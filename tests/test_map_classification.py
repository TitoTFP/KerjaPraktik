import pandas as pd
import pytest

from laporan_kerja_praktik.classification import natural_breaks


def test_natural_breaks_finds_weighted_clusters_and_percent_labels():
    values = pd.Series(
        [
            value
            for cluster in ((1, 2, 3), (10, 11, 12), (20, 21, 22), (30, 31, 32), (40, 41, 42))
            for value in cluster
            for _ in range(2)
        ],
        dtype=float,
    )

    bounds, labels = natural_breaks(values)

    assert bounds == (3.0, 12.0, 22.0, 32.0)
    assert labels == (
        "1.00–≤3.00%",
        ">3.00–≤12.00%",
        ">12.00–≤22.00%",
        ">22.00–≤32.00%",
        ">32.00–42.00%",
    )


def test_natural_breaks_requires_enough_distinct_values():
    with pytest.raises(ValueError, match="Natural Breaks memerlukan setidaknya 5 nilai unik"):
        natural_breaks(pd.Series([0.0, 0.0, 1.0, 1.0, 2.0]))
