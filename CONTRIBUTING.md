# Panduan Kontribusi

## Alur kerja

1. Untuk perubahan besar pada data, metode, atau indikator, diskusikan usulan melalui [GitHub Issues](https://github.com/TitoTFP/KerjaPraktik/issues).
2. Buat branch dari `main`. Jika tidak memiliki akses tulis, buat fork terlebih dahulu.
3. Jangan menimpa CSV sumber. Tulis transformasi di kode dan perbarui dokumentasi bila definisi indikator, sumber, atau metode berubah.
4. Jalankan pemeriksaan yang sama dengan [GitHub Actions](.github/workflows/quality.yml) dari root repositori:

   ```bash
   uv sync --locked
   uv run ruff check src tests
   uv run pytest
   ```

   Untuk perubahan laporan, jalankan juga `quarto render laporan`. Untuk perubahan dashboard, [jalankan aplikasi secara lokal](README.md#jalankan-dashboard) dan periksa halaman yang terdampak.
5. Buka pull request ke `main`. Ringkas perubahan dan cara memverifikasinya. Jika analisis berubah, jelaskan metode, dampak pada hasil, dan keterbatasan data.
   Jika melaporkan bug, sertakan langkah reproduksi serta hasil yang diharapkan dan diamati.

## Alat bantu pengembangan dashboard

- Skill Streamlit yang mengikuti versi proyek dapat dipasang secara lokal dengan `uv run --locked --extra dashboard streamlit skills --yes`.
- Audit visual menggunakan [Unslop](https://github.com/heydamir/unslop) karya Damir Sokolovsky (CC BY 4.0), disertakan di [`.agents/skills/unslop/`](.agents/skills/unslop/) dari revisi `620163e`.

## Analisis data

- Gunakan nama kolom sumber apa adanya atau dokumentasikan pemetaan nama yang dipakai.
- Hindari klaim kausal dari ringkasan deskriptif.
- Simpan visualisasi dengan label, satuan, dan keterangan sumber yang jelas.

## Laporan dan sitasi

- Struktur laporan Quarto berada di `laporan/`; panduan instalasi dan ekspor Zotero ada di [Panduan Quarto, Pandoc, dan Zotero](docs/panduan-referensi.md).
- `laporan/references.bib` adalah ekspor Better BibTeX yang dilacak Git. Perbarui ekspor otomatis setelah mengubah pustaka sumber.
