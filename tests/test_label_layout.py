from laporan_kerja_praktik.label_layout import place_label_centers


def test_place_label_centers_separates_overlapping_labels():
    anchors = [(20.0, 20.0)] * 4
    sizes = [(12.0, 8.0)] * 4

    centers = place_label_centers(anchors, sizes, (0.0, 0.0, 80.0, 80.0))
    boxes = [
        (x - 7, y - 5, x + 7, y + 5)
        for x, y in centers
    ]

    assert any(center != anchors[0] for center in centers)
    for index, (left, bottom, right, top) in enumerate(boxes):
        for other_left, other_bottom, other_right, other_top in boxes[index + 1 :]:
            assert (
                right <= other_left
                or other_right <= left
                or top <= other_bottom
                or other_top <= bottom
            )
