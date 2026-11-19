from __future__ import annotations

from collections.abc import Iterable
from math import log, log2, pi, radians, tan
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale
from shapely.geometry import shape

COLORS = {
    "ink": "#182b3a",
    "muted": "#536575",
    "accent": "#0f766e",
    "blue": "#327da8",
    "purple": "#8064a2",
    "green": "#39835e",
    "amber": "#c77b32",
    "surface": "#f8fafb",
}

QUADRANT_COLORS = {
    "TPT tinggi + Angkatan kerja besar": "#b34b36",
    "TPT tinggi + Angkatan kerja kecil": "#e7a46c",
    "TPT rendah + Angkatan kerja besar": "#71adbd",
    "TPT rendah + Angkatan kerja kecil": "#326b8c",
}

SECTOR_COLORS = {
    "Pertanian": "#39835e",
    "Industri dan Konstruksi": "#8064a2",
    "Perdagangan dan Akomodasi": "#c77b32",
    "Jasa": "#327da8",
}

DISPLAY_LABELS = {
    "kode_kd": "Kode wilayah",
    "kel_desa": "Desa/kelurahan",
    "kecamatan": "Kecamatan",
    "TPT_Proxy": "TPT",
    "weighted_tpt_proxy": "TPT tertimbang",
    "Total_Penganggur": "Penganggur (orang)",
    "Total_Penduduk_Bekerja": "Penduduk bekerja (orang)",
    "Angkatan_Kerja": "Angkatan kerja (orang)",
    "penganggur": "Penganggur (orang)",
    "total_penganggur": "Penganggur (orang)",
    "total_angkatan_kerja": "Angkatan kerja (orang)",
    "total_penduduk_bekerja": "Penduduk bekerja (orang)",
    "pendidikan_rendah": "Pendidikan rendah (orang)",
    "share_pendidikan_rendah": "Proporsi pendidikan rendah",
    "share_pendidikan_tinggi": "Proporsi pendidikan tinggi",
    "penyakit_kronis": "Kronis tercatat (orang)",
    "share_penyakit_kronis": "Proporsi kronis tercatat",
    "penyakit_unknown": "Tidak diketahui (orang)",
    "share_penyakit_unknown": "Proporsi tidak diketahui",
    "rate_scale_quadrant": "Kuadran rate–skala",
    "rate_group": "Kelompok TPT",
    "education_priority_quadrant": "Kuadran pendidikan",
    "disease_priority_quadrant": "Kuadran kesehatan",
    "sektor_dominan": "Sektor dominan",
    "persentase_penganggur": "Proporsi penganggur",
    "share": "Proporsi",
    "jumlah": "Jumlah (orang)",
    "sektor": "Sektor pekerjaan",
    "kategori": "Kategori",
    "local_cluster_tpt_proxy": "Local Moran TPT",
    "local_cluster_pendidikan_rendah": "Local Moran pendidikan",
    "local_cluster_penyakit_kronis": "Local Moran kesehatan",
    "model": "Model",
    "r2": "R²",
    "adj_r2": "Adjusted R²",
    "aic": "AIC",
    "aicc": "AICc",
    "rmse": "RMSE",
    "residual_moran_i": "Moran's I residual",
    "residual_moran_p": "p residual",
    "gwr_local_r2": "Local R²",
    "gwr_local_condition_number": "Local condition number",
    "variable": "Variabel",
    "coefficient": "Koefisien",
    "se": "Standard error",
    "t": "t-value",
    "p_value_unadjusted": "p tak terkoreksi",
}

CLUSTER_COLORS = {
    "High-High": "#b2182b",
    "Low-Low": "#2166ac",
    "High-Low": "#ef8a62",
    "Low-High": "#67a9cf",
    "Tidak signifikan": "#d9d9d9",
}


