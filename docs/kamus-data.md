# Kamus Data

Sumber kerja: `Datasets/Data_Pengangguran_Clean_Audited_8_Sep_2026.csv`. Skema berikut dikelompokkan menurut nama kolom; konfirmasi definisi, satuan, periode rujukan, dan sumber kepada pemilik data sebelum menafsirkan hasil.

| Kelompok | Kolom |
| --- | --- |
| Identitas wilayah | `fid`, `ori_name`, `kode_kec`, `kode_kd`, `kode_kk`, `kode_prov`, `tipe_kd`, `kecamatan`, `kel_desa`, `kab_kota`, `provinsi`, `jenis_kd`, `nama`, `label`, `key_join`, `KECAMATAN_2`, `Desa`, `key_join_2`, `KECAMATAN_3`, `Desa_2`, `key_join_3`, `No.`, `Nama Kecamatan`, `Kode Kec`, `Kode Desa`, `Nama Desa`, `Kecamatan_4`, `Desa_3`, `key_join_4` |
| Kesehatan | `Tidak Ada`, `Asma`, `Diabetes`, `Hipertensi`, `Kanker/Tumor Ganas`, `Kolesterol`, `Gagal Ginjal`, `Leukimia`, `Masalah Jantung`, `Rematik`, `Stroke`, `TBC`, `Thalasemia`, `Sirosis Hati`, `HIV/AIDS`, `Alzheimer`, `Haemophilia`, `Lainnya`, `#N/A`, `Total` |
| Pendidikan | `D1/D2/D3`, `D4/S1`, `MA`, `MAK`, `MI`, `MTs`, `Paket A`, `Paket B`, `Paket C`, `Profesi`, `S2`, `S3`, `SD`, `SDLB`, `SMA`, `SMK`, `SMLB`, `SMP`, `SMP LB`, `SPM/PDF Ula`, `SPM/PDF Ulya`, `SPM/PDF Wustha`, `Tidak Punya Ijazah SD` |
| Lapangan pekerjaan | `Bangunan/Konstruksi`, `Hotel & Rumah Makan`, `Industri Pengolahan`, `Informasi & Komunikasi`, `Jasa Kemasyarakatan, Pemerintah, Dan Perorangan`, `Jasa Kesehatan`, `Jasa Pendidikan`, `Keuangan & Asuransi`, `Lainnya_2`, `Listrik Dan Gas`, `Perdagangan`, `Perikanan`, `Pertanian Padi & Palawija`, `Peternakan`, `Transportasi & Pergudangan` |
| Jumlah agregat | `Total_Penduduk_Bekerja`, `Total_Penganggur` |
| Pemeriksaan kualitas | `QC_Penyakit_Total`, `QC_Partisi_Penganggur`, `Unknown_Penyakit`, `QC_Kode_Unik`, `QC_Nama_Alias`, `QC_KeyJoin_Unik`, `QC_KeyJoin_Blok` |

## Catatan interpretasi

- Kode administrasi dipertahankan sebagai teks agar tidak diperlakukan sebagai bilangan; jangan menghapus tanda titik atau nol awal.
- `#N/A` adalah nama kolom yang muncul pada berkas sumber. Maknanya tidak ditetapkan di sini; jangan gunakan sebagai indikator tanpa klarifikasi.
- Kolom dengan akhiran seperti `_2`, `_3`, dan `_4` tetap dipertahankan agar skema sumber tidak berubah. Pastikan asal dan fungsi tiap kolom sebelum menggabungkan atau memilih salah satunya.
- Kolom `QC_*` merupakan penanda pemeriksaan, bukan jumlah penduduk. Laporkan hasil QC terpisah dari indikator substantif.
- `Total_Penganggur` dan `Total_Penduduk_Bekerja` adalah hitungan pada sumber. Jangan menyebut rasio atau tingkat pengangguran tanpa definisi denominator yang telah dikonfirmasi.
