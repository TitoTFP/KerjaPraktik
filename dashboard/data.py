from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_OUTPUT = ROOT / "dashboard_data" / "dashboard_insights_non_regresi"
SPATIAL_OUTPUT = ROOT / "dashboard_data" / "spatial_analysis"
GEOJSON_PATH = ROOT / "Datasets" / "Kabupaten Tuban-KEL_DESA.geojson"

SECTOR_GROUPS = {
    "Pertanian": ["Pertanian Padi & Palawija", "Peternakan", "Perikanan"],
    "Industri dan Konstruksi": [
        "Industri Pengolahan",
        "Bangunan/Konstruksi",
        "Listrik Dan Gas",
    ],
    "Perdagangan dan Akomodasi": ["Perdagangan", "Hotel & Rumah Makan"],
    "Jasa": [
        "Informasi & Komunikasi",
        "Jasa Kemasyarakatan, Pemerintah, Dan Perorangan",
        "Jasa Kesehatan",
        "Jasa Pendidikan",
        "Keuangan & Asuransi",
        "Lainnya_2",
        "Transportasi & Pergudangan",
    ],
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"kode_kd": "string", "kode_kec": "string"})


def _add_sector_groups(village: pd.DataFrame) -> pd.DataFrame:
    village = village.copy()
    denominator = village["Total_Penduduk_Bekerja"].replace(0, pd.NA)
    for label, columns in SECTOR_GROUPS.items():
        village[label] = village[columns].sum(axis=1)
        village[f"share_{label}"] = village[label] / denominator
    share_columns = [f"share_{label}" for label in SECTOR_GROUPS]
    village["sektor_dominan"] = (
        village[share_columns].idxmax(axis=1).str.replace("share_", "", regex=False)
    )
    return village


@st.cache_data(show_spinner=False)
def load_bundle() -> dict[str, object]:
    village = _add_sector_groups(_read_csv(DASHBOARD_OUTPUT / "village_rankings.csv"))
    clusters = _read_csv(DASHBOARD_OUTPUT / "spatial_clusters.csv")
    model = _read_csv(SPATIAL_OUTPUT / "modeling_results.csv")

    cluster_columns = [
        "kode_kd",
        "local_cluster_tpt_proxy",
        "local_cluster_pendidikan_rendah",
        "local_cluster_penyakit_kronis",
        "education_priority_quadrant",
        "disease_priority_quadrant",
        "local_moran_tpt_proxy_p_adj",
        "local_moran_pendidikan_rendah_p_adj",
        "local_moran_penyakit_kronis_p_adj",
    ]
    village = village.merge(
        clusters[cluster_columns], on="kode_kd", how="left", validate="one_to_one"
    )

    model_columns = [
        "kode_kd",
        "gwr_local_r2",
        "gwr_local_condition_number",
        "gwr_residual",
        "ols_residual",
        *[column for column in model.columns if column.startswith("gwr_coef_")],
    ]
    village = village.merge(model[model_columns], on="kode_kd", how="left", validate="one_to_one")

    with (DASHBOARD_OUTPUT / "dashboard_insight_summary.json").open(encoding="utf-8") as handle:
        dashboard_summary = json.load(handle)
    with (SPATIAL_OUTPUT / "summary.json").open(encoding="utf-8") as handle:
        spatial_summary = json.load(handle)
    with GEOJSON_PATH.open(encoding="utf-8") as handle:
        geojson = json.load(handle)

    if len(village) != 328 or village["kode_kd"].nunique() != 328:
        raise ValueError("Dashboard membutuhkan tepat 328 kode_kd unik pada village_rankings.csv.")
    required_complete = [
        "TPT_Proxy",
        "Total_Penganggur",
        "Angkatan_Kerja",
        "local_cluster_tpt_proxy",
        "education_priority_quadrant",
        "disease_priority_quadrant",
        "gwr_local_r2",
        "gwr_local_condition_number",
    ]
    missing_after_join = village[required_complete].isna().sum()
    if int(missing_after_join.sum()) != 0:
        details = ", ".join(
            f"{column}={int(count)}" for column, count in missing_after_join.items() if count
        )
        raise ValueError(f"Artefak dashboard tidak lengkap setelah join: {details}")

    geo_codes = {
        str(feature.get("properties", {}).get("kode_kd", ""))
        for feature in geojson.get("features", [])
    }
    village_codes = set(village["kode_kd"].astype(str))
    if geo_codes != village_codes:
        raise ValueError(
            "Coverage kode_kd GeoJSON tidak sama dengan tabel dashboard 328 desa/kelurahan."
        )

    return {
        "village": village,
        "kecamatan": _read_csv(DASHBOARD_OUTPUT / "kecamatan_summary.csv"),
        "education_overall": _read_csv(DASHBOARD_OUTPUT / "education_overall_profile.csv"),
        "education_village": _read_csv(DASHBOARD_OUTPUT / "education_village_profiles.csv"),
        "education_kecamatan": _read_csv(DASHBOARD_OUTPUT / "education_kecamatan_summary.csv"),
        "education_quadrants": _read_csv(DASHBOARD_OUTPUT / "education_quadrant_summary.csv"),
        "disease_overall": _read_csv(DASHBOARD_OUTPUT / "disease_overall_profile.csv"),
        "disease_detail": _read_csv(DASHBOARD_OUTPUT / "disease_detail_profile.csv"),
        "disease_village": _read_csv(DASHBOARD_OUTPUT / "disease_village_profiles.csv"),
        "disease_kecamatan": _read_csv(DASHBOARD_OUTPUT / "disease_kecamatan_summary.csv"),
        "disease_quadrants": _read_csv(DASHBOARD_OUTPUT / "disease_quadrant_summary.csv"),
        "profile_by_rate": _read_csv(DASHBOARD_OUTPUT / "profile_by_rate_group.csv"),
        "quadrants": _read_csv(DASHBOARD_OUTPUT / "quadrant_summary.csv"),
        "moran": _read_csv(DASHBOARD_OUTPUT / "spatial_moran_summary.csv"),
        "cluster_summary": _read_csv(DASHBOARD_OUTPUT / "local_cluster_summary.csv"),
        "model_comparison": _read_csv(SPATIAL_OUTPUT / "model_comparison.csv"),
        "gwr_kernels": _read_csv(SPATIAL_OUTPUT / "gwr_kernel_comparison.csv"),
        "gwr_coefficients": _read_csv(SPATIAL_OUTPUT / "gwr_local_coefficient_summary.csv"),
        "gwr_parameters": _read_csv(SPATIAL_OUTPUT / "gwr_local_parameters.csv"),
        "dashboard_summary": dashboard_summary,
        "spatial_summary": spatial_summary,
        "geojson": geojson,
    }


def weighted_sector_profile(village: pd.DataFrame) -> pd.DataFrame:
    denominator = float(village["Total_Penduduk_Bekerja"].sum())
    rows = []
    for label in SECTOR_GROUPS:
        total = float(village[label].sum())
        rows.append(
            {
                "sektor": label,
                "jumlah": total,
                "share": total / denominator if denominator else 0.0,
            }
        )
    return pd.DataFrame(rows)


def rate_group_sector_profile(village: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rate_group, group in village.groupby("rate_group", sort=False):
        denominator = float(group["Total_Penduduk_Bekerja"].sum())
        for label in SECTOR_GROUPS:
            total = float(group[label].sum())
            rows.append(
                {
                    "rate_group": rate_group,
                    "sektor": label,
                    "share": total / denominator if denominator else 0.0,
                }
            )
    return pd.DataFrame(rows)
