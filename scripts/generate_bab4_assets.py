"""Regenerate Bab IV figures from the repository dataset and village boundaries."""

from __future__ import annotations

import json
import math
from statistics import NormalDist, mean, pstdev

import matplotlib

matplotlib.use("Agg")

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from laporan_kerja_praktik.classification import natural_breaks
from laporan_kerja_praktik.data import PROJECT_ROOT, load_dataset
from laporan_kerja_praktik.geometry import point_on_surface, signed_ring_area
from laporan_kerja_praktik.label_layout import place_label_centers

DATASET_PATH = PROJECT_ROOT / "Datasets" / "Data_Pengangguran_Clean_Audited_8_Sep_2026.csv"
BOUNDARIES_PATH = PROJECT_ROOT / "Datasets" / "Kabupaten Tuban-KEL_DESA.geojson"
OUTPUT_DIR = PROJECT_ROOT / "laporan" / "assets" / "bab-04"

NAVY = "#19364b"
TEAL = "#167c72"
BLUE = "#3978a8"
RED = "#b42332"
ORANGE = "#e57937"
MUTED = "#637783"
GRID = "#d9e2e8"
TPT_MAP_COLORS = ("#FFF1B3", "#FFC55D", "#FD7835", "#E41C26", "#8A012D")
ORRD_MAP_COLORS = ("#FDE5C3", "#FCC38E", "#F68656", "#DF3E2A", "#AC0001")

EDUCATION_GROUPS = {
    "D1 ke atas": ("D1/D2/D3", "D4/S1", "Profesi", "S2", "S3"),
    "SMA/sederajat": ("MA", "MAK", "Paket C", "SMA", "SMK", "SMLB", "SPM/PDF Ulya"),
    "SD/SMP sederajat": (
        "MI",
        "MTs",
        "Paket A",
        "Paket B",
        "SD",
        "SDLB",
        "SMP",
        "SMP LB",
        "SPM/PDF Ula",
        "SPM/PDF Wustha",
    ),
    "Tidak punya ijazah SD": ("Tidak Punya Ijazah SD",),
}

CHRONIC_COLUMNS = (
    "Asma",
    "Diabetes",
    "Hipertensi",
    "Kanker/Tumor Ganas",
    "Kolesterol",
    "Gagal Ginjal",
    "Leukimia",
    "Masalah Jantung",
    "Rematik",
    "Stroke",
    "TBC",
    "Thalasemia",
    "Sirosis Hati",
    "HIV/AIDS",
    "Alzheimer",
    "Haemophilia",
    "Lainnya",
)


def load_report_data() -> pd.DataFrame:
    """Load source counts and derive the Bab IV descriptive indicators."""
    data = load_dataset(DATASET_PATH).copy()
    numeric_columns = {
        "Total_Penganggur",
        "Total_Penduduk_Bekerja",
        "Tidak Ada",
        "Total",
        "#N/A",
        *CHRONIC_COLUMNS,
        *(column for columns in EDUCATION_GROUPS.values() for column in columns),
    }
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="raise").fillna(0)

    labor_force = data["Total_Penganggur"] + data["Total_Penduduk_Bekerja"]
    if (labor_force <= 0).any():
        raise ValueError("Angkatan kerja harus positif untuk menghitung TPT.")
    if (data["Total_Penganggur"] <= 0).any():
        raise ValueError("Jumlah penganggur harus positif untuk menghitung proporsi.")

    data["tpt_pct"] = 100 * data["Total_Penganggur"] / labor_force
    for label, columns in EDUCATION_GROUPS.items():
        data[label] = data[list(columns)].sum(axis=1)
    data["Pendidikan rendah"] = data["SD/SMP sederajat"] + data["Tidak punya ijazah SD"]
    data["Pendidikan tinggi"] = data["D1 ke atas"]
    data["share_pendidikan_rendah"] = 100 * data["Pendidikan rendah"] / data["Total_Penganggur"]
    data["share_pendidikan_tinggi"] = 100 * data["Pendidikan tinggi"] / data["Total_Penganggur"]
    data["Penyakit kronis tercatat"] = data["Total"]
    data["Penyakit tidak diketahui"] = data["#N/A"]
    data["share_penyakit_kronis"] = (
        100 * data["Penyakit kronis tercatat"] / data["Total_Penganggur"]
    )
    return data


