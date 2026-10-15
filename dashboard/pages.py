from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.data import (
    SECTOR_GROUPS,
    load_bundle,
    rate_group_sector_profile,
    weighted_sector_profile,
)
from dashboard.ui import (
    CLUSTER_COLORS,
    COLORS,
    QUADRANT_COLORS,
    SECTOR_COLORS,
    choropleth,
    download_csv,
    hero,
    horizontal_bar,
    metric_card,
    note,
    num,
    page_header,
    pct,
    profile_kpis,
    selected_code_from_event,
    style_figure,
    table_columns,
)


def _reset_explorer_state() -> None:
    st.session_state.update(
        {
            "explorer_indicator": "TPT",
            "explorer_kecamatan": "Semua kecamatan",
            "explorer_search": "",
            "explorer_view": "Peta",
            "explorer_quadrant": "Semua kuadran",
            "explorer_selected_code": "",
        }
    )
    st.session_state["explorer_reset_version"] = (
        st.session_state.get("explorer_reset_version", 0) + 1
    )
    for key in list(st.session_state):
        if key.startswith("explorer_map_") or key.startswith("explorer_table_"):
            st.session_state.pop(key, None)


def _select_explorer_map(map_key: str) -> None:
    code = selected_code_from_event(st.session_state[map_key])
    if code:
        st.session_state["explorer_selected_code"] = code


def _select_explorer_table(table_key: str, codes: list[str]) -> None:
    rows = st.session_state[table_key].selection.rows
    if rows:
        st.session_state["explorer_selected_code"] = codes[rows[0]]


