# Panduan Kontribusi

## Alur kerja

1. Buat branch terpisah untuk perubahan analisis atau dokumentasi.
2. Jangan mengubah atau menimpa CSV sumber; tulis transformasi di kode/notebook baru dan jelaskan aturan pembersihannya.
3. Perbarui dokumentasi bila definisi indikator, sumber, atau metode berubah.
4. Jalankan pemeriksaan sebelum membuka pull request:

   ```bash
   uv sync
   uv run pytest
   uv run ruff check src tests
   if test -f Datasets/Data_Pengangguran_Clean_Audited_8_Sep_2026.csv; then
       uv run jupyter nbconvert --to notebook --execute --output-dir /tmp notebooks/01_eksplorasi_data.ipynb notebooks/02_tabel_variabel.ipynb
   else
       echo "Eksekusi notebook dilewati: CSV sumber tidak tersedia."
   fi
   ```

5. Pada pull request, jelaskan pertanyaan analisis, metode, perubahan visualisasi, serta keterbatasan data.

## Notebook

- Jalankan notebook dari lingkungan proyek (`uv run jupyter lab`).
- Gunakan nama kolom sumber apa adanya atau dokumentasikan pemetaan nama yang dipakai.
- Hindari klaim kausal dari ringkasan deskriptif.
- Hapus output sel yang besar atau memuat data sensitif sebelum commit.
- Simpan grafik dengan label, satuan, dan keterangan sumber yang jelas.
