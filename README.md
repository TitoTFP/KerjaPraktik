# Laporan Kerja Praktik: Data Pengangguran Kabupaten Tuban

Repositori untuk analisis deskriptif dan penyusunan laporan kerja praktik menggunakan data pengangguran Kabupaten Tuban.
CSV sumber yang dipakai loader dan berkas batas wilayah GeoJSON disertakan di `Datasets/`: `Data_Pengangguran_Clean_Audited_8_Sep_2026.csv` dan `Kabupaten Tuban-KEL_DESA.geojson`. Unit tests tidak memerlukan CSV.

## Mulai cepat

Prasyarat: Python 3.12 atau lebih baru dan [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync
```

## Menulis laporan

Laporan kerja praktik disusun sebagai Quarto Book dengan satu berkas `.qmd` per bab: `laporan/index.qmd` berisi Bab I (nama `index.qmd` diperlukan oleh Quarto Book), lalu `bab-02-gambaran-umum.qmd` sampai `bab-05-penutup.qmd`. Berkas hanya mencakup Bab I–V; halaman awal, daftar pustaka, dan lampiran dari sumber DOCX tidak disertakan. Quarto merender HTML dan Word; DOCX gabungan tersimpan di `laporan/_output/laporan.docx`. Quarto menyertakan Pandoc untuk konversi dan sitasi. Siapkan Zotero serta Better BibTeX untuk ekspor referensi ke `laporan/references.bib`.

```bash
quarto check
quarto render laporan
```

Lihat [panduan Quarto, Pandoc, dan Zotero](docs/panduan-referensi.md) untuk instalasi, ekspor otomatis, gaya sitasi, dan format kutipan.

## Pemeriksaan lokal

```bash
uv run pytest
uv run ruff check src tests
# Opsional; memerlukan Quarto
quarto render laporan
```

## Struktur

```text
.
├── .github/                  # workflow CI dan templat kontribusi GitHub
├── Datasets/                 # CSV sumber dan batas wilayah GeoJSON
├── docs/                     # panduan referensi, kamus data, dan kerangka laporan
├── laporan/                  # proyek Quarto, dokumen .qmd, dan ekspor references.bib
├── src/laporan_kerja_praktik/ # loader dan agregasi yang dapat digunakan ulang
├── tests/                    # uji perilaku loader dan agregasi
├── pyproject.toml            # metadata, dependensi, dan konfigurasi Python
└── uv.lock                   # lockfile dependensi
```

Data analisis berada di `Datasets/`. Jangan menimpa berkas sumber saat membersihkan atau menganalisis data; simpan perubahan analisis di kode proyek.

## Git dan GitHub

Direktori kerja ini sudah merupakan repositori Git lokal. Berkas `.gitignore`, `.gitattributes`, workflow, dan templat GitHub disediakan. Untuk publikasi, buat repositori GitHub kosong, tambahkan URL remote yang diberikan GitHub, lalu push branch kerja. Sebelum repositori dibuat publik, pastikan izin distribusi dan atribusi data telah dipenuhi. Belum ada lisensi proyek karena pemegang hak belum ditetapkan.

## Dokumentasi laporan

- [Kerangka laporan kerja praktik](docs/kerangka-laporan.md)
- [Kamus data dan catatan interpretasi](docs/kamus-data.md)
- [Panduan Quarto, Pandoc, dan Zotero](docs/panduan-referensi.md)
- [Panduan kontribusi](CONTRIBUTING.md)