def inject_css() -> None:
    st.html(
        """
        <style>
        /* Keep Plotly's toolbar legible on touch and out of the way on desktop. */
        [data-testid="stPlotlyChart"]:has(.gtitle) .modebar {top: 44px !important;}
        [data-testid="stPlotlyChart"] .modebar-group {
            background: #fff !important;
        }
        [data-testid="stPlotlyChart"] .modebar-btn svg path {
            fill: #536575 !important;
        }
        [data-testid="stPlotlyChart"] .modebar-btn:hover svg path,
        [data-testid="stPlotlyChart"] .modebar-btn.active svg path {
            fill: #0f766e !important;
        }
        @media (hover: hover) and (pointer: fine) {
            [data-testid="stPlotlyChart"]:not(:hover):not(:focus-within) .modebar {opacity: 0;}
        }
        /* Keep fixed-grid metrics compact on phones. */
        @media (max-width: 640px) {
            .block-container {padding-top: 4rem;}
            [data-testid="stHorizontalBlock"]:has(
                > [data-testid="stColumn"]:nth-child(3)
            ):has([data-testid="stMetric"]) {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px;
            }
            [data-testid="stHorizontalBlock"]:has(
                > [data-testid="stColumn"]:nth-child(3)
            ) > [data-testid="stColumn"]:has([data-testid="stMetric"]) {
                width: auto;
                min-width: 0;
            }
        }
        </style>
        """
    )


def render_sidebar() -> None:
    st.logo(
        """<svg xmlns="http://www.w3.org/2000/svg" width="152" height="34" viewBox="0 0 152 34"
             font-family="system-ui, sans-serif">
        <text x="0" y="16" font-size="18" font-weight="600" fill="#182b3a">Tuban</text>
        <text x="0" y="31" font-size="12" fill="#536575">Data Pengangguran</text>
        </svg>""",
        size="large",
    )
    st.sidebar.image(
        Path(__file__).with_name("assets") / "pdpm-its.jpg",
        width=80,
        link="https://www.its.ac.id/pdpm/logo-dan-lambang-pdpm/",
    )
    st.sidebar.caption("Proyek Kerja Praktik · **PDPM ITS**")


def metric_card(label: str, value: str, detail: str) -> None:
    st.metric(label, value, help=detail)


def table_columns(df: pd.DataFrame) -> dict:
    config = {}
    percentages = {"TPT_Proxy", "weighted_tpt_proxy", "persentase_penganggur", "share"}
    counts = {
        "Total_Penganggur",
        "Total_Penduduk_Bekerja",
        "Angkatan_Kerja",
        "penganggur",
        "pendidikan_rendah",
        "penyakit_kronis",
        "penyakit_unknown",
        "jumlah",
        "total_penganggur",
        "total_angkatan_kerja",
        "total_penduduk_bekerja",
    }
    for column in df.columns:
        label = DISPLAY_LABELS.get(column, column)
        if column in percentages or column.startswith("share_"):
            config[column] = st.column_config.NumberColumn(label, format="percent")
        elif column in counts:
            config[column] = st.column_config.NumberColumn(label, format="localized")
        elif pd.api.types.is_float_dtype(df[column]):
            config[column] = st.column_config.NumberColumn(label, format="%.4f")
        else:
            config[column] = st.column_config.Column(label)
    return config


def page_header(title: str, description: str | None = None) -> None:
    st.title(title, anchor=False)
    if description:
        st.caption(description)


def profile_kpis(items: list[tuple[str, str]]) -> None:
    with st.container(horizontal=True, gap="medium"):
        for label, value in items:
            st.metric(label, value, width="content")


