# Laporan Kerja Praktik: Data Pengangguran Kabupaten Tuban

Repositori untuk analisis deskriptif dan penyusunan laporan kerja praktik menggunakan data pengangguran Kabupaten Tuban.
CSV sumber yang dipakai loader dan berkas batas wilayah GeoJSON disertakan di `Datasets/`: `Data_Pengangguran_Clean_Audited_8_Sep_2026.csv` dan `Kabupaten Tuban-KEL_DESA.geojson`. Unit tests tidak memerlukan CSV.

## Mulai cepat

Prasyarat: Python 3.12 atau lebih baru dan [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync
```

## Menulis laporan

Laporan kerja praktik disusun sebagai Quarto Book dengan `laporan/index.qmd` sebagai halaman awal (wajib untuk buku Quarto) dan Bab I–V di `laporan/bab/`, dari `bab-01-pendahuluan.qmd` sampai `bab-05-penutup.qmd`. Berkas hanya mencakup Bab I–V; bagian halaman awal, daftar pustaka, dan lampiran dari DOCX sumber tidak disertakan. Quarto merender HTML dan Word; DOCX gabungan tersimpan di `laporan/_output/laporan.docx`. Quarto menyertakan Pandoc untuk konversi dan sitasi. Siapkan Zotero serta Better BibTeX untuk ekspor referensi ke `laporan/references.bib`.

```bash
quarto check
quarto render laporan
```

Lihat [panduan Quarto, Pandoc, dan Zotero](docs/panduan-referensi.md) untuk instalasi, ekspor otomatis, gaya sitasi, dan format kutipan.

## Reproduksi aset Bab IV

Empat belas gambar analisis Bab IV (Gambar 4.1–4.14) dibuat ulang dari CSV pengangguran dan GeoJSON batas desa di `Datasets/`, termasuk peta Gambar 4.3–4.5, 4.9, dan 4.11 serta tiga plot korelasi Spearman Gambar 4.12–4.14. Pada Gambar 4.14, enam kategori mengikuti nama di Tabel 3.3; X6 ditampilkan sebagai “Sektor Gabungan”. Lima tangkapan layar bagian 4.7 Dashboard tetap menggunakan `laporan/docx-media/media/image13.png`–`image17.png` dan tidak dibuat ulang oleh generator.

```bash
uv run python scripts/generate_bab4_assets.py
quarto render laporan
```

Generator menulis empat belas gambar analisis ke `laporan/assets/bab-04/`. Peta 4.3, 4.5, 4.9, dan 4.11 memakai kelas *Natural Breaks* dan label desa dari kolom `fid` CSV; peta 4.4 memakai label nama kecamatan dan TPT agregat berbobot angkatan kerja. Peta 4.5 berupa satu peta Kabupaten Tuban: enam kecamatan dengan TPT agregat tertinggi diwarnai menurut TPT desa/kelurahan, dibagi menurut batas desa, dan diberi label fid numerik; 14 kecamatan lain ditampilkan abu-abu. Batas kelas warna TPT desa dihitung dari seluruh dataset agar konsisten dengan peta 4.3. Gambar 4.12–4.14 menampilkan korelasi Spearman TPT dengan jumlah penganggur menurut pendidikan dan kesehatan; Gambar 4.14 menampilkan enam kelompok pekerjaan, dengan X6/Sektor Gabungan sebagai agregat sembilan kategori yang juga digunakan dalam model. Pertanian Padi & Palawija menjadi kategori referensi. *P-value* dikoreksi Holm per gambar. Batas kecamatan digabung dari geometri desa pada GeoJSON yang disediakan. Tangkapan layar Dashboard tetap bersumber dari `laporan/docx-media/`.

## Streamlit dashboard

Dashboard Streamlit memakai artefak pra-hitung di `dashboard_data/` dan GeoJSON di `Datasets/`; dashboard tidak menjalankan ulang analisis spasial atau model.

Ringkasan menampilkan indikator utama terlebih dahulu. Tabel rinci dan catatan metode dapat
dibuka sesuai kebutuhan; atribusi PDPM ITS dan kredit pengembang tersedia di semua halaman.

```bash
uv sync --extra dashboard
uv run --extra dashboard streamlit run app.py
```

Untuk mengaktifkan skill Streamlit di lingkungan lokal, jalankan
`uv run --extra dashboard streamlit skills --yes`. Skill ini mengikuti versi Streamlit
proyek. Audit visual memakai [Unslop](https://github.com/heydamir/unslop) karya
Damir Sokolovsky (CC BY 4.0), di `.agents/skills/unslop/`, dari revisi `620163e`.

## Deployment systemd

Dua unit contoh ada di `deploy/systemd/`: `tuban-dashboard.service` menjalankan dashboard pada `127.0.0.1:8501` dan `cloudflared-tunnel.service` meneruskannya lewat Cloudflare Tunnel. Keduanya mengasumsikan aplikasi terpasang di `/opt/tuban-dashboard` serta user sistem `tuban-dashboard` dan `cloudflared` sudah dibuat.

```bash
sudo useradd --system --home /var/lib/tuban-dashboard --shell /usr/sbin/nologin tuban-dashboard
sudo install -d -o tuban-dashboard -g tuban-dashboard /opt/tuban-dashboard
# salin isi repositori ke /opt/tuban-dashboard/current, lalu bangun venv di lokasi unit
# (shebang skrip venv mengunci path, jadi bangun langsung di tujuan, bukan dipindah):
sudo UV_PROJECT_ENVIRONMENT=/opt/tuban-dashboard/.venv uv sync --locked --extra dashboard \
  --project /opt/tuban-dashboard/current
sudo chown -R tuban-dashboard:tuban-dashboard /opt/tuban-dashboard
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tuban-dashboard.service cloudflared-tunnel.service
```

Token tunnel dibaca dari `/etc/cloudflared/tunnel-token` (tidak dilacak Git); buat berkas itu dengan izin baca hanya untuk user `cloudflared` sebelum unit dijalankan. `StateDirectory` membuat `/var/lib/tuban-dashboard` dan `/var/lib/cloudflared` otomatis dengan mode `0750`.

## Pemeriksaan lokal

```bash
uv run pytest
uv run ruff check src tests scripts
# Opsional; memerlukan Quarto
quarto render laporan
```

## Struktur

```text
.
├── .github/                  # workflow CI dan templat GitHub
├── .streamlit/               # konfigurasi tampilan Streamlit
├── Datasets/                 # CSV sumber dan batas wilayah GeoJSON
├── dashboard/                # halaman, loader data, dan UI Streamlit
├── dashboard_data/           # artefak pra-hitung yang dipakai dashboard
├── deploy/systemd/           # unit systemd dashboard dan Cloudflare Tunnel
├── docs/                     # panduan referensi, kamus data, dan kerangka laporan
├── laporan/                  # Quarto Book
├── src/laporan_kerja_praktik/ # loader dan agregasi yang dapat digunakan ulang
├── tests/                    # uji perilaku loader dan agregasi
├── app.py                    # entry point dashboard
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
