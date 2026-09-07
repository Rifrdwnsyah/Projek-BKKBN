# Streamlit UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengubah antarmuka Streamlit menjadi workspace desktop modern-minimalis berwarna utama `#4E9AD3` tanpa mengubah logika validasi, state, atau alur bisnis.

**Architecture:** Implementasi tetap berada di `app.py` agar tidak memecah arsitektur proyek yang saat ini berupa satu entry point Streamlit. Styling dikonsolidasikan dalam satu blok CSS, sedangkan helper presentasi hanya merender sidebar, header, pengantar, dan label status; seluruh widget, handler, pipeline, dan struktur `st.session_state` dipertahankan.

**Tech Stack:** Python 3.12, Streamlit 1.63.0, HTML/CSS melalui `st.markdown`, komponen native Streamlit.

---

### Task 1: Tetapkan fondasi tema dan shell aplikasi

**Files:**
- Modify: `app.py:13-102`

- [ ] **Step 1: Catat kontrak UI dan perilaku sebelum edit**

Run:

```powershell
rg -n 'page_title|st\.session_state|MENUNGGU VERIFIKASI ADMIN|DITOLAK SISTEM|DITERIMA ADMIN|DITOLAK ADMIN|run_pipeline|extract_text_from_pdf' app.py
```

Expected: judul lama ditemukan; key session state, nilai status, dan pemanggilan pipeline tercatat sebagai baseline yang tidak boleh hilang.

- [ ] **Step 2: Ganti konfigurasi halaman dan CSS global**

Ubah konfigurasi menjadi:

```python
st.set_page_config(
    page_title="Validasi Dokumen Kepegawaian",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

Blok CSS harus mendefinisikan token berikut dan menggunakannya untuk app canvas, sidebar, typography, button, input, selectbox, uploader, progress, metric, alert, expander, serta keadaan disabled:

```css
:root {
    --brand: #4E9AD3;
    --brand-hover: #3D86BE;
    --brand-soft: #EAF4FB;
    --canvas: #F5F8FB;
    --surface: #FFFFFF;
    --text: #17324D;
    --muted: #6F8194;
    --border: #DFE8F0;
}
```

Gunakan font `Inter, "Segoe UI", Arial, sans-serif`, sidebar putih, canvas abu-biru muda, radius 8-16 px, border tipis, dan shadow ringan. Hilangkan dekorasi emoji yang rawan rusak; jangan memuat font atau icon eksternal.

- [ ] **Step 3: Tambahkan helper presentasi tanpa state**

Tambahkan helper sebelum inisialisasi session state:

```python
def render_page_header(title, meta):
    st.markdown(
        f'<div class="app-header"><strong>{title}</strong><span>{meta}</span></div>',
        unsafe_allow_html=True,
    )


def render_intro(eyebrow, title, description):
    st.markdown(
        f'''<section class="page-intro">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </section>''',
        unsafe_allow_html=True,
    )
```

Helper tidak boleh membaca atau menulis `st.session_state`.

- [ ] **Step 4: Verifikasi sintaks**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py
```

Expected: exit code 0 tanpa output error.

- [ ] **Step 5: Commit fondasi visual**

```powershell
git add app.py
git commit -m "style: establish Streamlit visual foundation"
```

### Task 2: Desain ulang sidebar dan halaman Pegawai

**Files:**
- Modify: `app.py:105-718`

- [ ] **Step 1: Ubah sidebar menjadi navigasi workspace**

Pertahankan radio dengan nilai yang sama, tetapi render brand teks dan label navigasi:

```python
st.sidebar.markdown(
    '<div class="sidebar-brand">Validasi Dokumen<br>Kepegawaian</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="sidebar-label">TAMPILAN</div>', unsafe_allow_html=True)
role = st.sidebar.radio(
    "Pilih Tampilan",
    ["Pegawai", "Admin"],
    label_visibility="collapsed",
)
```

Tidak boleh ada logo, inisial `VD`, atau teks `BKKBN`.

- [ ] **Step 2: Tambahkan header dan pengantar Pegawai**

Di cabang `role == "Pegawai"`, render:

```python
render_page_header("Ruang Pengajuan", "Sistem validasi dokumen")
render_intro(
    "PENGAJUAN BARU",
    "Ajukan dokumen kepegawaian",
    "Lengkapi detail dan unggah PDF untuk memulai pemeriksaan awal.",
)
```

Tambahkan stepper informasional `Detail`, `Dokumen`, `Validasi` sebagai HTML tanpa event handler.

- [ ] **Step 3: Susun area kerja dua kolom**

Gunakan:

```python
detail_col, upload_col = st.columns([1.2, 0.8], gap="large")
```

Di `detail_col`, letakkan container berbatas yang memuat selectbox kategori dan input dinamis. Di `upload_col`, letakkan container berbatas yang memuat uploader atau kartu file, aksi hapus, caption, dan tombol validasi.

Pertahankan persis label dan pemetaan `detail`:

```python
# Kursus
detail = {"tanggal_kursus": tanggal_kursus, "tanggal_selesai_kursus": tanggal_selesai}
# Diklat
detail = {"tanggal": tanggal}
# Jabatan
detail = {"jabatan_fungsional_umum": jabatan, "nomor_sk": nomor_sk}
# Golongan
detail = {"golongan": golongan}
```

Simpan hasil tombol ke `submit_clicked`; pindahkan hanya posisi render tombol, lalu biarkan blok `if submit_clicked:` menjalankan isi handler lama tanpa perubahan.

- [ ] **Step 4: Restyle file, progress, dan hasil**

