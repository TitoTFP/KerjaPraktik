import pandas as pd
import pytest

from laporan_kerja_praktik import load_dataset, summarize_by_district


def test_load_dataset_keeps_administrative_codes_as_text(tmp_path):
    path = tmp_path / "codes.csv"
    path.write_text(
        "kode_kec,kode_kd,kode_kk,kecamatan,kel_desa,Total_Penganggur,Total_Penduduk_Bekerja\n"
        "35.23.17,35.23.17.2012,35.23,Plumpang,Bandungrejo,7,136\n",
        encoding="utf-8",
    )

    data = load_dataset(path)

    assert str(data["kode_kec"].dtype) == "string"
    assert str(data["kode_kd"].dtype) == "string"
    assert data.loc[0, "kode_kec"] == "35.23.17"
    assert data.loc[0, "kode_kd"] == "35.23.17.2012"


def test_load_dataset_rejects_missing_report_columns(tmp_path):
    path = tmp_path / "incomplete.csv"
    path.write_text("kecamatan,kel_desa\nTuban,Karang\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Kolom wajib tidak ditemukan"):
        load_dataset(path)


def test_district_summary_sums_counts_and_sorts_largest_first():
    data = pd.DataFrame(
        {
            "kecamatan": ["Bancar", "Tuban", "Bancar"],
            "Total_Penganggur": [2, 4, 3],
            "Total_Penduduk_Bekerja": [30, 60, 40],
        }
    )

    result = summarize_by_district(data)

    assert result.to_dict("records") == [
        {"kecamatan": "Bancar", "Total_Penganggur": 5, "Total_Penduduk_Bekerja": 70},
        {"kecamatan": "Tuban", "Total_Penganggur": 4, "Total_Penduduk_Bekerja": 60},
    ]


def test_district_summary_requires_count_columns():
    with pytest.raises(ValueError, match="Kolom wajib untuk agregasi tidak ditemukan"):
        summarize_by_district(pd.DataFrame({"kecamatan": ["Tuban"]}))