def _display_disease_labels(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if "kategori" in frame.columns:
        frame["kategori"] = frame["kategori"].replace(
            {"Unknown/Tidak diketahui": "Tidak diketahui", "Unknown": "Tidak diketahui"}
        )
    return frame


def _profile_charts(row: pd.Series) -> None:
    sector_df = pd.DataFrame(
        {
            "sektor": list(SECTOR_GROUPS),
            "share": [row[f"share_{sector}"] for sector in SECTOR_GROUPS],
        }
    )
    education_df = pd.DataFrame(
        {
            "kategori": ["Rendah", "Menengah", "Tinggi"],
            "share": [
                row["share_pendidikan_rendah"],
                row["share_pendidikan_menengah"],
                row["share_pendidikan_tinggi"],
            ],
        }
    )
    disease_df = pd.DataFrame(
        {
            "kategori": ["Tidak Ada", "Kronis tercatat", "Tidak diketahui"],
            "share": [
                row["share_tidak_ada"],
                row["share_penyakit_kronis"],
                row["share_penyakit_unknown"],
            ],
        }
    )
    sector_tab, education_tab, disease_tab = st.tabs(["Pekerjaan", "Pendidikan", "Kesehatan"])
    with sector_tab:
        st.plotly_chart(
            horizontal_bar(
                sector_df,
                "share",
                "sektor",
                "Komposisi pekerjaan",
                percent_x=True,
            ),
            width="stretch",
        )
        st.caption("Basis: penduduk bekerja; setiap sektor merupakan bagian dari total pekerjaan.")
        st.dataframe(
            sector_df, hide_index=True, width="stretch", column_config=table_columns(sector_df)
        )
    with education_tab:
        st.plotly_chart(
            horizontal_bar(
                education_df,
                "share",
                "kategori",
                "Pendidikan penganggur",
                percent_x=True,
            ),
            width="stretch",
        )
        st.caption(
            "Basis: penganggur. Rendah = tanpa ijazah SD atau SD/SMP; menengah = SMA; "
            "tinggi = D1 ke atas."
        )
        st.dataframe(
            education_df,
            hide_index=True,
            width="stretch",
            column_config=table_columns(education_df),
        )
    with disease_tab:
        st.plotly_chart(
            horizontal_bar(
                disease_df,
                "share",
                "kategori",
                "Penyakit pada penganggur",
                percent_x=True,
            ),
            width="stretch",
        )
        st.caption(
            "Basis: penganggur, bukan seluruh penduduk. "
            "Tidak diketahui tidak digabung ke Tidak Ada."
        )
        st.dataframe(
            disease_df, hide_index=True, width="stretch", column_config=table_columns(disease_df)
        )


def render_overview() -> None:
    bundle = load_bundle()
    village = bundle["village"]
    kecamatan = bundle["kecamatan"]
    tpt = bundle["dashboard_summary"]["tpt_proxy_and_scale"]
    education = bundle["education_overall"]
    disease = _display_disease_labels(bundle["disease_overall"])
    sectors = weighted_sector_profile(village)
    priority = next(
        item
        for item in tpt["rate_scale_quadrants"]
        if item["rate_scale_quadrant"] == "TPT tinggi + Angkatan kerja besar"
    )
    total_unemployed = int(village["Total_Penganggur"].sum())
    total_labor = int(village["Angkatan_Kerja"].sum())

    page_header(
        "TPT Desa/Kelurahan Kabupaten Tuban",
        "TPT = penganggur ÷ (penganggur + penduduk bekerja). "
        "Indikator berbasis data administratif, bukan TPT resmi BPS.",
    )
    cards = [
        (
            "TPT tertimbang",
            pct(tpt["weighted_tpt_proxy"]),
            "Rate kabupaten dari total penganggur ÷ total angkatan kerja.",
        ),
        (
            "Median TPT desa",
            pct(tpt["median_village_tpt_proxy"]),
            f"Titik tengah {num(len(village))} desa/kelurahan, bukan rate kabupaten.",
        ),
        (
            "Total penganggur",
            num(total_unemployed),
            f"orang · dari {num(total_labor)} orang angkatan kerja.",
        ),
        (
            "Kandidat prioritas",
            f"{num(priority['desa'])} desa",
            f"Rate tinggi + skala besar; mencakup {pct(priority['share_penganggur'])} penganggur.",
        ),
    ]
    for column, (label, value, detail) in zip(st.columns(4), cards, strict=True):
        with column:
            metric_card(label, value, detail)

    hero(
        "Rate tinggi tidak selalu berarti beban pengangguran terbesar",
        f"TPT menunjukkan proporsi, sedangkan jumlah penganggur menunjukkan beban absolut. "
        f"Korelasi Spearman TPT dengan ukuran angkatan kerja hanya "
        f"{num(tpt['spearman_rate_vs_labor_force'], 3)}. "
        "Baca keduanya bersama sebelum menentukan wilayah untuk ditelaah.",
    )
    nav1, nav2, nav3 = st.columns(3)
    nav1.page_link(
        st.Page(render_explorer, title="Peta & Wilayah"),
        label="Jelajahi peta & profil desa",
        icon=":material/map:",
        width="stretch",
    )
    nav2.page_link(
        st.Page(render_profiles, title="Profil & Prioritas"),
        label="Telusuri pendidikan & kesehatan",
        icon=":material/bar_chart:",
        width="stretch",
    )
    nav3.page_link(
        st.Page(render_spatial, title="Pola Spasial"),
        label="Periksa prioritas & pola spasial",
        icon=":material/hub:",
        width="stretch",
    )

    st.subheader("Gambaran wilayah")
    left, right = st.columns([1.45, 1], gap="medium")
    with left:
        st.plotly_chart(
            choropleth(village, bundle["geojson"], "TPT_Proxy", "Sebaran TPT", percent_color=True),
            width="stretch",
            key="overview_tpt_map",
        )
        st.caption(
            "328 desa/kelurahan · 5 kelas interval sama · denominator: angkatan kerja. "
            "Buka Peta & Wilayah untuk filter dan detail desa."
        )
        with st.expander("Data TPT desa/kelurahan"):
            map_table = village[
                [
                    "kel_desa",
                    "kecamatan",
                    "TPT_Proxy",
                    "Total_Penganggur",
                    "Angkatan_Kerja",
                ]
            ].sort_values("TPT_Proxy", ascending=False)
            st.dataframe(
                map_table, hide_index=True, width="stretch", column_config=table_columns(map_table)
            )
    with right:
        rank_by = st.segmented_control(
            "Bandingkan kecamatan",
            ["TPT", "Jumlah penganggur"],
            default="TPT",
            required=True,
            key="overview_rank",
        )
        rank_column = "weighted_tpt_proxy" if rank_by == "TPT" else "total_penganggur"
        ranking = kecamatan.nlargest(10, rank_column)
        st.plotly_chart(
            horizontal_bar(
                ranking,
                rank_column,
                "kecamatan",
                "10 kecamatan tertinggi",
                labels={"total_penganggur": "Penganggur (orang)"},
                percent_x=rank_by == "TPT",
            ),
            width="stretch",
        )
        st.caption("TPT kecamatan dihitung dari total penganggur ÷ total angkatan kerja.")
        with st.expander("Lihat data seluruh kecamatan"):
            district_table = kecamatan[
                ["kecamatan", "weighted_tpt_proxy", "total_penganggur", "total_angkatan_kerja"]
            ].sort_values(rank_column, ascending=False)
            st.dataframe(
                district_table,
                hide_index=True,
                width="stretch",
                column_config=table_columns(district_table),
            )
            download_csv(
                "Unduh ringkasan kecamatan",
                district_table,
                "tuban_ringkasan_kecamatan.csv",
                "overview_district_download",
            )

    st.subheader("Siapa yang tercatat menganggur?")
    st.caption("Pendidikan dan kesehatan adalah profil penganggur, bukan penyebab TPT.")
    low_education = education.loc[
        education["kategori"].isin(["Tidak punya ijazah SD", "SD/SMP sederajat"]),
        "persentase_penganggur",
    ].sum()
    chronic = disease.loc[
        disease["kategori"] == "Penyakit kronis (tercatat)", "persentase_penganggur"
    ].iloc[0]
    unknown = disease.loc[disease["kategori"] == "Tidak diketahui", "persentase_penganggur"].iloc[0]
    for column, card in zip(
        st.columns(3),
        [
            (
                "Pendidikan rendah",
                pct(low_education),
                "Tanpa ijazah SD atau lulusan SD/SMP sederajat.",
            ),
            (
                "Kronis tercatat",
                pct(chronic),
                "Profil penyakit pada penganggur, bukan prevalensi penduduk.",
            ),
            ("Kesehatan tidak diketahui", pct(unknown), "Tetap terpisah dari kategori Tidak Ada."),
        ],
        strict=True,
    ):
        with column:
            metric_card(*card)

    education_tab, disease_tab, sector_tab = st.tabs(["Pendidikan", "Kesehatan", "Pekerjaan"])
    for tab, frame, x, y, title, denominator in (
        (
            education_tab,
            education,
            "persentase_penganggur",
            "kategori",
            "Komposisi pendidikan penganggur",
            "Seluruh penganggur kabupaten",
        ),
        (
            disease_tab,
            disease,
            "persentase_penganggur",
            "kategori",
            "Kondisi kesehatan yang tercatat",
            "Seluruh penganggur kabupaten",
        ),
        (
            sector_tab,
            sectors,
            "share",
            "sektor",
            "Komposisi pekerjaan penduduk bekerja",
            "Seluruh penduduk bekerja kabupaten",
        ),
    ):
        with tab:
            chart_col, data_col = st.columns([1.3, 1])
            with chart_col:
                st.plotly_chart(horizontal_bar(frame, x, y, title, percent_x=True), width="stretch")
            with data_col:
                st.caption(f"Denominator: {denominator.lower()}.")
                st.dataframe(
                    frame,
                    hide_index=True,
                    width="stretch",
                    column_config=table_columns(frame),
                )

    with st.expander("Mengapa rate dan skala perlu dibaca bersama?"):
        scatter = px.scatter(
            village,
            x="Angkatan_Kerja",
            y="TPT_Proxy",
            size="Total_Penganggur",
            color="rate_scale_quadrant",
            color_discrete_map=QUADRANT_COLORS,
            hover_name="kel_desa",
            hover_data={"kecamatan": True, "Total_Penganggur": ":,.0f", "TPT_Proxy": ":.2%"},
            labels={
                "Angkatan_Kerja": "Angkatan kerja (orang)",
                "TPT_Proxy": "TPT",
                "rate_scale_quadrant": "Kuadran",
            },
        )
        scatter.add_vline(
            x=village["Angkatan_Kerja"].median(), line_dash="dash", line_color=COLORS["muted"]
        )
        scatter.add_hline(
            y=village["TPT_Proxy"].median(), line_dash="dash", line_color=COLORS["muted"]
        )
        scatter.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_figure(scatter, 480), width="stretch")
        st.caption(
            f"Ukuran titik = jumlah penganggur. Garis putus-putus = median TPT "
            f"{pct(village['TPT_Proxy'].median())} dan angkatan kerja "
            f"{num(village['Angkatan_Kerja'].median())} orang. Cutoff eksploratif, bukan ambang "
            "kebijakan."
        )
        scatter_table = village[
            [
                "kel_desa",
                "kecamatan",
                "TPT_Proxy",
                "Angkatan_Kerja",
                "Total_Penganggur",
                "rate_scale_quadrant",
            ]
        ]
        st.dataframe(
            scatter_table,
            hide_index=True,
            width="stretch",
            column_config=table_columns(scatter_table),
        )


