# Panduan Kontribusi

## Alur kerja

1. Buat branch terpisah untuk perubahan analisis atau dokumentasi.
2. Jangan mengubah atau menimpa CSV sumber; tulis transformasi di kode dan jelaskan aturan pembersihannya.
3. Perbarui dokumentasi bila definisi indikator, sumber, atau metode berubah.
4. Jalankan pemeriksaan sebelum membuka pull request:

   ```bash
   uv sync
   uv run pytest
   uv run ruff check src tests
   ```

   Jika Quarto terpasang, verifikasi render laporan dengan `quarto render laporan`.
5. Pada pull request, jelaskan pertanyaan analisis, metode, perubahan visualisasi, serta keterbatasan data.

## Analisis data

- Gunakan nama kolom sumber apa adanya atau dokumentasikan pemetaan nama yang dipakai.
- Hindari klaim kausal dari ringkasan deskriptif.
- Simpan visualisasi dengan label, satuan, dan keterangan sumber yang jelas.

## Laporan dan sitasi

- Struktur laporan Quarto berada di `laporan/`; panduan instalasi dan ekspor Zotero ada di [Panduan Quarto, Pandoc, dan Zotero](docs/panduan-referensi.md).
- `laporan/references.bib` adalah ekspor Better BibTeX yang dilacak Git. Perbarui ekspor otomatis setelah mengubah pustaka sumber.
