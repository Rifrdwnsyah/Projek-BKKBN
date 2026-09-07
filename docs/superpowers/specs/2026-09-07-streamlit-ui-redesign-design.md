# Desain Ulang UI Streamlit Validasi Dokumen Kepegawaian

Tanggal: 7 September 2026

## Ringkasan

Aplikasi Streamlit akan didesain ulang dengan arah modern-minimalis, segar, profesional, dan berorientasi desktop. Nama yang ditampilkan adalah **Validasi Dokumen Kepegawaian**. Identitas visual tidak memakai logo, inisial "VD", atau kata "BKKBN".

Perubahan dibatasi pada presentasi antarmuka di `app.py`. Seluruh alur, state, aturan validasi, OCR, ekstraksi, similarity, penyimpanan pengajuan, dan keputusan admin harus tetap berfungsi sama seperti sebelum perubahan.

## Tujuan

- Meningkatkan hierarki visual dan keterbacaan aplikasi.
- Memanfaatkan lebar layar laptop secara efisien.
- Membuat alur unggah dan verifikasi lebih mudah dipindai.
- Menghilangkan tampilan emoji/ikon yang rusak atau tidak konsisten.
- Menjaga seluruh label isian dan pesan sistem tetap jelas.

## Di Luar Cakupan

- Perubahan fungsi pada `extractor.py`, `ocr.py`, `pipeline.py`, `rules.py`, atau `similarity.py`.
- Perubahan struktur data `st.session_state`.
- Penambahan autentikasi, basis data, pencarian, atau fitur bisnis baru.
- Perubahan aturan validasi maupun isi hasil pemeriksaan.
- Dukungan layout khusus ponsel; target utama adalah desktop/laptop.

## Arah Visual

### Palet warna

- Warna utama: `#4E9AD3`.
- Hover/aksen gelap: `#3D86BE`.
- Latar aksen lembut: `#EAF4FB`.
- Latar aplikasi: `#F5F8FB`.
- Permukaan kartu: `#FFFFFF`.
- Teks utama: `#17324D`.
- Teks sekunder: `#6F8194`.
- Garis/border: `#DFE8F0`.
- Status sukses, peringatan, dan gagal tetap memakai hijau, kuning, dan merah yang lembut agar maknanya tidak bergantung pada biru.

### Tipografi dan bentuk

- Gunakan font sistem modern: `Inter`, `Segoe UI`, `Arial`, sans-serif, tanpa ketergantungan unduhan font eksternal.
- Judul memakai bobot 700-800; teks isi memakai bobot 400-500.
- Radius kartu 12-16 px, input 8-10 px, dan tombol 8-10 px.
- Bayangan sangat ringan dan border tipis; tidak menggunakan efek dekoratif berlebihan.
- Ikon hanya berupa simbol sederhana yang aman dirender atau elemen CSS; tidak memakai emoji yang rawan tampil rusak.

## Kerangka Aplikasi

### Sidebar

- Sidebar putih dengan border kanan tipis.
- Bagian teratas hanya menampilkan teks **Validasi Dokumen Kepegawaian** tanpa logo atau inisial.
- Pilihan `Pegawai` dan `Admin` tetap menggunakan radio Streamlit yang sama, tetapi ditata seperti navigasi vertikal.
- Item aktif memakai latar `#EAF4FB`, teks biru, dan indikator garis `#4E9AD3`.

### Header halaman

- Header horizontal menggunakan warna `#4E9AD3` dengan teks putih.
- Tampilan Pegawai memakai judul konteks **Ruang Pengajuan**.
- Tampilan Admin memakai judul konteks **Ruang Verifikasi**.
- Tidak ada kata "BKKBN" di header, sidebar, maupun elemen dekoratif baru.

## Tampilan Pegawai

### Pengantar

Di bawah header terdapat:

1. Label kecil `PENGAJUAN BARU`.
2. Judul **Ajukan dokumen kepegawaian**.
3. Deskripsi singkat tentang pengisian detail dan unggah PDF.
4. Indikator tiga tahap yang bersifat informasional: Detail, Dokumen, dan Validasi. Indikator tidak mengubah alur program.

### Area kerja dua kolom

Gunakan dua kolom dengan proporsi sekitar 60:40.

Kolom kiri adalah kartu **Detail Dokumen**. Kartu ini mempertahankan kategori dan seluruh input dinamis yang sudah ada:

- Kursus: `Tanggal Kursus` dan `Tanggal Selesai Kursus`.
- Diklat: `Tanggal Diklat`.
- Jabatan: `Jabatan Fungsional Umum` dan `Nomor SK`.
- Golongan: `Golongan`.
- PNS dan CPNS: pesan informasi tanpa input tambahan.

Setiap label diletakkan tepat di atas kontrol input dan tidak disembunyikan.

Kolom kanan adalah kartu **Unggah Dokumen**. Kartu memuat file uploader, informasi format PDF, kartu file setelah berhasil dipilih, aksi hapus file, keterangan penggantian file, serta tombol **Validasi & Ajukan Dokumen**.

### Proses dan hasil