def load_boundaries(data: pd.DataFrame) -> tuple[list[dict], float, float]:
    """Read GeoJSON features and verify a one-to-one village-code join."""
    geojson = json.loads(BOUNDARIES_PATH.read_text(encoding="utf-8"))
    features = geojson["features"]
    data_codes = set(data["kode_kd"].astype(str))
    boundary_codes = {str(feature["properties"]["kode_kd"]) for feature in features}
    if len(data_codes) != len(data) or len(boundary_codes) != len(features):
        raise ValueError("Kode desa harus unik pada data dan GeoJSON.")
    if data_codes != boundary_codes:
        raise ValueError("Kode desa pada CSV dan GeoJSON tidak cocok.")
    fids = pd.to_numeric(data["fid"], errors="raise")
    if fids.isna().any() or fids.duplicated().any() or fids.mod(1).ne(0).any():
        raise ValueError("Kolom fid CSV harus terisi, unik, dan berupa bilangan bulat.")
    fids_by_code = dict(
        zip(data["kode_kd"].astype(str), fids.astype(int), strict=True)
    )
    for feature in features:
        feature["properties"]["fid"] = str(
            fids_by_code[str(feature["properties"]["kode_kd"])]
        )
    min_lon = min_lat = float("inf")
    max_lon = max_lat = float("-inf")
    for feature in features:
        for polygon in _polygons(feature["geometry"]):
            for longitude, latitude, *_ in polygon[0]:
                min_lon = min(min_lon, longitude)
                max_lon = max(max_lon, longitude)
                min_lat = min(min_lat, latitude)
                max_lat = max(max_lat, latitude)
    return features, (min_lon + max_lon) / 2, (min_lat + max_lat) / 2


