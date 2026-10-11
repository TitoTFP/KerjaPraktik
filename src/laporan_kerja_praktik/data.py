"""Loading and summarizing the audited Tuban unemployment dataset."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "Datasets" / "Data_Pengangguran_Clean_Audited_8_Sep_2026.csv"
REQUIRED_COLUMNS = (
    "kecamatan",
    "kel_desa",
    "kode_kec",
    "kode_kd",
    "Total_Penganggur",
    "Total_Penduduk_Bekerja",
)
IDENTIFIER_COLUMNS = ("kode_kec", "kode_kd", "kode_kk")


def load_dataset(path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Read the CSV and retain administrative codes as text.

    Args:
        path: CSV path. Defaults to the expected file under the project-root
            ``Datasets/`` directory.

    Raises:
        FileNotFoundError: If ``path`` does not point to a file.
        ValueError: If a column required by the report is missing.
    """
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_path}")

    data = pd.read_csv(dataset_path, dtype={column: "string" for column in IDENTIFIER_COLUMNS})
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")
    return data


def summarize_by_district(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate working and unemployed counts by ``kecamatan``.

    This reports counts from the source columns; it does not infer causes or rates.
    """
    columns = ("kecamatan", "Total_Penganggur", "Total_Penduduk_Bekerja")
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Kolom wajib untuk agregasi tidak ditemukan: {', '.join(missing)}")

    return (
        data.groupby("kecamatan", as_index=False, dropna=False)
        .agg(
            Total_Penganggur=("Total_Penganggur", "sum"),
            Total_Penduduk_Bekerja=("Total_Penduduk_Bekerja", "sum"),
        )
        .sort_values("Total_Penganggur", ascending=False)
        .reset_index(drop=True)
    )