Kartu file yang dipilih memakai class `uploaded-file-card`; tombol hapus menjadi tombol sekunder. Tempatkan progress dan alert hasil dalam aliran di bawah area dua kolom. Pertahankan semua nilai progress `10`, `25`, `75`, `85`, `100`, isi pesan, `try/except/finally`, dan penghapusan temporary PDF.

- [ ] **Step 5: Jalankan pemeriksaan sintaks dan kontrak Pegawai**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py
rg -n 'Tanggal Kursus|Tanggal Selesai Kursus|Tanggal Diklat|Jabatan Fungsional Umum|Nomor SK|Golongan|extract_text_from_pdf|run_pipeline' app.py
```

Expected: syntax valid dan seluruh label serta pemanggilan pipeline tetap ditemukan.

- [ ] **Step 6: Commit halaman Pegawai**

```powershell
git add app.py
git commit -m "style: redesign employee submission workspace"
```

### Task 3: Desain ulang halaman Admin

**Files:**
- Modify: `app.py:721-1406`

- [ ] **Step 1: Tambahkan shell dan ringkasan Admin**

Di cabang `role == "Admin"`, ganti judul lama dengan:

```python
render_page_header("Ruang Verifikasi", f"{total} dokumen tercatat")
render_intro(
    "DASHBOARD ADMIN",
    "Verifikasi dokumen",
    "Pantau status dan tinjau hasil pemeriksaan otomatis.",
)
```

Hitung `total`, `menunggu`, `ditolak_sistem`, `diterima_admin`, dan `ditolak_admin` dengan ekspresi lama sebelum header membutuhkan `total`.

- [ ] **Step 2: Tata metric menjadi kartu statistik**

Pertahankan lima pemanggilan `metric` dengan label dan nilai yang sama di lima kolom. Styling dibedakan melalui CSS `data-testid="stMetric"`; tidak menambahkan data atau perhitungan baru.

- [ ] **Step 3: Rapikan filter dan daftar pengajuan**

Pertahankan selectbox `Filter Status Pengajuan`, `status_mapping`, dan filter list lama. Tampilkan jumlah hasil di dekat filter. Render judul expander dengan nama file, kategori, dan status yang sama, tetapi gunakan simbol aman dan badge visual melalui CSS; jangan menambahkan fitur pencarian.

- [ ] **Step 4: Kelompokkan detail dan tindakan**

Pertahankan seluruh section berikut dalam urutan yang sama:

```text
Informasi Dokumen
Detail yang Diajukan Pegawai
Hasil Pemeriksaan Sistem
Data Hasil Ekstraksi
Hasil Similarity
Hasil OCR
Dokumen Asli
Keputusan Admin
```

Gunakan container, divider, caption, dan expander sekunder agar JSON/OCR tidak mendominasi. Tombol terima menjadi primary `#4E9AD3`; tombol tolak diberi class/selector gaya outline merah. Jangan ubah key widget, validasi alasan penolakan, status, atau isi mutasi session state.

- [ ] **Step 5: Jalankan pemeriksaan sintaks dan kontrak Admin**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py
rg -n 'Filter Status Pengajuan|status_mapping|pdf_access_|download_|close_pdf_|alasan_|terima_|tolak_|DITERIMA ADMIN|DITOLAK ADMIN' app.py
```

Expected: syntax valid dan seluruh key/status lama tetap ditemukan.

- [ ] **Step 6: Commit halaman Admin**

```powershell
git add app.py
git commit -m "style: redesign admin verification workspace"
```

### Task 4: Verifikasi regresi dan tampilan desktop

**Files:**
- Verify: `app.py`
- Verify unchanged: `extractor.py`, `ocr.py`, `pipeline.py`, `rules.py`, `similarity.py`

- [ ] **Step 1: Bandingkan kontrak logika dengan baseline**

Run:

```powershell
git diff c5d771e -- app.py
git diff --exit-code c5d771e -- extractor.py ocr.py pipeline.py rules.py similarity.py
```

Expected: diff `app.py` hanya mencakup presentasi/penataan; perintah kedua exit code 0.

- [ ] **Step 2: Jalankan aplikasi Streamlit**

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.port 8501
```

Expected: server aktif pada `http://localhost:8501` tanpa traceback.

- [ ] **Step 3: Uji halaman Pegawai di browser desktop**

Periksa kategori Kursus, Diklat, Jabatan, Golongan, PNS, dan CPNS. Pastikan label dinamis terlihat, uploader bekerja, kartu file/hapus tampil, tombol validasi dapat diklik, progress terlihat, dan state hasil tetap muncul.

- [ ] **Step 4: Uji halaman Admin di browser desktop**

Periksa keadaan kosong dan data yang muncul dari pengajuan. Uji filter status, expander detail, akses/tutup/download PDF, alasan penolakan, tombol terima, dan tombol tolak. Pastikan tidak ada overflow, teks terpotong, ikon rusak, atau elemen bertumpuk.

- [ ] **Step 5: Jalankan pemeriksaan akhir**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile app.py extractor.py ocr.py pipeline.py rules.py similarity.py
git diff --check
git status --short
```

Expected: kompilasi dan diff check berhasil; status hanya menampilkan perubahan yang sengaja dibuat dan artefak lama yang tidak di-stage.

- [ ] **Step 6: Commit perbaikan QA jika diperlukan**

Jika QA menghasilkan koreksi visual pada `app.py`:

```powershell
git add app.py
git commit -m "fix: polish Streamlit desktop interface"
```

Jika tidak ada koreksi, langkah commit ini dilewati.
