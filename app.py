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

st.caption("Data administratif · bukan TPT resmi BPS · bukan bukti sebab-akibat")
with st.expander("Tentang data", icon=":material/info:"):
    st.markdown(
        """
        - **Cakupan:** 328 desa/kelurahan Kabupaten Tuban, dipadankan lewat `kode_kd`.
        - **TPT administratif:** penganggur ÷ angkatan kerja (penganggur + penduduk
          bekerja), bukan TPT resmi BPS. TPT wilayah dihitung dari total,
          bukan rata-rata TPT desa.
        - **Profil:** pendidikan dan kesehatan menggambarkan penganggur, bukan
          seluruh penduduk atau penyebab TPT. Status kesehatan tidak diketahui
          dibedakan dari tidak adanya kondisi kronis tercatat.
        - **Prioritas:** kuadran memakai median kabupaten, bukan ambang kebijakan.
        - **Sumber:** hasil pra-hitung di `dashboard_data/` dan geometri di `Datasets/`.
        """
    )
st.caption(
    "**Dikembangkan oleh:** Daffa Dzaky Mumtaz dan Tito Fauzan Putra\\\n"
    "**Proyek Kerja Praktik di:** Pusat Studi Potensi Daerah dan Pemberdayaan "
    "Masyarakat (PDPM ITS), 2026"
)