def _polygons(geometry: dict) -> list[list[list[list[float]]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    raise ValueError(f"Tipe geometri tidak didukung: {geometry['type']}")


def _projected_polygons(
    data: pd.DataFrame,
    features: list[dict],
    center_lon: float,
    center_lat: float,
    column: str,
) -> tuple[
    list[list[tuple[float, float]]],
    list[float],
    list[tuple[float, float]],
    list[str],
    tuple[float, float, float, float],
]:
    values = data.set_index(data["kode_kd"].astype(str))[column].to_dict()
    cosine = math.cos(math.radians(center_lat))
    polygons: list[list[tuple[float, float]]] = []
    polygon_values: list[float] = []
    label_points: list[tuple[float, float]] = []
    fid_labels: list[str] = []
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for feature in features:
        code = str(feature["properties"]["kode_kd"])
        value = float(values[code])
        projected_parts = []
        for polygon in _polygons(feature["geometry"]):
            projected_rings = [
                [
                    ((longitude - center_lon) * cosine, latitude)
                    for longitude, latitude, *_ in ring
                ]
                for ring in polygon
            ]
            outer_ring = projected_rings[0]
            for x, y in outer_ring:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
            polygons.append(outer_ring)
            polygon_values.append(value)
            projected_parts.append(projected_rings)

        largest_part = max(
            projected_parts, key=lambda rings: abs(signed_ring_area(rings[0]))
        )
        label_points.append(point_on_surface(largest_part))
        fid_labels.append(str(feature["properties"]["fid"]))
    return (
        polygons,
        polygon_values,
        label_points,
        fid_labels,
        (min_x, max_x, min_y, max_y),
    )



def save_figure(
    fig: plt.Figure,
    filename: str,
    *,
    dpi: int = 180,
    bbox_inches: str | None = "tight",
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUTPUT_DIR / filename,
        dpi=dpi,
        bbox_inches=bbox_inches,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)



def plot_discrete_map(
    data: pd.DataFrame,
    features: list[dict],
    center_lon: float,
    center_lat: float,
    column: str,
    title: str,
    subtitle: str,
    legend_title: str,
    filename: str,
    colors: tuple[str, ...],
    title_size: int = 26,
    title_top: int = 14,
    subtitle_top: int = 45,
) -> None:
    breakpoints, legend_labels = natural_breaks(data[column], len(colors))
    polygons, values, label_points, fid_labels, extent = _projected_polygons(
        data, features, center_lon, center_lat, column
    )
    facecolors = [
        colors[sum(value > breakpoint for breakpoint in breakpoints)] for value in values
    ]
    fig = plt.figure(figsize=(12.8, 7.05), facecolor="white")
    ax = fig.add_axes((92 / 1280, 13 / 705, 884 / 1280, 556 / 705))
    ax.add_collection(
        PolyCollection(
            polygons,
            facecolors=facecolors,
            edgecolors="#fff1dc",
            linewidths=0.3,
        )
    )
    min_x, max_x, min_y, max_y = extent
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect("auto")
    ax.set_axis_off()

    fig.text(
        20 / 1280,
        1 - title_top / 705,
        title,
        color="#193050",
        fontsize=title_size,
        fontweight="bold",
        va="top",
    )
    fig.text(
        20 / 1280,
        1 - subtitle_top / 705,
        subtitle,
        color="#858e98",
        fontsize=10.5,
        va="top",
    )
    fig.text(
        1111 / 1280,
        1 - 116 / 705,
        legend_title,
        color="#242424",
        fontsize=9,
        va="top",
    )
    label_texts = [
        ax.text(
            x,
            y,
            fid,
            color="#19364b",
            fontsize=9,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=5,
            clip_on=True,
            path_effects=[path_effects.withStroke(linewidth=0.7, foreground="white")],
        )
        for (x, y), fid in zip(label_points, fid_labels, strict=True)
    ]
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    label_sizes = [
        (bbox.width, bbox.height)
        for bbox in (text.get_window_extent(renderer) for text in label_texts)
    ]
    anchor_pixels = [ax.transData.transform(point) for point in label_points]
    axes_bounds = ax.bbox
    label_centers = place_label_centers(
        anchor_pixels,
        label_sizes,
        (axes_bounds.x0, axes_bounds.y0, axes_bounds.x1, axes_bounds.y1),
        padding=1.5,
    )
    inverse_transform = ax.transData.inverted()
    for text, anchor, center, (anchor_x, anchor_y) in zip(
        label_texts, anchor_pixels, label_centers, label_points, strict=True
    ):
        x, y = inverse_transform.transform(center)
        text.set_position((x, y))
        if math.dist(anchor, center) > 2:
            leader, = ax.plot(
                (anchor_x, x),
                (anchor_y, y),
                color="#19364b",
                linewidth=0.6,
                alpha=0.8,
                zorder=4,
            )
            leader.set_path_effects(
                [path_effects.withStroke(linewidth=1.4, foreground="white")]
            )
    for index, (color, label) in enumerate(zip(colors, legend_labels, strict=True)):
        row_top = 141 + index * 26
        fig.add_artist(
            Rectangle(
                (1132 / 1280, 1 - (row_top + 14) / 705),
                23 / 1280,
                14 / 705,
                transform=fig.transFigure,
                facecolor=color,
                edgecolor="none",
            )
        )
        fig.text(
            1166 / 1280,
            1 - (row_top + 7) / 705,
            label,
            color="#242424",
            fontsize=9,
            va="center",
        )
    fig.text(
        1055 / 1280,
        1 - 157 / 705,
        "N",
        color="#193050",
        fontsize=12,
        fontweight="bold",
        ha="center",
        va="top",
    )
    fig.text(
        1055 / 1280,
        1 - 200 / 705,
        "↑",
        color="#193050",
        fontsize=27,
        ha="center",
        va="top",
    )

    x_span = max_x - min_x
    y_span = max_y - min_y
    scale_x = min_x + x_span * 0.05
    scale_y = min_y + y_span * 0.055
    scale_length = 10 / 111.32
    ax.plot(
        (scale_x, scale_x + scale_length),
        (scale_y, scale_y),
        color="#193050",
        linewidth=2.8,
        solid_capstyle="butt",
        zorder=3,
    )
    ax.text(
        scale_x + scale_length / 2,
        scale_y + y_span * 0.027,
        "10 km",
        color="#193050",
        fontsize=8.5,
        ha="center",
        va="center",
        zorder=4,
    )
    save_figure(fig, filename, dpi=100, bbox_inches=None)


def plot_tpt_distribution(data: pd.DataFrame) -> None:
    values = data["tpt_pct"].tolist()
    median = pd.Series(values).median()
    fig = plt.figure(figsize=(12, 8), facecolor="white")
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 0.75), hspace=0.38, wspace=0.28)
    histogram = fig.add_subplot(grid[0, 0])
    ecdf = fig.add_subplot(grid[0, 1])
    boxplot = fig.add_subplot(grid[1, :])

    histogram.hist(values, bins=20, color=BLUE, edgecolor="white", linewidth=0.7)
    histogram.axvline(
        median, color=RED, linestyle="--", linewidth=1.5, label=f"Median {median:.1f}%"
    )
    histogram.set(
        title="Distribusi TPT desa/kelurahan", xlabel="TPT (%)", ylabel="Jumlah desa/kelurahan"
    )
    histogram.legend(frameon=False)

    sorted_values = sorted(values)
    ecdf.plot(
        sorted_values, [(index + 1) / len(values) for index in range(len(values))], color=BLUE
    )
    ecdf.set(title="ECDF TPT", xlabel="TPT (%)", ylabel="Proporsi kumulatif", ylim=(0, 1.02))
    ecdf.grid(color=GRID, linewidth=0.6)

    boxplot.boxplot(
        values,
        orientation="horizontal",
        patch_artist=True,
        boxprops={"facecolor": "#91c9df", "edgecolor": NAVY},
        medianprops={"color": RED, "linewidth": 2},
        flierprops={
            "marker": "o",
            "markersize": 4,
            "markerfacecolor": "white",
            "markeredgecolor": MUTED,
        },
    )
    boxplot.set(title="Boxplot TPT", xlabel="TPT (%)", yticks=[1], yticklabels=["TPT"])
    for ax in (histogram, ecdf, boxplot):
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
    fig.suptitle(
        "Distribusi TPT menurut desa/kelurahan", color=NAVY, fontsize=15, fontweight="bold"
    )
    save_figure(fig, "gambar-4-1-distribusi-tpt.png")