def render_explorer() -> None:
    bundle = load_bundle()
    village = bundle["village"]
    page_header(
        "Peta & Eksplorasi Wilayah",
        "Pilih indikator, persempit wilayah, lalu bandingkan profil desa dengan "
        "kecamatan dan kabupaten.",
    )
    indicator_config = {
        "TPT": ("TPT_Proxy", False, "YlOrRd", True),
        "Jumlah penganggur": ("Total_Penganggur", False, "Blues", False),
        "Angkatan kerja": ("Angkatan_Kerja", False, "Teal", False),
        "Proporsi pendidikan rendah": ("share_pendidikan_rendah", False, "YlOrBr", True),
        "Proporsi pendidikan tinggi": ("share_pendidikan_tinggi", False, "Blues", True),
        "Proporsi penyakit kronis tercatat": ("share_penyakit_kronis", False, "Purples", True),
        "Proporsi tidak diketahui": ("share_penyakit_unknown", False, "Greys", True),
        "Sektor pekerjaan dominan": ("sektor_dominan", True, None, False),
        "Kuadran prioritas": ("rate_scale_quadrant", True, None, False),
    }
    quadrant_options = ["Semua kuadran", *QUADRANT_COLORS]
    with st.container(border=True):
        f1, f2, f3 = st.columns([1.3, 1, 1.2])
        indicator = f1.selectbox("Indikator", list(indicator_config), key="explorer_indicator")
        kecamatan = f2.selectbox(
            "Kecamatan",
            ["Semua kecamatan", *sorted(village["kecamatan"].unique())],
            key="explorer_kecamatan",
        )
        search = f3.text_input(
            "Cari desa/kelurahan",
            placeholder="Nama desa, misalnya Bancar",
            key="explorer_search",
        )
        q1, q2, q3 = st.columns([1.8, 1, 0.65], vertical_alignment="bottom")
        quadrant = q1.selectbox(
            "Kuadran rate–skala",
            quadrant_options,
            key="explorer_quadrant",
            help=(
                "Kategori berdasarkan median seluruh desa di kabupaten, bukan ambang "
                "kebijakan resmi."
            ),
        )
        st.session_state.setdefault("explorer_view", "Peta")
        view_mode = q2.segmented_control(
            "Tampilan",
            ["Peta", "Tabel"],
            required=True,
            key="explorer_view",
        )
        q3.button(
            "Reset filter",
            on_click=_reset_explorer_state,
            icon=":material/restart_alt:",
            width="stretch",
        )

    filtered = village
    if kecamatan != "Semua kecamatan":
        filtered = filtered[filtered["kecamatan"] == kecamatan]
    if search.strip():
        filtered = filtered[
            filtered["kel_desa"].str.contains(search.strip(), case=False, na=False, regex=False)
        ]
    if quadrant != "Semua kuadran":
        filtered = filtered[filtered["rate_scale_quadrant"] == quadrant]
    st.caption(
        f"{num(len(filtered))} dari {num(len(village))} desa/kelurahan · {kecamatan} · {quadrant}"
    )
    if filtered.empty:
        st.info(
            "Tidak ada wilayah yang cocok. Ubah kata pencarian atau gunakan Reset filter.",
            icon=":material/search_off:",
        )
        return

    color_column, categorical, scale, percent_color = indicator_config[indicator]
    if color_column == "TPT_Proxy":
        denominator = "Denominator: angkatan kerja (penganggur + penduduk bekerja)."
    elif color_column.startswith("share_"):
        denominator = "Denominator: penganggur di setiap desa, bukan seluruh penduduk."
    elif color_column == "sektor_dominan":
        denominator = "Sektor dengan proporsi terbesar dari penduduk bekerja."
    elif color_column == "rate_scale_quadrant":
        denominator = (
            f"Cutoff kabupaten: median TPT {pct(village['TPT_Proxy'].median())} "
            f"dan angkatan kerja {num(village['Angkatan_Kerja'].median())} orang."
        )
    else:
        denominator = "Satuan: orang. Jumlah absolut, bukan rate atau proporsi."

    labels = filtered.assign(
        _label=filtered["kel_desa"] + " — " + filtered["kecamatan"]
    ).sort_values(["kecamatan", "kel_desa"])
    valid_codes = labels["kode_kd"].astype(str).tolist()
    if str(st.session_state.get("explorer_selected_code", "")) not in valid_codes:
        st.session_state["explorer_selected_code"] = valid_codes[0]
    scope_key = (
        f"{st.session_state.get('explorer_reset_version', 0)}_"
        f"{color_column}_{kecamatan}_{search.strip()}_{quadrant}"
    )
    map_col, profile_col = st.columns([1.65, 1], gap="medium")

    with map_col:
        st.subheader("Wilayah dalam filter")
        labor = float(filtered["Angkatan_Kerja"].sum())
        unemployed = float(filtered["Total_Penganggur"].sum())
        profile_kpis(
            [
                ("Desa/kelurahan", num(len(filtered))),
                ("TPT tertimbang", pct(unemployed / labor)),
                ("Penganggur (orang)", num(unemployed)),
            ]
        )
        st.caption(denominator)
        if view_mode == "Tabel":
            display_columns = list(
                dict.fromkeys(
                    [
                        "kel_desa",
                        "kecamatan",
                        color_column,
                        "TPT_Proxy",
                        "Total_Penganggur",
                        "Angkatan_Kerja",
                        "rate_scale_quadrant",
                    ]
                )
            )
            display = filtered.sort_values(color_column, ascending=categorical)[display_columns]
            table_key = f"explorer_table_{scope_key}"
            st.dataframe(
                display,
                width="stretch",
                hide_index=True,
                height=520,
                column_config=table_columns(display),
                on_select=lambda: _select_explorer_table(
                    table_key, filtered.loc[display.index, "kode_kd"].astype(str).tolist()
                ),
                selection_mode="single-row",
                key=table_key,
            )
            st.caption("Pilih satu baris untuk membuka profil desa/kelurahan.")
        else:
            discrete = (
                QUADRANT_COLORS
                if color_column == "rate_scale_quadrant"
                else SECTOR_COLORS
                if color_column == "sektor_dominan"
                else None
            )
            map_key = f"explorer_map_{scope_key}"
            st.plotly_chart(
                choropleth(
                    filtered,
                    bundle["geojson"],
                    color_column,
                    indicator,
                    categorical=categorical,
                    discrete_map=discrete,
                    color_scale=scale or "YlOrRd",
                    labels={color_column: indicator},
                    percent_color=percent_color,
                    classification_df=village,
                ),
                width="stretch",
                on_select=lambda: _select_explorer_map(map_key),
                selection_mode="points",
                key=map_key,
            )
            st.caption(
                "Gunakan zoom untuk detail batas desa. Pilih desa pada peta atau "
                "melalui daftar profil. "
                "Kelas dan warna tetap mengacu pada seluruh kabupaten saat filter berubah."
            )
        download_csv(
            "Unduh data wilayah terfilter",
            filtered,
            "tuban_wilayah_terfilter.csv",
            "explorer_download",
        )

    with profile_col:
        with st.container(border=True):
            st.subheader("Profil wilayah")
            label_lookup = labels.set_index("kode_kd")["_label"].to_dict()
            code = st.selectbox(
                "Desa/kelurahan",
                valid_codes,
                format_func=label_lookup.get,
                key="explorer_selected_code",
            )
            row = labels.loc[labels["kode_kd"] == code].iloc[0]
            st.markdown(f"### {row['kel_desa']}")
            st.caption(f"Kecamatan {row['kecamatan']} · Kode {code}")
            profile_kpis(
                [
                    ("TPT", pct(row["TPT_Proxy"])),
                    ("Penganggur (orang)", num(row["Total_Penganggur"])),
                    ("Angkatan kerja (orang)", num(row["Angkatan_Kerja"])),
                ]
            )
            st.caption(
                f"Peringkat TPT #{int(row['rank_tpt_proxy'])}/{len(village)} · "
                f"{row['rate_scale_quadrant']}"
            )
            district_rate = float(
                bundle["kecamatan"]
                .loc[bundle["kecamatan"]["kecamatan"] == row["kecamatan"], "weighted_tpt_proxy"]
                .iloc[0]
            )
            county_rate = float(
                bundle["dashboard_summary"]["tpt_proxy_and_scale"]["weighted_tpt_proxy"]
            )
            gap = float(row["TPT_Proxy"]) - county_rate
            st.caption(
                f"{num(abs(gap) * 100, 2)} poin persentase "
                f"{'di atas' if gap >= 0 else 'di bawah'} TPT kabupaten."
            )
            benchmark = pd.DataFrame(
                {
                    "wilayah": [
                        f"Desa {row['kel_desa']}",
                        f"Kec. {row['kecamatan']}",
                        "Kab. Tuban",
                    ],
                    "TPT": [float(row["TPT_Proxy"]), district_rate, county_rate],
                }
            )
            st.plotly_chart(
                horizontal_bar(benchmark, "TPT", "wilayah", "Perbandingan TPT", percent_x=True),
                width="stretch",
            )
            st.caption("TPT kecamatan dan kabupaten memakai agregasi tertimbang.")
            with st.expander("Pekerjaan, pendidikan & kesehatan"):
                _profile_charts(row)
            with st.expander("Data profil desa"):
                profile_table = filtered[filtered["kode_kd"] == code][
                    [
                        "TPT_Proxy",
                        "Total_Penganggur",
                        "Angkatan_Kerja",
                        "share_pendidikan_rendah",
                        "share_penyakit_kronis",
                        "share_penyakit_unknown",
                    ]
                ]
                st.dataframe(
                    profile_table,
                    hide_index=True,
                    width="stretch",
                    column_config=table_columns(profile_table),
                )
                download_csv(
                    "Unduh profil desa",
                    filtered[filtered["kode_kd"] == code],
                    f"tuban_profil_{code}.csv",
                    "explorer_profile_download",
                )
            st.page_link(
                st.Page(render_gwr, title="GWR & Metodologi"),
                label="Lihat parameter GWR wilayah ini",
                icon=":material/functions:",
                query_params={"kode_kd": code},
            )


