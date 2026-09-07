# Sticky Sidebar Interactions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menjadikan header dan identitas sidebar tetap terlihat, memberi transisi pada kartu role, serta menata kontrol tutup/buka sidebar menjadi satu tombol kecil pada setiap state.

**Architecture:** Seluruh perubahan berada di blok CSS presentasional `app.py`. Widget radio Streamlit, key, session state, handler pengajuan, handler admin, dan pipeline tidak diubah. Selector tombol sidebar menggunakan test id/aria label Streamlit dan fallback selector yang sempit.

**Tech Stack:** Python 3.12, Streamlit 1.63.0, CSS melalui `st.markdown`.

---

### Task 1: Tambahkan sticky shell dan tombol sidebar kecil

**Files:**
- Modify: `app.py` blok tema global dan selector sidebar

- [ ] **Step 1: Tambahkan sticky header dan brand sidebar**

Tambahkan `position: sticky`, `top`, `z-index`, dan background opaque pada `.app-header` serta `.sidebar-brand` agar tidak tertutup ketika kontainer digulir.

- [ ] **Step 2: Tata kontrol native Streamlit**

Gaya `[data-testid="stSidebarCollapseButton"]` menjadi tombol outline kecil di pojok kanan atas sidebar. Gaya `[data-testid="stSidebarCollapsedControl"]` menjadi tombol outline kecil di pojok kiri atas area konten ketika sidebar tertutup. Sembunyikan teks/ikon tambahan dari wrapper yang sama sehingga tidak ada dua kontrol pada state yang sama.

- [ ] **Step 3: Jalankan kompilasi**

Run `..\\.venv\\Scripts\\python.exe -m py_compile app.py` dari root proyek. Expected: exit code 0.

### Task 2: Animasi kartu role dan verifikasi kontrak

**Files:**
- Modify: `app.py` selector radio role
- Verify unchanged: `extractor.py`, `ocr.py`, `pipeline.py`, `rules.py`, `similarity.py`

- [ ] **Step 1: Tambahkan transisi role**

Pertahankan `st.sidebar.radio` dan label yang sama, lalu tambahkan transisi transform/background/box-shadow pada label dan keyframe ringan untuk label terpilih melalui selector `:has(input:checked)`.

- [ ] **Step 2: Pastikan hanya presentasi berubah**

Run `git diff -- app.py` dan `git diff --exit-code -- extractor.py ocr.py pipeline.py rules.py similarity.py`. Expected: hanya CSS app.py berubah; modul pipeline exit code 0.

- [ ] **Step 3: Uji sintaks dan diff whitespace**

Run `..\\.venv\\Scripts\\python.exe -m py_compile app.py extractor.py ocr.py pipeline.py rules.py similarity.py` dan `git diff --check`. Expected: semua berhasil.

- [ ] **Step 4: Commit dan push**

Run `git add app.py docs/superpowers/plans/2026-09-07-sticky-sidebar-interactions.md` lalu `git commit -m "style: refine sticky sidebar controls"` dan `git push origin feat/streamlit-ui-redesign`.