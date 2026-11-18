from __future__ import annotations

import streamlit as st

from dashboard.pages import (
    render_explorer,
    render_gwr,
    render_overview,
    render_profiles,
    render_spatial,
)
from dashboard.ui import inject_css, render_sidebar

st.set_page_config(
    page_title="TPT Kabupaten Tuban",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="auto",
)
inject_css()
render_sidebar()

pages = {
    "Dashboard": [
        st.Page(
            render_overview, title="Ringkasan Kabupaten", icon=":material/dashboard:", default=True
        ),
        st.Page(render_explorer, title="Peta & Wilayah", icon=":material/map:"),
        st.Page(render_profiles, title="Profil & Prioritas", icon=":material/bar_chart:"),
        st.Page(render_spatial, title="Pola Spasial", icon=":material/hub:"),
    ],
    "Analisis teknis": [
        st.Page(render_gwr, title="GWR & Metodologi", icon=":material/functions:"),
    ],
}

navigation = st.navigation(pages)
navigation.run()

st.divider()
with st.expander("Tentang data & cara membaca dashboard", icon=":material/info:"):
    st.markdown(
        """
        - **Cakupan:** 328 desa/kelurahan Kabupaten Tuban, digabungkan melalui `kode_kd`.
        - **TPT:** penganggur ÷ (penganggur + penduduk bekerja). Data administratif,
          **bukan TPT resmi BPS**.
        - **Agregasi wilayah:** TPT tertimbang dihitung dari total penganggur ÷ total
          angkatan kerja, bukan rata-rata rate desa.
        - **Profil pendidikan dan kesehatan:** proporsi dari penganggur; bukan
          karakteristik seluruh penduduk atau bukti sebab-akibat. Kategori tidak
          diketahui tetap terpisah dari tidak ada penyakit.
        - **Kuadran prioritas:** median kabupaten sebagai cutoff eksploratif, bukan
          ambang kebijakan resmi.
        - **Sumber tampilan:** artefak pra-hitung di
          `dashboard_data/dashboard_insights_non_regresi/`,
          `dashboard_data/spatial_analysis/`, dan geometri di `Datasets/`.
          Tidak ada pemodelan ulang saat dashboard dibuka.
        """
    )
st.caption(
    "Kabupaten Tuban · Analisis tingkat desa/kelurahan · Interpretasi deskriptif, bukan kausal"
)
st.caption(
    "**Dikembangkan oleh:** Daffa Dzaky Mumtaz dan Tito Fauzan Putra\\\n"
    "**Proyek Kerja Praktik di:** Pusat Studi Potensi Daerah dan Pemberdayaan "
    "Masyarakat (PDPM ITS), 2026"
)
