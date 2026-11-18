from __future__ import annotations

from collections.abc import Iterable
from html import escape
from math import log, log2, pi, radians, tan

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale
from shapely.geometry import shape

COLORS = {
    "ink": "#173247",
    "muted": "#52697b",
    "accent": "#0f766e",
    "blue": "#327da8",
    "purple": "#8064a2",
    "green": "#39835e",
    "amber": "#c77b32",
    "surface": "#f3f6f8",
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
    st.markdown(
        """
        <style>
        .block-container {
            padding: 4rem 2.5rem 3rem;
            max-width: 1540px;
        }
        [data-testid="stAppViewContainer"] {background: #f3f6f8;}
        [data-testid="stHeader"] {background: rgba(243,246,248,.95);}
        [data-testid="stSidebar"] {
            background: #edf2f5;
            border-right: 1px solid #dce5eb;
        }
        [data-testid="stSidebarLogo"] {height: 46px; max-height: 46px; width: auto;}
        [data-testid="stSidebarNavLink"] {
            border-radius: 8px;
            padding: .55rem .7rem;
            margin: .15rem 0;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: #d8e9e7;
            color: #0f605a;
            font-weight: 650;
        }
        h1 {font-size: 2.1rem !important; letter-spacing: -.045em; line-height: 1.2;}
        h2 {font-size: 1.4rem !important; letter-spacing: -.025em;}
        h3 {font-size: 1.1rem !important;}
        .page-eyebrow {
            color: #0f766e;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .13em;
            margin: .2rem 0 .35rem;
        }
        .page-description {color: #52697b; font-size: .94rem; line-height: 1.65;}
        .sidebar-scope {
            border-top: 1px solid #d5e0e7;
            margin-top: 1.4rem;
            padding-top: 1.1rem;
            color: #52697b;
            font-size: .8rem;
            line-height: 1.8;
        }
        .sidebar-scope strong {color: #173247;}
        .metric-card, [data-testid="stMetric"] {
            background: #fff;
            border: 1px solid #dce5eb;
            border-radius: 12px;
            padding: 1.05rem 1.15rem;
        }
        .metric-card {border-top: 3px solid #0f766e; min-height: 154px;}
        [data-testid="stMarkdownContainer"]:has(.metric-card) {margin-bottom: 0;}
        .metric-label {color: #52697b; font-size: .8rem; font-weight: 550;}
        .metric-value {
            color: #173247;
            font-size: clamp(1.65rem, 2.4vw, 2.15rem);
            font-weight: 720;
            font-variant-numeric: tabular-nums;
            letter-spacing: -.04em;
            line-height: 1.4;
        }
        .metric-detail {color: #52697b; font-size: .75rem; line-height: 1.5;}
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] p {
            font-size: clamp(1.3rem, 2vw, 1.75rem) !important;
            font-variant-numeric: tabular-nums;
            white-space: normal !important;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
            white-space: normal !important;
        }
        .hero-box {
            border: 1px solid #cce1de;
            background: #eaf4f2;
            border-radius: 12px;
            padding: 1.1rem 1.35rem;
            margin: .4rem 0 .3rem;
            color: #355b60;
            font-size: .88rem;
            line-height: 1.65;
        }
        .hero-box strong {
            display: block;
            font-size: 1.16rem;
            color: #164e49;
            margin-bottom: .2rem;
        }
        .soft-note {
            border-left: 3px solid #0f766e;
            background: #eaf1f4;
            padding: .8rem 1rem;
            border-radius: 0 8px 8px 0;
            color: #385569;
            font-size: .86rem;
            line-height: 1.6;
        }
        .profile-kpis {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .5rem;
            margin: .2rem 0 .8rem;
        }
        .profile-kpi {
            min-width: 0;
            background: #edf5f4;
            border-radius: 8px;
            padding: .75rem .65rem;
        }
        .profile-kpi-label {
            color: #52697b;
            font-size: .7rem;
            line-height: 1.4;
            min-height: 2rem;
            overflow-wrap: anywhere;
        }
        .profile-kpi-value {
            color: #173247;
            font-size: 1.1rem;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            line-height: 1.4;
        }
        [data-testid="stPlotlyChart"] {
            background: #fff;
            box-shadow: 0 0 0 1px #dce5eb;
            border-radius: 12px;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            border-color: #dce5eb;
            border-radius: 12px;
        }
        [data-testid="stDataFrame"] {border: 1px solid #dce5eb; border-radius: 10px;}
        [data-testid="stExpander"] {background: #fff; border-radius: 10px;}
        [data-testid="stCaptionContainer"] {color: #52697b;}
        [data-testid="stPageLink"] a {font-weight: 600;}
        @media (max-width: 1100px) {
            [data-testid="stHorizontalBlock"]:has(.profile-kpis) {flex-wrap: wrap;}
            [data-testid="stHorizontalBlock"]:has(.profile-kpis) > [data-testid="stColumn"] {
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100%;
            }
        }
        @media (max-width: 640px) {
            .block-container {padding: 4rem 1rem 2rem;}
            h1 {font-size: 1.7rem !important;}
            [data-testid="stHorizontalBlock"]:has(.metric-card) {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: .75rem;
            }
            [data-testid="stHorizontalBlock"]:has(.metric-card) > [data-testid="stColumn"] {
                width: auto !important;
                min-width: 0 !important;
            }
            [data-testid="stHorizontalBlock"]:has(.metric-card)
            > [data-testid="stColumn"]:nth-child(3):last-child {
                grid-column: 1 / -1;
            }
            .metric-card {min-height: 168px;}
            .metric-value {font-size: 1.9rem;}
            .hero-box {padding: 1rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.logo(
        """<svg xmlns="http://www.w3.org/2000/svg" width="240" height="56" viewBox="0 0 240 56">
        <rect x="0" y="5" width="42" height="42" rx="11" fill="#0f766e"/>
        <path d="M10 34V23h5v11zm9 0V17h5v17zm9 0V12h5v22z" fill="#fff"/>
        <text x="54" y="25" font-family="sans-serif" font-size="19"
              font-weight="700" fill="#173247">TUBAN</text>
        <text x="54" y="42" font-family="sans-serif" font-size="10"
              letter-spacing="1" fill="#52697b">DATA KETENAGAKERJAAN</text>
        </svg>""",
        size="large",
    )
    st.sidebar.markdown(
        '<div class="sidebar-scope"><strong>Proyek Kerja Praktik · PDPM ITS</strong><br><br>'
        "<strong>Cakupan analisis</strong><br>"
        "328 desa/kelurahan<br>Data administratif, bukan TPT resmi BPS.<br><br>"
        "Peta dan profil untuk eksplorasi deskriptif. "
        "Pemodelan tersedia di bagian analisis teknis.</div>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div>'
        f'<div class="metric-detail">{escape(detail)}</div></div>',
        unsafe_allow_html=True,
    )


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
    st.markdown(
        '<div class="page-eyebrow">ANALISIS PENGANGGURAN · KABUPATEN TUBAN</div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    if description:
        st.markdown(
            f'<div class="page-description">{escape(description)}</div>',
            unsafe_allow_html=True,
        )


def hero(text: str, detail: str) -> None:
    st.markdown(
        f'<div class="hero-box"><strong>{escape(text)}</strong><span>{escape(detail)}</span></div>',
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    st.markdown(f'<div class="soft-note">{escape(text)}</div>', unsafe_allow_html=True)


def profile_kpis(items: list[tuple[str, str]]) -> None:
    cards = "".join(
        f'<div class="profile-kpi"><div class="profile-kpi-label">{escape(label)}</div>'
        f'<div class="profile-kpi-value">{escape(value)}</div></div>'
        for label, value in items
    )
    st.markdown(f'<div class="profile-kpis">{cards}</div>', unsafe_allow_html=True)


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
        margin=dict(l=18, r=30, t=58, b=25),
        font=dict(family="Inter, system-ui, sans-serif", size=12, color=COLORS["ink"]),
        title=dict(
            text=fig.layout.title.text or "",
            font=dict(size=15, color=COLORS["ink"]),
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