- Progress bar, spinner, status proses, pesan error, dan pesan hasil tetap memakai kondisi serta teks yang sudah ada.
- Komponen proses ditempatkan dalam area status yang konsisten di bawah area kerja.
- Keadaan disabled selama pemrosesan tetap dipertahankan dan diberi tampilan redup yang jelas.
- Hasil berhasil memakai alert hijau; penolakan atau kegagalan memakai alert merah; informasi proses memakai biru lembut.

## Tampilan Admin

### Ringkasan

- Tampilkan judul dan deskripsi singkat di bawah header.
- Pertahankan lima metric: Total, Menunggu, Ditolak Sistem, Diterima Admin, dan Ditolak Admin.
- Tata metric sebagai lima kartu sejajar dengan angka yang dominan, label ringkas, dan aksen status yang berbeda.

### Filter dan daftar pengajuan

- Pertahankan selectbox filter status beserta pemetaan dan perilakunya saat ini.
- Letakkan jumlah dokumen yang ditampilkan dekat dengan filter.
- Setiap pengajuan tetap menggunakan expander, tetapi diberi gaya kartu dengan badge status yang mudah dipindai.
- Tidak ditambahkan kolom pencarian karena penambahan tersebut akan mengubah perilaku aplikasi.

### Detail dan keputusan

- Informasi dokumen, detail pegawai, hasil sistem, ekstraksi, similarity, OCR, dokumen asli, dan keputusan admin tetap tersedia dengan urutan logis yang sama.
- Data teknis seperti JSON dan OCR ditempatkan dalam expander sekunder agar tidak mendominasi tampilan.
- Tombol menerima memakai warna utama `#4E9AD3`; tombol menolak memakai gaya outline merah agar kedua tindakan mudah dibedakan tanpa menciptakan dua tombol utama.
- Persyaratan alasan penolakan dan seluruh perubahan status tetap sama.

## Data dan Perilaku yang Dipertahankan

Aliran data tidak berubah:

1. Pengguna memilih peran dan kategori.
2. Input dinamis mengisi objek `detail`.
3. PDF disimpan di `st.session_state.uploaded_pdf`.
4. Tombol validasi menjalankan OCR dan pipeline yang sama.
5. Hasil ditambahkan ke `st.session_state.pengajuan` dengan struktur yang sama.
6. Admin memfilter, meninjau, mengunduh, menerima, atau menolak menggunakan handler yang sama.

Refactor tampilan diperbolehkan hanya jika ekspresi kondisi, key widget, nilai status, dan mutasi session state tetap identik secara perilaku.

## Penanganan Error dan State

- Pesan error yang ada tidak dihapus atau diubah maknanya.
- File yang belum diunggah tetap memicu peringatan yang sama.
- Exception OCR/pipeline tetap ditangkap oleh blok yang ada.
- Temporary PDF tetap dibersihkan pada `finally`.
- Rerun setelah unggah, hapus, buka/tutup akses PDF, terima, dan tolak tetap dipertahankan.
- CSS tidak boleh menghalangi interaksi widget kecuali ketika proses validasi memang sedang mengunci UI.

## Strategi Implementasi

- Konsolidasikan token visual dan selector CSS di bagian tema `app.py`.
- Gunakan container dan columns Streamlit untuk struktur; gunakan HTML/CSS hanya untuk header, label dekoratif, badge, dan elemen presentasi yang tidak membutuhkan state.
- Pertahankan widget Streamlit asli untuk input, upload, filter, expander, progress, download, dan tombol agar aksesibilitas serta event handler tidak berubah.
- Hindari selector CSS yang terlalu bergantung pada struktur DOM internal apabila tersedia selector `data-testid` yang lebih stabil.

## Verifikasi

### Pemeriksaan statis

- Pastikan hanya presentasi `app.py` yang berubah saat implementasi.
- Pastikan file modul pemrosesan tidak berubah.
- Pastikan key widget, nilai status, dan field session state tetap sama.
- Jalankan pemeriksaan sintaks Python.

### Pemeriksaan browser desktop

- Periksa tampilan Pegawai untuk seluruh kategori dokumen.
- Periksa state sebelum unggah, sesudah unggah, saat proses, berhasil, ditolak sistem, dan error.
- Periksa tampilan Admin tanpa data dan dengan data pada seluruh status.
- Uji filter, expander, akses/unduh PDF, terima, dan tolak.
- Pastikan tidak ada teks terpotong, komponen tumpang tindih, ikon rusak, atau kontras teks yang buruk pada lebar desktop umum.

## Kriteria Penerimaan

- Warna utama yang terlihat adalah `#4E9AD3`.
- Tidak ada logo/inisial `VD` atau kata `BKKBN` yang ditambahkan pada UI.
- Nama **Validasi Dokumen Kepegawaian** terlihat jelas di sidebar.
- Layout Pegawai menggunakan pola dua kolom Detail Dokumen dan Unggah Dokumen.
- Seluruh label input dinamis tetap terlihat.
- Dashboard Admin lebih mudah dipindai tanpa menambah fitur baru.
- Semua perilaku lama tetap berjalan tanpa perubahan logika.