def render_profiles() -> None:
    bundle = load_bundle()
    village = bundle["village"]
    geojson = bundle["geojson"]
    page_header(
        "Profil & Prioritas Deskriptif",
        "Kenali pendidikan dan kesehatan penganggur serta struktur pekerjaan wilayah. "
        "Bedakan proporsi dengan jumlah orang; profil ini tidak menjelaskan sebab-akibat.",
    )
    education_tab, disease_tab, work_tab = st.tabs(["Pendidikan", "Kesehatan", "Pekerjaan"])

    with education_tab:
        note(
            "Pendidikan rendah = tanpa ijazah SD atau SD/SMP sederajat. "
            "Denominator: penganggur, bukan seluruh penduduk."
        )
        overall = bundle["education_overall"]
        profile_kpis(
            [
                ("Pendidikan rendah (orang)", num(village["pendidikan_rendah"].sum())),
                (
                    "Proporsi tertimbang",
                    pct(village["pendidikan_rendah"].sum() / village["Total_Penganggur"].sum()),
                ),
                ("Median proporsi desa", pct(village["share_pendidikan_rendah"].median())),
            ]
        )
        left, right = st.columns([1, 1.2])
        with left:
            st.plotly_chart(
                horizontal_bar(
                    overall,
                    "persentase_penganggur",
                    "kategori",
                    "Komposisi pendidikan",
                    percent_x=True,
                ),
                width="stretch",
            )
        with right:
            scatter = px.scatter(
                village,
                x="pendidikan_rendah",
                y="share_pendidikan_rendah",
                color="rate_group",
                size="Total_Penganggur",
                hover_name="kel_desa",
                color_discrete_map={
                    "TPT tinggi": QUADRANT_COLORS["TPT tinggi + Angkatan kerja besar"],
                    "TPT rendah": COLORS["blue"],
                },
                hover_data={
                    "kecamatan": True,
                    "Total_Penganggur": ":,.0f",
                    "share_pendidikan_rendah": ":.2%",
                },
                labels={
                    "pendidikan_rendah": "Pendidikan rendah (orang)",
                    "share_pendidikan_rendah": "Proporsi pendidikan rendah",
                    "rate_group": "Kelompok TPT",
                },
                title="Proporsi vs beban absolut",
            )
            scatter.update_yaxes(tickformat=".0%")
            st.plotly_chart(style_figure(scatter, 320), width="stretch")
        st.caption(
            "Ukuran titik = total penganggur desa. Proporsi tinggi tidak selalu "
            "menunjukkan jumlah orang terbesar."
        )
        with st.expander("Data komposisi & grafik pendidikan"):
            st.dataframe(
                overall, hide_index=True, width="stretch", column_config=table_columns(overall)
            )
            education_data = village[
                [
                    "kel_desa",
                    "kecamatan",
                    "pendidikan_rendah",
                    "share_pendidikan_rendah",
                    "Total_Penganggur",
                    "TPT_Proxy",
                ]
            ].sort_values("share_pendidikan_rendah", ascending=False)
            st.dataframe(
                education_data,
                hide_index=True,
                width="stretch",
                column_config=table_columns(education_data),
            )
        with st.expander("Peta sebaran pendidikan rendah"):
            st.plotly_chart(
                choropleth(
                    village,
                    geojson,
                    "share_pendidikan_rendah",
                    "Proporsi pendidikan rendah",
                    color_scale="YlOrBr",
                    percent_color=True,
                ),
                width="stretch",
            )
            st.caption(
                "Denominator: penganggur di setiap desa. Nilai aktual tersedia pada "
                "tooltip dan data komposisi di atas."
            )

        st.subheader("Wilayah yang perlu ditelaah")
        r1, r2 = st.columns(2)
        level = r1.segmented_control(
            "Unit wilayah",
            ["Kecamatan", "Desa/kelurahan"],
            default="Kecamatan",
            required=True,
            key="education_rank_level",
        )
        rank_by = r2.segmented_control(
            "Urutkan pendidikan rendah",
            ["Jumlah", "Proporsi"],
            default="Jumlah",
            required=True,
            key="education_rank_metric",
        )
        source = bundle["education_kecamatan"] if level == "Kecamatan" else village
        count_column = "penganggur" if level == "Kecamatan" else "Total_Penganggur"
        columns = (["kecamatan"] if level == "Kecamatan" else ["kel_desa", "kecamatan"]) + [
            "pendidikan_rendah",
            "share_pendidikan_rendah",
            count_column,
        ]
        if level == "Kecamatan":
            columns.append("weighted_tpt_proxy")
        sort_column = "pendidikan_rendah" if rank_by == "Jumlah" else "share_pendidikan_rendah"
        ranking = source.sort_values(sort_column, ascending=False)[columns]
        if level == "Desa/kelurahan":
            ranking = ranking.head(25)
        st.caption(
            "Jumlah menyorot beban absolut; proporsi menyorot komposisi penganggur. "
            "Desa ditampilkan 25 teratas."
        )
        st.dataframe(
            ranking, hide_index=True, width="stretch", column_config=table_columns(ranking)
        )
        download_csv(
            "Unduh ranking pendidikan",
            ranking,
            "tuban_ranking_pendidikan.csv",
            "education_rank_download",
        )

    with disease_tab:
        note(
            "Kondisi kronis yang tercatat pada penganggur, bukan prevalensi seluruh penduduk. "
            "Tidak diketahui tetap terpisah dari Tidak Ada."
        )
        overall = _display_disease_labels(bundle["disease_overall"])
        disease_detail = _display_disease_labels(bundle["disease_detail"])
        profile_kpis(
            [
                ("Kronis tercatat (orang)", num(village["penyakit_kronis"].sum())),
                (
                    "Proporsi tertimbang",
                    pct(village["penyakit_kronis"].sum() / village["Total_Penganggur"].sum()),
                ),
                ("Tidak diketahui (orang)", num(village["penyakit_unknown"].sum())),
            ]
        )
        left, right = st.columns([1, 1.2])
        with left:
            st.plotly_chart(
                horizontal_bar(
                    overall,
                    "persentase_penganggur",
                    "kategori",
                    "Profil kesehatan penganggur",
                    percent_x=True,
                ),
                width="stretch",
            )
        with right:
            scatter = px.scatter(
                village,
                x="penyakit_kronis",
                y="share_penyakit_kronis",
                size="Total_Penganggur",
                color="rate_group",
                hover_name="kel_desa",
                color_discrete_map={
                    "TPT tinggi": QUADRANT_COLORS["TPT tinggi + Angkatan kerja besar"],
                    "TPT rendah": COLORS["blue"],
                },
                hover_data={
                    "kecamatan": True,
                    "penyakit_unknown": ":,.0f",
                    "share_penyakit_kronis": ":.2%",
                },
                labels={
                    "penyakit_kronis": "Kronis tercatat (orang)",
                    "share_penyakit_kronis": "Proporsi kronis",
                    "penyakit_unknown": "Tidak diketahui (orang)",
                    "rate_group": "Kelompok TPT",
                },
                title="Proporsi vs jumlah kasus",
            )
            scatter.update_yaxes(tickformat=".0%")
            st.plotly_chart(style_figure(scatter, 320), width="stretch")
        st.caption(
            "Ukuran titik = total penganggur desa. Kategori Tidak Ada berarti tidak "
            "ada kondisi kronis yang tercatat."
        )
        with st.expander("Rincian kondisi kronis tercatat"):
            st.plotly_chart(
                horizontal_bar(
                    disease_detail.sort_values("jumlah", ascending=False).head(12),
                    "jumlah",
                    "kategori",
                    "Kondisi kronis tercatat terbanyak",
                ),
                width="stretch",
            )
            st.dataframe(
                disease_detail,
                hide_index=True,
                width="stretch",
                column_config=table_columns(disease_detail),
            )
        with st.expander("Peta sebaran & data kesehatan desa"):
            st.info(
                "Tidak ada desa yang lolos koreksi FDR untuk Local Moran penyakit kronis. "
                "Peta ini menunjukkan sebaran eksploratif, bukan hotspot atau klaster penyakit."
            )
            st.plotly_chart(
                choropleth(
                    village,
                    geojson,
                    "share_penyakit_kronis",
                    "Proporsi kronis tercatat",
                    color_scale="Purples",
                    percent_color=True,
                ),
                width="stretch",
            )
            disease_data = village[
                [
                    "kel_desa",
                    "kecamatan",
                    "penyakit_kronis",
                    "share_penyakit_kronis",
                    "penyakit_unknown",
                    "share_penyakit_unknown",
                    "Total_Penganggur",
                ]
            ].sort_values("share_penyakit_kronis", ascending=False)
            st.caption(
                "Denominator: penganggur di setiap desa. Kategori tidak diketahui "
                "ditampilkan terpisah pada tabel."
            )
            st.dataframe(
                disease_data,
                hide_index=True,
                width="stretch",
                column_config=table_columns(disease_data),
            )
        with st.expander("Data komposisi kesehatan"):
            st.dataframe(
                overall, hide_index=True, width="stretch", column_config=table_columns(overall)
            )

        st.subheader("Wilayah yang perlu ditelaah")
        r1, r2 = st.columns(2)
        level = r1.segmented_control(
            "Unit wilayah",
            ["Kecamatan", "Desa/kelurahan"],
            default="Kecamatan",
            required=True,
            key="disease_rank_level",
        )
        rank_by = r2.segmented_control(
            "Urutkan kronis tercatat",
            ["Jumlah", "Proporsi"],
            default="Jumlah",
            required=True,
            key="disease_rank_metric",
        )
        source = bundle["disease_kecamatan"] if level == "Kecamatan" else village
        columns = (["kecamatan"] if level == "Kecamatan" else ["kel_desa", "kecamatan"]) + [
            "penyakit_kronis",
            "share_penyakit_kronis",
            "penyakit_unknown",
            "share_penyakit_unknown",
            "penganggur" if level == "Kecamatan" else "Total_Penganggur",
        ]
        sort_column = "penyakit_kronis" if rank_by == "Jumlah" else "share_penyakit_kronis"
        ranking = source.sort_values(sort_column, ascending=False)[columns]
        if level == "Desa/kelurahan":
            ranking = ranking.head(25)
        st.caption(
            "Bandingkan jumlah dan proporsi; ketidaklengkapan pencatatan tetap "
            "terlihat. Desa ditampilkan 25 teratas."
        )
        st.dataframe(
            ranking, hide_index=True, width="stretch", column_config=table_columns(ranking)
        )
        download_csv(
            "Unduh ranking kesehatan",
            ranking,
            "tuban_ranking_kesehatan.csv",
            "disease_rank_download",
        )

    with work_tab:
        note(
            "Denominator: penduduk bekerja. Komposisi sektor adalah profil wilayah, "
            "bukan bukti bahwa sektor tertentu menyebabkan TPT tinggi atau rendah."
        )
        sector_rate = rate_group_sector_profile(village)
        fig = px.bar(
            sector_rate,
            x="share",
            y="rate_group",
            color="sektor",
            orientation="h",
            color_discrete_map=SECTOR_COLORS,
            title="Komposisi sektor menurut kelompok TPT",
            labels={"share": "Proporsi penduduk bekerja", "rate_group": ""},
        )
        fig.update_layout(barmode="stack")
        fig.update_xaxes(tickformat=".0%", range=[0, 1])
        st.plotly_chart(style_figure(fig, 320), width="stretch")
        sector_overall = weighted_sector_profile(village)
        st.plotly_chart(
            horizontal_bar(
                sector_overall, "share", "sektor", "Komposisi pekerjaan kabupaten", percent_x=True
            ),
            width="stretch",
        )
        with st.expander("Data komposisi pekerjaan"):
            st.dataframe(
                sector_overall,
                hide_index=True,
                width="stretch",
                column_config=table_columns(sector_overall),
            )
            st.dataframe(
                sector_rate,
                hide_index=True,
                width="stretch",
                column_config=table_columns(sector_rate),
            )
            download_csv(
                "Unduh profil sektor", sector_rate, "tuban_profil_sektor.csv", "sector_download"
            )