def pct(value: float | int | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "–"
    return f"{float(value) * 100:.{decimals}f}%".replace(".", ",")


def num(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "–"
    if decimals == 0:
        return f"{float(value):,.0f}".replace(",", ".")
    rendered = f"{float(value):,.{decimals}f}"
    return rendered.replace(",", "_").replace(".", ",").replace("_", ".")


def style_figure(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(
        margin=dict(l=16, r=24, t=72 if fig.layout.title.text else 32, b=24),
        font=dict(family="Source Sans 3, system-ui, sans-serif", size=13, color=COLORS["ink"]),
        title=dict(
            text=fig.layout.title.text or "",
            font=dict(size=16, color=COLORS["ink"]),
            x=0.03,
            xanchor="left",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_color=COLORS["ink"]),
        legend=dict(orientation="h", y=-0.2, x=0, yanchor="top", font_size=11),
        legend_title_text="",
        separators=",.",
    )
    fig.update_xaxes(
        gridcolor="#e9eef2",
        zerolinecolor="#dce5eb",
        title_font=dict(size=11, color=COLORS["muted"]),
        tickfont=dict(size=11, color=COLORS["muted"]),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="#e9eef2",
        zerolinecolor="#dce5eb",
        title_font=dict(size=11, color=COLORS["muted"]),
        tickfont=dict(size=11, color=COLORS["muted"]),
        automargin=True,
    )
    if height:
        fig.update_layout(height=height)
    return fig


def _class_value(value: float, *, percent: bool, decimals: int) -> str:
    if percent:
        return f"{value * 100:.1f}%".replace(".", ",")
    if decimals == 0:
        return num(value)
    return f"{value:.{decimals}f}".replace(".", ",")


def _classified_values(
    df: pd.DataFrame,
    color: str,
    color_scale: str,
    *,
    percent_color: bool,
    midpoint: float | None,
    reference: pd.Series | None = None,
) -> tuple[pd.DataFrame, str, dict[str, str], list[str]]:
    mapped = df.copy()
    values = pd.to_numeric(mapped[color], errors="coerce")
    valid = (
        pd.to_numeric(reference, errors="coerce").dropna()
        if reference is not None
        else values.dropna()
    )
    class_column = f"__class_{color}"

    if valid.empty:
        mapped[class_column] = "Tidak tersedia"
        return mapped, class_column, {"Tidak tersedia": "#d9d9d9"}, ["Tidak tersedia"]

    minimum = float(valid.min())
    maximum = float(valid.max())
    if minimum == maximum:
        decimals = 1 if percent_color else 3
        label = _class_value(minimum, percent=percent_color, decimals=decimals)
        mapped[class_column] = label
        return mapped, class_column, {label: sample_colorscale(color_scale, [0.5])[0]}, [label]

    if midpoint is not None and minimum < midpoint < maximum:
        span = max(midpoint - minimum, maximum - midpoint)
        class_count = 6
        lower = midpoint - span
        upper = midpoint + span
    else:
        class_count = 5
        lower = minimum
        upper = maximum

    step = (upper - lower) / class_count
    edges = [lower + (step * index) for index in range(class_count + 1)]
    edges[0] = min(edges[0], minimum)
    edges[-1] = max(edges[-1], maximum)

    span = maximum - minimum
    if percent_color:
        decimals = 1
    elif span >= 100:
        decimals = 0
    elif span >= 10:
        decimals = 1
    elif span >= 1:
        decimals = 2
    else:
        decimals = 3

    labels = [
        f"{_class_value(edges[index], percent=percent_color, decimals=decimals)} – "
        f"{_class_value(edges[index + 1], percent=percent_color, decimals=decimals)}"
        for index in range(class_count)
    ]
    codes = pd.cut(
        values,
        bins=edges,
        labels=False,
        include_lowest=True,
        duplicates="drop",
    )
    mapped[class_column] = codes.map(
        lambda value: labels[int(value)] if pd.notna(value) else "Tidak tersedia"
    )
    mapped[class_column] = pd.Categorical(
        mapped[class_column],
        categories=[*labels, "Tidak tersedia"],
        ordered=True,
    )

    positions = [(index + 0.5) / class_count for index in range(class_count)]
    colors = sample_colorscale(color_scale, positions)
    discrete_map = dict(zip(labels, colors, strict=True))
    if mapped[class_column].isna().any() or (mapped[class_column] == "Tidak tersedia").any():
        discrete_map["Tidak tersedia"] = "#d9d9d9"
    return mapped, class_column, discrete_map, labels


@st.cache_data(show_spinner=False)
def _geometry_bounds(geojson: dict) -> dict[str, tuple[float, float, float, float]]:
    return {
        str(feature["properties"]["kode_kd"]): shape(feature["geometry"]).bounds
        for feature in geojson["features"]
    }


def choropleth(
    df: pd.DataFrame,
    geojson: dict,
    color: str,
    title: str,
    *,
    labels: dict[str, str] | None = None,
    categorical: bool = False,
    discrete_map: dict[str, str] | None = None,
    midpoint: float | None = None,
    color_scale: str = "YlOrRd",
    percent_color: bool = False,
    extra_hover_data: dict[str, bool | str] | None = None,
    classification_df: pd.DataFrame | None = None,
) -> go.Figure:
    display_labels = DISPLAY_LABELS.copy()
    if labels:
        display_labels.update(labels)
    hover_data: dict[str, bool | str] = {
        "kecamatan": True,
        "TPT_Proxy": ":.2%",
        "Total_Penganggur": ":,.0f",
        "Angkatan_Kerja": ":,.0f",
        "kode_kd": False,
    }
    if percent_color and color not in hover_data:
        hover_data[color] = ":.2%"
    if extra_hover_data:
        hover_data.update(extra_hover_data)

    map_df = df
    map_color = color
    category_orders = None
    if not categorical:
        map_df, map_color, discrete_map, class_order = _classified_values(
            df,
            color,
            color_scale,
            percent_color=percent_color,
            midpoint=midpoint,
            reference=classification_df[color] if classification_df is not None else None,
        )
        display_labels[map_color] = display_labels.get(color, color)
        category_orders = {map_color: class_order}

    common = dict(
        data_frame=map_df,
        geojson=geojson,
        locations="kode_kd",
        featureidkey="properties.kode_kd",
        color=map_color,
        hover_name="kel_desa",
        hover_data=hover_data,
        labels=display_labels,
        custom_data=["kode_kd"],
        opacity=0.86,
        map_style="carto-positron",
    )
    fig = px.choropleth_map(
        **common,
        color_discrete_map=discrete_map,
        category_orders=(
            {color: list(discrete_map)} if categorical and discrete_map else category_orders
        ),
    )
    feature_lookup = {
        str(feature["properties"]["kode_kd"]): feature for feature in geojson["features"]
    }
    for trace in fig.data:
        trace.geojson = {
            "type": "FeatureCollection",
            "features": [feature_lookup[str(code)] for code in trace.locations],
        }
    fig.update_traces(
        marker_line_width=0.6,
        marker_line_color="#ffffff",
        selected_marker_opacity=1,
        unselected_marker_opacity=0.86,
    )
    bounds = _geometry_bounds(geojson)
    selected_bounds = [bounds[str(code)] for code in df["kode_kd"]]
    west = min(bound[0] for bound in selected_bounds)
    south = min(bound[1] for bound in selected_bounds)
    east = max(bound[2] for bound in selected_bounds)
    north = max(bound[3] for bound in selected_bounds)
    padding = max(east - west, north - south) * 0.06
    longitude_span = (east - west + 2 * padding) / 360
    mercator_span = (
        log(tan(pi / 4 + radians(north + padding) / 2))
        - log(tan(pi / 4 + radians(south - padding) / 2))
    ) / (2 * pi)
    # Keep the full extent visible on narrow maps without constraining native pan/zoom.
    zoom = min(log2(260 / (512 * longitude_span)), log2(240 / (512 * mercator_span)))
    fig.update_layout(
        title=title,
        map=dict(
            bearing=0,
            pitch=0,
            zoom=zoom,
            uirevision="tuban-map",
            center=dict(lon=(west + east) / 2, lat=(south + north) / 2),
        ),
        clickmode="event+select",
    )
    return style_figure(fig, 520)


def horizontal_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    *,
    labels: dict[str, str] | None = None,
    percent_x: bool = False,
    color: str | None = None,
) -> go.Figure:
    display_labels = {**DISPLAY_LABELS, **(labels or {})}
    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation="h",
        title=title,
        labels=display_labels,
        color=color,
        color_discrete_sequence=[COLORS["accent"], COLORS["blue"], COLORS["amber"]],
    )
    if color is None:
        fig.update_traces(
            text=[pct(value, 1) if percent_x else num(value) for value in df[x]],
            textposition="outside",
            cliponaxis=False,
            marker_cornerradius=3,
            hovertemplate="%{y}<br>%{x:.1%}<extra></extra>"
            if percent_x
            else "%{y}<br>%{x:,.0f}<extra></extra>",
        )
    if percent_x:
        fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(categoryorder="total ascending", title=None, showgrid=False)
    fig.update_layout(showlegend=color is not None)
    style_figure(fig, max(250, min(480, 110 + 32 * len(df))))
    fig.update_layout(margin_r=70)
    return fig


def download_csv(label: str, df: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
        icon=":material/download:",
    )


def selected_code_from_event(event: object) -> str | None:
    try:
        points: Iterable[dict] = event.selection.points
    except (AttributeError, TypeError):
        return None
    points = list(points)
    if not points:
        return None
    custom = points[0].get("customdata")
    if isinstance(custom, (list, tuple)) and custom:
        return str(custom[0])
    return None
