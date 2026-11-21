# Reproduksi Aset Bab IV

Generator membuat ulang 14 gambar analisis (Gambar 4.1–4.14) dari CSV pengangguran dan GeoJSON batas desa/kelurahan di [`Datasets/`](../Datasets/). Lima tangkapan layar dashboard pada Bagian 4.7 (`image13.png`–`image17.png`) tetap menggunakan aset dari [`laporan/docx-media/media/`](../laporan/docx-media/media/) dan tidak dibuat ulang oleh generator.

## Menjalankan generator

Dari root repositori, dengan Python 3.12+ dan [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync --locked
uv run --locked python scripts/generate_bab4_assets.py
```

Generator memperbarui PNG yang dilacak Git di [`laporan/assets/bab-04/`](../laporan/assets/bab-04/). Untuk memasukkan perubahan gambar ke laporan, jalankan `quarto render laporan` (lihat [panduan render](panduan-referensi.md#mengutip-dan-merender)).

## Catatan metode

- Gambar 4.3, 4.5, 4.9, dan 4.11 memakai klasifikasi *Natural Breaks* dan label desa dari kolom `fid` CSV. Batas kecamatan dibentuk dari gabungan geometri desa pada GeoJSON.
- Gambar 4.4 memakai nama kecamatan dan TPT agregat berbobot angkatan kerja. Gambar 4.5 mewarnai desa/kelurahan di enam kecamatan dengan TPT agregat tertinggi; 14 kecamatan lain ditampilkan abu-abu. Batas kelas TPT desa dihitung dari seluruh dataset agar konsisten dengan Gambar 4.3.
- Gambar 4.12–4.14 menampilkan korelasi Spearman TPT dengan jumlah penganggur menurut pendidikan, kesehatan, dan lapangan pekerjaan. *P-value* dikoreksi dengan metode Holm per gambar.
- Enam kelompok pekerjaan di Gambar 4.14 mengikuti Tabel 3.3. X6 ditampilkan sebagai **Sektor Gabungan**, agregat sembilan kategori yang juga digunakan dalam model. Pertanian Padi & Palawija menjadi kategori referensi.

Lihat [Bab IV — Hasil dan Pembahasan](../laporan/bab/bab-04-hasil.qmd) untuk interpretasi gambar.