def render_spatial() -> None:
    bundle = load_bundle()
    village = bundle["village"]
    geojson = bundle["geojson"]
    page_header(
        "Prioritas & Pola Spasial",
        "Pilih indikator satu kali, lalu baca pola bertetangga dan perbandingan besarannya.",
    )
    config = {
        "TPT": (
            "local_cluster_tpt_proxy",
            "TPT_Proxy",
            "YlOrRd",
            "TPT = penganggur ÷ angkatan kerja. Skala pembandingnya adalah jumlah angkatan kerja.",
        ),
        "Pendidikan rendah": (
            "local_cluster_pendidikan_rendah",
            "share_pendidikan_rendah",
            "YlOrBr",
            "Pendidikan rendah = tanpa ijazah SD atau SD/SMP sederajat. "
            "Proporsi dihitung dari penganggur; beban adalah jumlah penganggur "
            "berpendidikan rendah.",
        ),
        "Penyakit kronis": (
            "local_cluster_penyakit_kronis",
            "share_penyakit_kronis",
            "Purples",
            "Proporsi kronis tercatat dihitung dari penganggur; beban adalah jumlah "
            "kasus tercatat. "
            "Bukan prevalensi seluruh penduduk; kategori tidak diketahui tetap terpisah.",
        ),
    }
    layer = st.selectbox(
        "Indikator",
        list(config),
        key="spatial_indicator",
        help="Pilihan ini berlaku untuk kedua tab: pola spasial dan perbandingan besaran.",
    )
    cluster_col, continuous_col, scale, definition = config[layer]
    st.caption(definition)
    local_tab, comparison_tab = st.tabs(["Pola spasial · Local Moran", "Besaran & prioritas"])

    with local_tab:
        note(
            "Apakah nilai tinggi atau rendah mengelompok dengan wilayah tetangganya? "
            "Local Moran memakai hubungan ketetanggaan dan koreksi FDR, bukan jumlah kasus."
        )
        summary = (
            bundle["cluster_summary"]
            .loc[bundle["cluster_summary"]["metric"] == continuous_col]
            .iloc[0]
        )
        significant = int(summary["fdr_significant_villages"])
        profile_kpis(
            [
                ("Desa lolos FDR", f"{significant} / {len(village)}"),
                ("High-High", num(summary["High-High"])),
                ("Low-Low", num(summary["Low-Low"])),
            ]
        )
        if layer == "Penyakit kronis" and significant == 0:
            st.info(
                "Tidak ada desa dengan pola lokal penyakit kronis yang lolos FDR. "
                "Yang ditampilkan adalah proporsi kronis tercatat, bukan peta hotspot "
                "atau klaster penyakit."
            )
            fig = choropleth(
                village,
                geojson,
                continuous_col,
                "Sebaran kronis tercatat",
                color_scale=scale,
                percent_color=True,
            )
        else:
            fig = choropleth(
                village,
                geojson,
                cluster_col,
                f"Local Moran · {layer}",
                categorical=True,
                discrete_map=CLUSTER_COLORS,
            )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "KNN-8 · 999 permutasi · Benjamini–Hochberg FDR, α = 0,05. "
            "Pola eksploratif, bukan bukti sebab-akibat."
        )
        with st.expander("Cara membaca kategori Local Moran"):
            st.markdown(
                """
                - **High-High:** nilai tinggi dikelilingi wilayah bernilai tinggi.
                - **Low-Low:** nilai rendah dikelilingi wilayah bernilai rendah.
                - **High-Low / Low-High:** nilai desa berbeda arah dari lingkungan sekitarnya.
                - **Tidak signifikan:** tidak lolos koreksi FDR; bukan bukti
                  bahwa pola spasial tidak ada.
                """
            )
        with st.expander("Data desa & hasil Moran global"):
            local_table = village[
                [
                    "kel_desa",
                    "kecamatan",
                    continuous_col,
                    cluster_col,
                ]
            ].sort_values(continuous_col, ascending=False)
            st.dataframe(
                local_table,
                width="stretch",
                hide_index=True,
                column_config=table_columns(local_table),
            )
            st.caption(
                "Moran global di bawah membandingkan ketiga indikator; tabel desa "
                "mengikuti indikator terpilih."
            )
            moran = bundle["moran"][["label", "moran_I", "permutation_p_value"]].rename(
                columns={
                    "label": "Indikator",
                    "moran_I": "Moran's I",
                    "permutation_p_value": "p permutasi",
                }
            )
            st.dataframe(
                moran, width="stretch", hide_index=True, column_config=table_columns(moran)
            )
            download_csv("Unduh pola lokal", local_table, "tuban_pola_lokal.csv", "local_download")

    with comparison_tab:
        note(
            "Pembacaan ini tidak memakai hubungan ketetanggaan atau uji FDR. "
            "Kuadran memakai median kabupaten, bukan ambang kebijakan resmi; "
            "rate/proporsi tinggi + skala/beban besar bukan kategori High-High Local Moran."
        )
        if layer == "TPT":
            st.subheader("TPT · rate vs skala angkatan kerja")
            st.caption(
                "Cari desa dengan rate tinggi sekaligus angkatan kerja besar. "
                "Jumlah penganggur ditunjukkan oleh ukuran titik, bukan sumbu horizontal."
            )
            priority = village[
                village["rate_scale_quadrant"] == "TPT tinggi + Angkatan kerja besar"
            ]
            profile_kpis(
                [
                    ("Desa kandidat prioritas", num(len(priority))),
                    ("Penganggur (orang)", num(priority["Total_Penganggur"].sum())),
                    (
                        "Proporsi penganggur kabupaten",
                        pct(priority["Total_Penganggur"].sum() / village["Total_Penganggur"].sum()),
                    ),
                ]
            )
            scatter = px.scatter(
                village,
                x="Angkatan_Kerja",
                y="TPT_Proxy",
                color="rate_scale_quadrant",
                color_discrete_map=QUADRANT_COLORS,
                size="Total_Penganggur",
                hover_name="kel_desa",
                hover_data={"kecamatan": True, "Total_Penganggur": ":,.0f", "TPT_Proxy": ":.2%"},
                title="Rate vs skala angkatan kerja",
                labels={
                    "Angkatan_Kerja": "Angkatan kerja (orang)",
                    "TPT_Proxy": "TPT",
                    "rate_scale_quadrant": "Kuadran",
                },
            )
            scatter.add_vline(
                x=village["Angkatan_Kerja"].median(), line_dash="dash", line_color=COLORS["muted"]
            )
            scatter.add_hline(
                y=village["TPT_Proxy"].median(), line_dash="dash", line_color=COLORS["muted"]
            )
            scatter.update_yaxes(tickformat=".0%")
            st.plotly_chart(style_figure(scatter, 480), width="stretch")
            st.caption(
                f"Ukuran titik = penganggur. Garis median: TPT "
                f"{pct(village['TPT_Proxy'].median())}; angkatan kerja "
                f"{num(village['Angkatan_Kerja'].median())} orang."
            )
            priority_table = priority[
                [
                    "kel_desa",
                    "kecamatan",
                    "TPT_Proxy",
                    "Total_Penganggur",
                    "Angkatan_Kerja",
                ]
            ].sort_values("Total_Penganggur", ascending=False)
            with st.expander(f"Daftar {len(priority)} kandidat prioritas"):
                st.dataframe(
                    priority_table,
                    hide_index=True,
                    width="stretch",
                    column_config=table_columns(priority_table),
                )
            download_csv(
                f"Unduh {len(priority)} kandidat prioritas",
                priority,
                "tuban_kandidat_prioritas_rate_skala.csv",
                "priority_download",
            )
            with st.expander("Data seluruh kuadran rate–skala"):
                quadrant_table = village[
                    [
                        "kel_desa",
                        "kecamatan",
                        "TPT_Proxy",
                        "Total_Penganggur",
                        "Angkatan_Kerja",
                        "rate_scale_quadrant",
                    ]
                ]
                st.dataframe(
                    quadrant_table,
                    hide_index=True,
                    width="stretch",
                    column_config=table_columns(quadrant_table),
                )
        else:
            profile = "Pendidikan rendah" if layer == "Pendidikan rendah" else "Kronis tercatat"
            st.subheader(f"{profile} · proporsi vs beban")
            st.caption(
                "Bandingkan bagian penganggur yang memiliki karakteristik ini dengan "
                "jumlah absolutnya. "
                "Keduanya adalah profil penganggur, bukan penyebab TPT."
            )
            if layer == "Pendidikan rendah":
                x, y, color = (
                    "pendidikan_rendah",
                    "share_pendidikan_rendah",
                    "education_priority_quadrant",
                )
            else:
                x, y, color = (
                    "penyakit_kronis",
                    "share_penyakit_kronis",
                    "disease_priority_quadrant",
                )
            scatter = px.scatter(
                village,
                x=x,
                y=y,
                color=color,
                size="Total_Penganggur",
                hover_name="kel_desa",
                color_discrete_sequence=list(QUADRANT_COLORS.values()),
                hover_data={"kecamatan": True, "Total_Penganggur": ":,.0f", y: ":.2%"},
                title=f"{profile} · proporsi vs jumlah",
                labels={
                    x: f"{profile} (orang)",
                    y: f"Proporsi {profile.lower()}",
                    color: "Kuadran profil",
                },
            )
            scatter.add_vline(x=village[x].median(), line_dash="dash", line_color=COLORS["muted"])
            scatter.add_hline(y=village[y].median(), line_dash="dash", line_color=COLORS["muted"])
            scatter.update_yaxes(tickformat=".0%")
            st.plotly_chart(style_figure(scatter, 480), width="stretch")
            st.caption(
                f"Ukuran titik = total penganggur. Median proporsi {pct(village[y].median())}; "
                f"median jumlah {num(village[x].median())} orang."
            )
            profile_columns = ["kel_desa", "kecamatan", x, y, "Total_Penganggur", color]
            if layer == "Penyakit kronis":
                profile_columns.extend(["penyakit_unknown", "share_penyakit_unknown"])
            with st.expander("Data kuadran profil"):
                profile_table = village[profile_columns].sort_values(x, ascending=False)
                st.dataframe(
                    profile_table,
                    hide_index=True,
                    width="stretch",
                    column_config=table_columns(profile_table),
                )


