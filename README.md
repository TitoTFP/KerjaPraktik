# Laporan Kerja Praktik: Data Pengangguran Kabupaten Tuban

Repositori untuk analisis deskriptif dan penyusunan laporan kerja praktik menggunakan data pengangguran Kabupaten Tuban.
Notebook membutuhkan `Datasets/Data_Pengangguran_Clean_Audited_8_Sep_2026.csv`; berkas data tidak disertakan dalam commit scaffold. Letakkan salinannya di path tersebut sebelum menjalankan notebook. Pastikan izin distribusi sebelum memasukkan data ke remote. Unit tests tidak memerlukan CSV; CI mengeksekusi notebook hanya jika CSV tersedia.

## Mulai cepat

Prasyarat: Python 3.12 atau lebih baru dan [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync
uv run jupyter lab
```

Buka `notebooks/01_eksplorasi_data.ipynb` untuk eksplorasi dan `notebooks/02_tabel_variabel.ipynb` untuk tabel definisi variabel. Notebook kedua merender tiga DataFrame langsung di output Jupyter agar bisa dipilih dan disalin; tidak ada file tabel/gambar terpisah.

## Pemeriksaan lokal

```bash
uv run pytest
uv run ruff check src tests
# Opsional; memerlukan CSV sumber di Datasets/
uv run jupyter nbconvert --to notebook --execute --output-dir /tmp notebooks/01_eksplorasi_data.ipynb notebooks/02_tabel_variabel.ipynb
```

## Struktur

```text
.
├── .github/                  # workflow CI dan templat kontribusi GitHub
├── Datasets/                 # lokasi lokal opsional untuk CSV sumber
├── docs/                     # kamus data dan kerangka laporan
├── notebooks/                # analisis Jupyter
├── src/laporan_kerja_praktik/ # loader dan agregasi yang dapat digunakan ulang
├── tests/                    # uji perilaku loader dan agregasi
├── pyproject.toml            # metadata, dependensi, dan konfigurasi Python
└── uv.lock                   # lockfile dependensi
```

CSV adalah sumber analisis notebook. Jangan menimpa dataset sumber saat membersihkan atau menganalisis data. Simpan perubahan analisis di notebook atau kode terpisah.

## Git dan GitHub

Direktori kerja ini sudah merupakan repositori Git lokal. Berkas `.gitignore`, `.gitattributes`, workflow, dan templat GitHub disediakan. Untuk publikasi, buat repositori GitHub kosong, tambahkan URL remote yang diberikan GitHub, lalu push branch kerja. Sebelum repositori dibuat publik, pastikan izin distribusi dan atribusi data telah dipenuhi. Belum ada lisensi proyek karena pemegang hak belum ditetapkan.

## Dokumentasi laporan

- [Kerangka laporan kerja praktik](docs/kerangka-laporan.md)
- [Kamus data dan catatan interpretasi](docs/kamus-data.md)
- [Panduan kontribusi](CONTRIBUTING.md)
