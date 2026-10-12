# Panduan Quarto, Pandoc, dan Zotero

## Perangkat

- [Quarto](https://quarto.org/docs/get-started/) untuk merender dokumen laporan ke HTML dan Word (`.docx`).
- Quarto menyertakan dan mengelola Pandoc untuk proses render dan sitasi. Tidak perlu memasang Pandoc terpisah untuk proyek ini; versi yang dipakai dapat dilihat dengan `quarto pandoc --version`.
- [Zotero](https://www.zotero.org/download/) dan add-on [Better BibTeX](https://retorque.re/zotero-better-bibtex/installation/) untuk mengelola referensi dan mengekspor berkas bibliografi. Zotero tidak harus berjalan saat Quarto merender laporan; `laporan/references.bib` sudah menjadi masukan render.

## Menyiapkan ekspor otomatis

1. Pasang Zotero Desktop dan add-on Better BibTeX.
2. Simpan sumber yang benar-benar digunakan ke sebuah koleksi Zotero untuk laporan ini. Periksa metadata bibliografi sebelum mengutipnya.
3. Di Zotero, klik kanan koleksi tersebut lalu pilih **Export Collection…**.
4. Pilih format **Better BibTeX**, centang **Keep updated**, lalu simpan sebagai `laporan/references.bib` di repositori ini. Setujui penggantian berkas awal jika diminta.
5. Simpan perubahan `references.bib` yang dihasilkan di Git. Zotero dan pengaturan ekspor otomatis bersifat lokal; berkas `.bib` itulah yang dibaca saat render.

Ekspor koleksi, bukan seluruh pustaka Zotero, agar bibliografi proyek hanya memuat sumber yang relevan. Jangan menambahkan data pribadi atau lampiran Zotero ke repositori.

## Mengutip dan merender

Gunakan citation key yang dibuat Better BibTeX di isi berkas `.qmd`, dengan sintaks Pandoc, misalnya `[@citation-key]` atau `[@citation-key, p. 10]`. Daftar pustaka dibuat dari sumber yang dikutip.

Dari direktori root repositori:

```bash
quarto check
quarto render laporan
```

Hasil HTML dan Word berada di `laporan/_output/` (diabaikan oleh Git). Pandoc bawaan Quarto memproses sitasi. Tanpa berkas CSL, gaya sitasi default Pandoc adalah Chicago author-date; jika pedoman kampus menentukan gaya lain, tambahkan berkas CSL ke `laporan/` dan atur `csl: nama-gaya.csl` di `laporan/_quarto.yml`.

Dokumentasi rujukan: [Quarto citations](https://quarto.org/docs/authoring/citations.html) dan [Better BibTeX automatic export](https://retorque.re/zotero-better-bibtex/exporting/auto/).