def plot_tpt_qq(data: pd.DataFrame) -> None:
    values = sorted(data["tpt_pct"].tolist())
    distribution = NormalDist(mu=mean(values), sigma=pstdev(values))
    theoretical = [
        NormalDist().inv_cdf((rank - 0.5) / len(values)) for rank in range(1, len(values) + 1)
    ]
    fitted = [distribution.mean + distribution.stdev * quantile for quantile in theoretical]
    fig, ax = plt.subplots(figsize=(8, 7), facecolor="white")
    ax.scatter(theoretical, values, s=18, color=BLUE, edgecolors="white", linewidths=0.2)
    ax.plot(theoretical, fitted, color=RED, linewidth=1.4)
    ax.set(
        title="Q-Q plot TPT desa/kelurahan",
        xlabel="Kuantil teoretis normal",
        ylabel="Kuantil TPT teramati (%)",
    )
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    save_figure(fig, "gambar-4-2-qq-tpt.png")




def plot_education_profile(data: pd.DataFrame) -> None:
    labels = list(EDUCATION_GROUPS)
    totals = [data[label].sum() for label in labels]
    total_unemployed = data["Total_Penganggur"].sum()
    percentages = [100 * value / total_unemployed for value in totals]
    palette = (TEAL, "#56b5ad", "#d9b565", "#965416")
    fig, ax = plt.subplots(figsize=(10, 5.8), facecolor="white")
    bars = ax.barh(labels, percentages, color=palette, height=0.78)
    ax.invert_yaxis()
    ax.set(xlabel="Persentase dari seluruh penganggur", xlim=(0, max(percentages) * 1.17))
    ax.set_title("Profil pendidikan penganggur Kabupaten Tuban", color=NAVY, fontweight="bold")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for bar, percentage, amount in zip(bars, percentages, totals, strict=True):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{percentage:.2f}% · {amount:,.0f}",
            va="center",
            fontsize=9,
        )
    save_figure(fig, "gambar-4-4-profil-pendidikan.png")