def render_gwr() -> None:
    bundle = load_bundle()
    village = bundle["village"]
    geojson = bundle["geojson"]
    comparison = bundle["model_comparison"]
    spatial_summary = bundle["spatial_summary"]
    params = bundle["gwr_parameters"].copy()
    coefficient_summary = bundle["gwr_coefficients"].copy()

    page_header(
        "GWR & Metodologi",
        "Halaman teknis untuk membandingkan model global dan lokal serta "
        "memeriksa variasi koefisien GWR.",
    )
    st.warning(
        "GWR bersifat asosiatif, bukan kausal. Moran's I residual GWR masih "
        "0,0587 (p = 0,038), sehingga struktur spasial berkurang kuat tetapi "
        "belum hilang sepenuhnya."
    )

    ols = comparison.loc[comparison["model"] == "OLS"].iloc[0]
    gwr = comparison.loc[comparison["model"].str.startswith("GWR")].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R² GWR", num(gwr["r2"], 3), delta=f"+{num(gwr['r2'] - ols['r2'], 3)} vs OLS")
    c2.metric("Adjusted R² GWR", num(gwr["adj_r2"], 3))
    c3.metric(
        "RMSE GWR",
        num(gwr["rmse"], 4),
        delta=f"{num(gwr['rmse'] - ols['rmse'], 4)} vs OLS",
        delta_color="inverse",
    )
    c4.metric(
        "AICc GWR",
        num(gwr["aicc"], 2),
        delta=f"{num(gwr['aicc'] - ols['aicc'], 2)} vs OLS",
        delta_color="inverse",
    )

    compare_view = comparison[
        [
            "model",
            "r2",
            "adj_r2",
            "aic",
            "aicc",
            "rmse",
            "residual_moran_i",
            "residual_moran_p",
        ]
    ].copy()
    st.subheader("Perbandingan model global & lokal")
    st.dataframe(
        compare_view, width="stretch", hide_index=True, column_config=table_columns(compare_view)
    )

    kernels = bundle["gwr_kernels"].sort_values("aicc")
    kernel_fig = px.scatter(
        kernels,
        x="aicc",
        y="kernel",
        text=kernels["aicc"].map(lambda value: num(value, 2)),
        title="Sensitivitas kernel (AICc)",
        labels={"kernel": "Kernel", "aicc": "AICc"},
        color_discrete_sequence=[COLORS["accent"]],
    )
    # The final sorted kernel is the top y-category; keep its annotation inside the plot.
    label_positions = ["top center"] * len(kernels)
    label_positions[-1] = "bottom center"
    kernel_fig.update_traces(marker_size=12, textposition=label_positions)
    st.plotly_chart(style_figure(kernel_fig, 280), width="stretch")
    st.caption(
        "AICc lebih rendah lebih baik. Selisih AICc antarkernel kecil (<2 "
        "antara model teratas), sehingga Gaussian dipakai sebagai model utama "
        "berdasarkan AICc minimum yang tervalidasi, bukan sebagai bukti dominasi "
        "mutlak kernel."
    )
    with st.expander("Data sensitivitas kernel"):
        st.dataframe(
            kernels, hide_index=True, width="stretch", column_config=table_columns(kernels)
        )

    st.subheader("Signifikansi koefisien lokal setelah koreksi")
    variable_labels = {
        "share_perdagangan": "Perdagangan",
        "share_lainnya": "Lainnya",
        "share_jasa_kemasyarakatan": "Jasa kemasyarakatan",
        "share_perikanan": "Perikanan",
        "share_jasa_pendidikan": "Jasa pendidikan",
        "share_sektor_lain_ref": "Sektor Gabungan",
    }
    significance = coefficient_summary[coefficient_summary["variable"].isin(variable_labels)].copy()
    significance["prediktor"] = significance["variable"].map(variable_labels)
    significance = significance.sort_values("significant_local_count_corrected", ascending=True)
    sig_fig = px.bar(
        significance,
        x="significant_local_count_corrected",
        y="prediktor",
        orientation="h",
        text="significant_local_count_corrected",
        title="Koefisien lokal signifikan (terkoreksi)",
        labels={
            "significant_local_count_corrected": "Jumlah desa/kelurahan",
            "prediktor": "",
        },
        color_discrete_sequence=[COLORS["accent"]],
    )
    st.plotly_chart(style_figure(sig_fig, 380), width="stretch")
    st.caption(
        "Jumlah di atas memakai flag signifikansi lokal terkoreksi; p-value tak "
        "terkoreksi tetap tersedia pada tabel parameter untuk audit."
    )
    with st.expander("Data signifikansi koefisien"):
        st.dataframe(
            significance,
            hide_index=True,
            width="stretch",
            column_config=table_columns(significance),
        )

    map_options = {
        "Local R²": ("metric", "gwr_local_r2", "Viridis", None),
        "Local condition number": (
            "metric",
            "gwr_local_condition_number",
            "Blues",
            None,
        ),
        "Koefisien perdagangan": (
            "coefficient",
            "share_perdagangan",
            "RdBu",
            0.0,
        ),
        "Koefisien lainnya": (
            "coefficient",
            "share_lainnya",
            "RdBu",
            0.0,
        ),
        "Koefisien jasa kemasyarakatan": (
            "coefficient",
            "share_jasa_kemasyarakatan",
            "RdBu",
            0.0,
        ),
        "Koefisien perikanan": (
            "coefficient",
            "share_perikanan",
            "RdBu",
            0.0,
        ),
        "Koefisien jasa pendidikan": (
            "coefficient",
            "share_jasa_pendidikan",
            "RdBu",
            0.0,
        ),
        "Koefisien Sektor Gabungan": (
            "coefficient",
            "share_sektor_lain_ref",
            "RdBu",
            0.0,
        ),
    }
    st.subheader("Eksplorasi diagnostik & koefisien lokal")
    selected_map = st.selectbox("Peta teknis", list(map_options))
    map_kind, source_column, scale, midpoint = map_options[selected_map]
    if map_kind == "coefficient":
        local_map = params.loc[
            params["variable"] == source_column,
            [
                "kode_kd",
                "coefficient",
                "se",
                "t",
                "significant_local_corrected",
            ],
        ].copy()
        local_map["signifikansi"] = local_map["significant_local_corrected"].map(
            {True: "Signifikan (terkoreksi)", False: "Tidak signifikan"}
        )
        map_df = village.merge(local_map, on="kode_kd", how="left", validate="one_to_one")
        map_color = "coefficient"
        map_labels = {
            "coefficient": selected_map,
            "se": "Standard error",
            "t": "t-value",
            "signifikansi": "Status signifikansi",
            "gwr_local_r2": "Local R²",
            "gwr_local_condition_number": "Local condition number",
        }
        extra_hover = {
            "coefficient": ":.4f",
            "se": ":.4f",
            "t": ":.3f",
            "signifikansi": True,
            "gwr_local_r2": ":.3f",
            "gwr_local_condition_number": ":.2f",
            "significant_local_corrected": False,
        }
    else:
        map_df = village
        map_color = source_column
        map_labels = {source_column: selected_map}
        extra_hover = {
            "gwr_local_r2": ":.3f",
            "gwr_local_condition_number": ":.2f",
        }
    classification_df = map_df
    if map_kind == "coefficient":
        only_significant = st.toggle(
            "Hanya lokasi signifikan (terkoreksi)",
            key="gwr_significant_only",
            help="Menggunakan flag koreksi multiple testing, bukan p-value lokal tak terkoreksi.",
        )
        if only_significant:
            map_df = map_df[map_df["significant_local_corrected"]]
        st.caption(f"{len(map_df)} dari {len(village)} desa/kelurahan ditampilkan.")
    if map_df.empty:
        st.info("Tidak ada lokasi dengan koefisien signifikan setelah koreksi untuk variabel ini.")
    else:
        st.plotly_chart(
            choropleth(
                map_df,
                geojson,
                map_color,
                selected_map,
                color_scale=scale,
                midpoint=midpoint,
                labels=map_labels,
                extra_hover_data=extra_hover,
                classification_df=classification_df,
            ),
            width="stretch",
        )
    if map_kind == "coefficient":
        st.caption(
            "Koefisien share pada peta dibaca relatif terhadap `share_pertanian` "
            "sebagai reference category. Tooltip memuat coefficient, standard error, "
            "t-value, status signifikansi terkoreksi, local R², dan local condition "
            "number."
        )
    with st.expander("Tabel alternatif peta teknis"):
        if map_kind == "coefficient":
            map_table = map_df[
                [
                    "kel_desa",
                    "kecamatan",
                    "coefficient",
                    "se",
                    "t",
                    "signifikansi",
                    "gwr_local_r2",
                    "gwr_local_condition_number",
                ]
            ].sort_values("coefficient", ascending=False)
        else:
            metric_columns = list(
                dict.fromkeys(
                    [
                        "kel_desa",
                        "kecamatan",
                        source_column,
                        "TPT_Proxy",
                        "gwr_local_r2",
                        "gwr_local_condition_number",
                    ]
                )
            )
            map_table = map_df[metric_columns].sort_values(source_column, ascending=False)
        st.dataframe(
            map_table,
            width="stretch",
            hide_index=True,
            column_config=table_columns(map_table),
        )

    st.subheader("Parameter lokal per desa")
    village_labels = village.assign(
        _label=village["kel_desa"] + " — " + village["kecamatan"]
    ).sort_values(["kecamatan", "kel_desa"])[["kode_kd", "_label"]]
    requested_code = str(st.query_params.get("kode_kd", ""))
    code_list = village_labels["kode_kd"].astype(str).tolist()
    default_index = code_list.index(requested_code) if requested_code in code_list else 0
    selected_label = st.selectbox(
        "Desa/kelurahan",
        village_labels["_label"].tolist(),
        index=default_index,
    )
    code = village_labels.loc[village_labels["_label"] == selected_label, "kode_kd"].iloc[0]
    local = params[params["kode_kd"] == code].copy()
    local["signifikansi"] = local["significant_local_corrected"].map(
        {True: "Signifikan (terkoreksi)", False: "Tidak signifikan"}
    )
    st.dataframe(
        local[
            [
                "variable",
                "coefficient",
                "se",
                "t",
                "p_value_unadjusted",
                "signifikansi",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config=table_columns(local),
    )
    selected_village = village[village["kode_kd"] == code].iloc[0]
    m1, m2, m3 = st.columns(3)
    m1.metric("Local R²", num(selected_village["gwr_local_r2"], 3))
    m2.metric("Local condition number", num(selected_village["gwr_local_condition_number"], 2))
    m3.metric("TPT", pct(selected_village["TPT_Proxy"]))
    st.caption(
        "P-value pada tabel adalah p-value lokal tak terkoreksi. Keputusan "
        "signifikansi menggunakan critical t terkoreksi untuk multiple testing."
    )

    with st.expander("Metodologi dan batas interpretasi", expanded=True):
        st.markdown(
            f"""
            - Unit analisis: **328 desa/kelurahan**; primary key `kode_kd`.
            - Outcome: **TPT** = penganggur / (penganggur + penduduk bekerja);
              dihitung dari data administratif dan bukan TPT resmi BPS.
            - OLS dipakai sebagai baseline global; GWR utama memakai kernel
              **Gaussian adaptive** dengan bandwidth **43 tetangga**.
            - `share_pertanian` adalah **reference category**, sehingga koefisien
              share dibaca relatif terhadap pertanian.
            - Moran's I residual GWR = **{spatial_summary["gwr_residual_moran"]["I"]:.4f}**
              dengan p = **{spatial_summary["gwr_residual_moran"]["p_sim"]:.3f}**.
            - Local condition number berada pada rentang
              **{spatial_summary["gwr_local_collinearity"]["condition_number_min"]:.2f}–{spatial_summary["gwr_local_collinearity"]["condition_number_max"]:.2f}**;
              tidak ada lokasi >30.
            - Koordinat/geometri dipakai untuk bobot dan jarak spasial, bukan
              sebagai prediktor substantif.
            - Dashboard membaca artefak model yang sudah dihitung sebelumnya;
              model tidak di-fit ulang ketika halaman dibuka.
            """
        )