def plot_education_scatter(data: pd.DataFrame) -> None:
    x = data["Pendidikan rendah"].tolist()
    y = data["share_pendidikan_rendah"].tolist()
    size = [18 + 0.08 * count for count in data["Total_Penganggur"]]
    median_count = pd.Series(x).median()
    median_share = pd.Series(y).median()
    fig, ax = plt.subplots(figsize=(9, 6.8), facecolor="white")
    points = ax.scatter(
        x,
        y,
        s=size,
        c=data["Total_Penganggur"],
        cmap="viridis",
        alpha=0.72,
        edgecolors="white",
        linewidths=0.4,
    )
    ax.axvline(median_count, color=MUTED, linestyle="--", linewidth=0.8)
    ax.axhline(median_share, color=MUTED, linestyle="--", linewidth=0.8)
    ax.set(
        title="Beban absolut dan proporsi pendidikan rendah per desa",
        xlabel="Penganggur berpendidikan rendah (orang)",
        ylabel="Share pendidikan rendah (%)",
    )
    ax.grid(color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    bar = fig.colorbar(points, ax=ax, fraction=0.04, pad=0.04)
    bar.set_label("Total penganggur")
    save_figure(fig, "gambar-4-5-beban-proporsi-pendidikan.png")


def plot_education_by_district(data: pd.DataFrame) -> None:
    district = (
        data.groupby("kecamatan", as_index=False)
        .agg(
            pendidikan_rendah=("Pendidikan rendah", "sum"),
            pendidikan_tinggi=("Pendidikan tinggi", "sum"),
            penganggur=("Total_Penganggur", "sum"),
        )
        .sort_values("pendidikan_rendah", ascending=False)
    )
    district["share_rendah"] = 100 * district["pendidikan_rendah"] / district["penganggur"]
    district["share_tinggi"] = 100 * district["pendidikan_tinggi"] / district["penganggur"]
    district = district.sort_values("share_rendah")
    positions = list(range(len(district)))
    fig, ax = plt.subplots(figsize=(10, 8), facecolor="white")
    for position, (_, row) in zip(positions, district.iterrows(), strict=True):
        ax.plot(
            [row["share_tinggi"], row["share_rendah"]],
            [position, position],
            color="#9ba6aa",
            linewidth=1,
        )
    ax.scatter(
        district["share_rendah"], positions, color=RED, label="Pendidikan rendah", s=40, zorder=3
    )
    ax.scatter(district["share_tinggi"], positions, color=BLUE, label="D1 ke atas", s=40, zorder=3)
    ax.set(
        yticks=positions,
        yticklabels=district["kecamatan"],
        xlabel="Share dari total penganggur (%)",
    )
    ax.set_title(
        "Kontras share pendidikan rendah dan tinggi per kecamatan", color=NAVY, fontweight="bold"
    )
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", frameon=True)
    save_figure(fig, "gambar-4-6-kontras-pendidikan-kecamatan.png")


def plot_chronic_profile(data: pd.DataFrame) -> None:
    total = data["Total_Penganggur"].sum()
    categories = ["Tidak Ada", "Penyakit kronis tercatat", "Unknown/Tidak diketahui"]
    counts = [
        data["Tidak Ada"].sum(),
        data["Penyakit kronis tercatat"].sum(),
        data["Penyakit tidak diketahui"].sum(),
    ]
    shares = [100 * value / total for value in counts]
    colors = ("#b7b7b7", ORANGE, BLUE)
    fig, ax = plt.subplots(figsize=(10, 5.4), facecolor="white")
    bars = ax.barh(categories, shares, color=colors)
    ax.invert_yaxis()
    ax.set(xlabel="Persentase dari total penganggur", xlim=(0, 110))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax.set_title("Profil catatan penyakit pada penganggur", color=NAVY, fontweight="bold")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for bar, share, count in zip(bars, shares, counts, strict=True):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{share:.2f}% · {count:,.0f}",
            va="center",
        )
    save_figure(fig, "gambar-4-8-profil-penyakit-kronis.png")


def main() -> None:
    """Generate the nine data-driven figures referenced by Bab IV."""
    data = load_report_data()
    features, center_lon, center_lat = load_boundaries(data)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": GRID,
            "axes.labelcolor": NAVY,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.titlecolor": NAVY,
            "figure.dpi": 120,
        }
    )
    plot_tpt_distribution(data)
    plot_tpt_qq(data)
    plot_discrete_map(
        data,
        features,
        center_lon,
        center_lat,
        "tpt_pct",
        "TPT",
        "Proporsi penganggur terhadap angkatan kerja · 328 desa/kelurahan",
        "TPT (%)",
        "gambar-4-3-peta-tpt.png",
        TPT_MAP_COLORS,
        title_size=28,
        title_top=5,
        subtitle_top=35,
    )
    plot_education_profile(data)
    plot_education_scatter(data)
    plot_education_by_district(data)
    plot_discrete_map(
        data,
        features,
        center_lon,
        center_lat,
        "share_pendidikan_rendah",
        "Share pendidikan rendah",
        "Profil pendidikan penganggur · 328 desa/kelurahan",
        "Share pendidikan rendah (%)",
        "gambar-4-7-peta-pendidikan-rendah.png",
        ORRD_MAP_COLORS,
        title_size=26,
        title_top=14,
        subtitle_top=45,
    )
    plot_chronic_profile(data)
    plot_discrete_map(
        data,
        features,
        center_lon,
        center_lat,
        "share_penyakit_kronis",
        "Share penyakit kronis tercatat",
        "Profil penyakit pada penganggur · bukan prevalensi penduduk · 328 desa/kelurahan",
        "Share penyakit kronis (%)",
        "gambar-4-9-peta-penyakit-kronis.png",
        ORRD_MAP_COLORS,
        title_size=28,
        title_top=12,
        subtitle_top=43,
    )
    print(f"Dibuat 9 gambar analisis Bab IV di {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
