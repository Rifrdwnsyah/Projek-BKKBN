import os
import uuid
import streamlit as st

from ocr import extract_text_from_pdf
from pipeline import run_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Document Validator BKKBN",
    page_icon="📄",
    layout="wide"
)

# ============================================================
# THEME
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #FFFFFF;
    }

    [data-testid="stSidebar"] {
        background-color: #F0F9FF;
        border-right: 1px solid #BAE6FD;
    }

    h1, h2, h3 {
        color: #0369A1;
    }

    div.stButton > button[kind="primary"] {
        background-color: #38BDF8;
        border-color: #38BDF8;
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #0EA5E9;
        border-color: #0EA5E9;
        color: white;
    }

    div.stButton > button:disabled {
        opacity: 0.55;
        cursor: not-allowed;
    }

    [data-testid="stFileUploader"] {
        background-color: #F8FCFF;
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 8px;
    }

    /* Hilangkan ikon + / upload bawaan */
    [data-testid="stFileUploaderDropzone"] svg {
        display: none;
    }

    [data-testid="stProgress"] > div > div {
        background-color: #38BDF8;
    }

    [data-testid="stExpander"] {
        border-color: #BAE6FD;
        border-radius: 10px;
    }

    [data-testid="stMetric"] {
        background-color: #F8FCFF;
        border: 1px solid #E0F2FE;
        border-radius: 10px;
        padding: 12px;
    }

    .uploaded-file-card {
        background-color: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "pengajuan" not in st.session_state:
    st.session_state.pengajuan = []

if "uploaded_pdf" not in st.session_state:
    st.session_state.uploaded_pdf = None

if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📄 Document Validator")

role = st.sidebar.radio(
    "Pilih Tampilan",
    [
        "Pegawai",
        "Admin"
    ]
)


# ============================================================
# PEGAWAI
# ============================================================

if role == "Pegawai":

    st.title("📄 Pengajuan Dokumen")

    st.write(
        "Upload dokumen dan isi detail yang diperlukan. "
        "Sistem akan melakukan pemeriksaan awal terhadap dokumen "
        "sebelum dokumen ditinjau lebih lanjut."
    )


    # ========================================================
    # CATEGORY
    # ========================================================

    kategori = st.selectbox(
        "Pilih Kategori Dokumen",
        [
            "Kursus",
            "Diklat",
            "Jabatan",
            "Golongan",
            "PNS",
            "CPNS"
        ]
    )


    # ========================================================
    # DETAIL
    # ========================================================

    detail = {}


    # --------------------------------------------------------
    # KURSUS
    # --------------------------------------------------------

    if kategori == "Kursus":

        st.subheader(
            "Detail Kursus"
        )

        tanggal_kursus = st.text_input(
            "Tanggal Kursus",
            placeholder="Contoh: 13-04-2015"
        )

        tanggal_selesai = st.text_input(
            "Tanggal Selesai Kursus",
            placeholder="Contoh: 17-04-2015"
        )

        detail = {
            "tanggal_kursus": tanggal_kursus,
            "tanggal_selesai_kursus": tanggal_selesai
        }


    # --------------------------------------------------------
    # DIKLAT
    # --------------------------------------------------------

    elif kategori == "Diklat":

        st.subheader(
            "Detail Diklat"
        )

        tanggal = st.text_input(
            "Tanggal Diklat",
            placeholder="Contoh: 13-08-2022"
        )

        detail = {
            "tanggal": tanggal
        }


    # --------------------------------------------------------
    # JABATAN
    # --------------------------------------------------------

    elif kategori == "Jabatan":

        st.subheader(
            "Detail Jabatan"
        )

        jabatan = st.text_input(
            "Jabatan Fungsional Umum",
            placeholder=(
                "Contoh: Kepala Bidang "
                "Pengendalian Penduduk"
            )
        )

        nomor_sk = st.text_input(
            "Nomor SK",
            placeholder=(
                "Contoh: 338/KP.05.01/PEG/2018"
            )
        )

        detail = {
            "jabatan_fungsional_umum": jabatan,
            "nomor_sk": nomor_sk
        }


    # --------------------------------------------------------
    # GOLONGAN
    # --------------------------------------------------------

    elif kategori == "Golongan":

        st.subheader(
            "Detail Golongan"
        )

        golongan = st.text_input(
            "Golongan",
            placeholder="Contoh: II/c"
        )

        detail = {
            "golongan": golongan
        }


    # --------------------------------------------------------
    # PNS
    # --------------------------------------------------------

    elif kategori == "PNS":

        st.subheader(
            "Dokumen PNS"
        )

        st.info(
            "Silakan upload dokumen pengangkatan "
            "Pegawai Negeri Sipil."
        )

        detail = {}


    # --------------------------------------------------------
    # CPNS
    # --------------------------------------------------------

    elif kategori == "CPNS":

        st.subheader(
            "Dokumen CPNS"
        )

        st.info(
            "Silakan upload dokumen pengangkatan "
            "Calon Pegawai Negeri Sipil."
        )

        detail = {}


    # ========================================================
    # FILE UPLOAD
    # ========================================================

    if st.session_state.uploaded_pdf is None:

        uploaded_file = st.file_uploader(
            "Upload Dokumen PDF",
            type=["pdf"],
            accept_multiple_files=False,
            key=f"pdf_uploader_{st.session_state.uploader_version}"
        )

        if uploaded_file is not None:

            st.session_state.uploaded_pdf = {
                "name": uploaded_file.name,
                "bytes": uploaded_file.getvalue(),
                "size": uploaded_file.size
            }

            st.rerun()

    else:

        uploaded_file = st.session_state.uploaded_pdf

        file_size_mb = (
            uploaded_file["size"] / (1024 * 1024)
        )

        st.markdown(
            f"""
            <div class="uploaded-file-card">
                <b>📄 {uploaded_file["name"]}</b><br>
                <small>{file_size_mb:.2f} MB</small>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "🗑️ Hapus File"
        ):

            st.session_state.uploaded_pdf = None
            st.session_state.uploader_version += 1
            st.rerun()

        st.caption(
            "Untuk mengganti dokumen, hapus file ini terlebih dahulu."
        )


    # ========================================================
    # VALIDATION BUTTON
    # ========================================================

    ui_lock = st.empty()

    if st.button(
        "🔍 Validasi dan Ajukan Dokumen",
        type="primary",
        use_container_width=True
    ):

        if st.session_state.uploaded_pdf is None:

            st.error(
                "Silakan upload dokumen PDF terlebih dahulu."
            )

        else:

            uploaded_file = st.session_state.uploaded_pdf

            # =================================================
            # LOCK UI SELAMA PROSES
            # =================================================

            ui_lock.markdown(
                """
                <style>

                [data-testid="stSelectbox"],
                [data-testid="stTextInput"],
                [data-testid="stFileUploader"] {
                    pointer-events: none !important;
                    opacity: 0.60;
                }

                /* Parent tombol yang menerima hover */
                div.stButton,
                div[data-testid="stButton"] {
                    cursor: not-allowed !important;
                }

                /* Tombol tidak bisa diklik */
                div.stButton > button,
                div[data-testid="stButton"] > button {
                    pointer-events: none !important;
                    opacity: 0.60 !important;
                }

                [data-testid="stSidebar"] {
                    pointer-events: none !important;
                    opacity: 0.75;
                }

                </style>
                """,
                unsafe_allow_html=True
            )

            # =================================================
            # TEMP FILE
            # =================================================

            temp_filename = (
                f"temp_{uuid.uuid4().hex}.pdf"
            )

            temp_path = temp_filename


            # =================================================
            # PROGRESS UI
            # =================================================

            progress_bar = st.progress(
                0
            )

            progress_text = st.empty()

            status_box = st.empty()


            try:

                # =============================================
                # STEP 1 - SIMPAN FILE
                # =============================================

                progress_bar.progress(
                    10
                )

                progress_text.write(
                    "📁 Menyiapkan dokumen..."
                )


                with open(
                    temp_path,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_file["bytes"]
                    )


                # =============================================
                # STEP 2 - OCR
                # =============================================

                progress_bar.progress(
                    25
                )

                progress_text.write(
                    "🔍 Membaca isi dokumen..."
                )

                status_box.info(
                    "Dokumen sedang diproses. "
                    "Dokumen hasil scan dapat membutuhkan "
                    "waktu beberapa saat."
                )


                with st.spinner(
                    "Sedang membaca dokumen..."
                ):

                    ocr_text = extract_text_from_pdf(
                        temp_path
                    )


                progress_bar.progress(
                    75
                )

                progress_text.write(
                    "✅ Dokumen berhasil dibaca."
                )

                status_box.empty()


                # =============================================
                # STEP 3 - VALIDASI
                # =============================================

                progress_bar.progress(
                    85
                )

                progress_text.write(
                    "🧠 Memeriksa kesesuaian dokumen..."
                )


                with st.spinner(
                    "Sedang melakukan pemeriksaan..."
                ):

                    result = run_pipeline(
                        kategori=kategori,
                        ocr_text=ocr_text,
                        detail=detail
                    )


                # =============================================
                # STEP 4 - SELESAI
                # =============================================

                progress_bar.progress(
                    100
                )

                progress_text.write(
                    "✅ Pemeriksaan dokumen selesai."
                )


                # =============================================
                # HASIL PIPELINE ERROR
                # =============================================

                if not result.get(
                    "success"
                ):

                    st.error(
                        "Terjadi kesalahan saat "
                        "memproses dokumen."
                    )

                    st.write(
                        "**Keterangan:**",
                        result.get(
                            "reason",
                            "Terjadi kesalahan."
                        )
                    )


                # =============================================
                # PIPELINE BERHASIL
                # =============================================

                else:

                    valid = result.get(
                        "valid"
                    )

                    reason = result.get(
                        "reason"
                    )


                    # =========================================
                    # STATUS
                    # =========================================

                    if valid:

                        status_pengajuan = (
                            "MENUNGGU VERIFIKASI ADMIN"
                        )

                    else:

                        status_pengajuan = (
                            "DITOLAK SISTEM"
                        )


                    # =========================================
                    # SIMPAN PENGAJUAN
                    # =========================================

                    pengajuan_id = str(
                        uuid.uuid4()
                    )

                    pdf_bytes = (
                        uploaded_file["bytes"]
                    )


                    pengajuan_baru = {

                        "id": pengajuan_id,

                        "nama_file":
                            uploaded_file["name"],

                        "kategori":
                            kategori,

                        "detail":
                            detail,

                        "status":
                            status_pengajuan,

                        "validasi_sistem":
                            valid,

                        "reason_system":
                            reason,

                        "extracted":
                            result.get(
                                "extracted",
                                {}
                            ),

                        "similarity":
                            result.get(
                                "similarity",
                                {}
                            ),

                        "ocr_text":
                            ocr_text,

                        "pdf_bytes":
                            pdf_bytes,

                        "keputusan_admin":
                            None,

                        "alasan_admin":
                            None
                    }


                    st.session_state.pengajuan.append(
                        pengajuan_baru
                    )


                    # =========================================
                    # NOTICE PEGAWAI
                    # =========================================

                    st.divider()

                    st.subheader(
                        "Status Pengajuan"
                    )


                    if valid:

                        st.success(
                            "✅ Dokumen Anda telah diajukan "
                            "kepada admin untuk ditinjau "
                            "lebih lanjut."
                        )


                    else:

                        st.error(
                            "❌ Maaf, dokumen Anda "
                            "tidak dapat diajukan."
                        )

                        st.write(
                            "**Alasan:**",
                            reason
                        )


            except Exception as e:

                progress_text.write(
                    "❌ Proses gagal."
                )

                status_box.empty()

                st.error(
                    f"Terjadi kesalahan: {e}"
                )


            finally:

                ui_lock.empty()

                if os.path.exists(
                    temp_path
                ):

                    os.remove(
                        temp_path
                    )


# ============================================================
# ADMIN
# ============================================================

elif role == "Admin":

    st.title(
        "🛡️ Verifikasi Admin"
    )

    st.write(
        "Halaman ini digunakan untuk melihat seluruh "
        "dokumen pengajuan dan hasil pemeriksaan otomatis."
    )


    # ========================================================
    # HITUNG STATUS
    # ========================================================

    total = len(
        st.session_state.pengajuan
    )


    menunggu = sum(
        1
        for item
        in st.session_state.pengajuan
        if item["status"]
        ==
        "MENUNGGU VERIFIKASI ADMIN"
    )


    ditolak_sistem = sum(
        1
        for item
        in st.session_state.pengajuan
        if item["status"]
        ==
        "DITOLAK SISTEM"
    )


    diterima_admin = sum(
        1
        for item
        in st.session_state.pengajuan
        if item["status"]
        ==
        "DITERIMA ADMIN"
    )


    ditolak_admin = sum(
        1
        for item
        in st.session_state.pengajuan
        if item["status"]
        ==
        "DITOLAK ADMIN"
    )


    # ========================================================
    # METRIC
    # ========================================================

    col1, col2, col3, col4, col5 = st.columns(
        5
    )


    col1.metric(
        "Total",
        total
    )

    col2.metric(
        "Menunggu",
        menunggu
    )

    col3.metric(
        "Ditolak Sistem",
        ditolak_sistem
    )

    col4.metric(
        "Diterima Admin",
        diterima_admin
    )

    col5.metric(
        "Ditolak Admin",
        ditolak_admin
    )


    st.divider()


    # ========================================================
    # FILTER
    # ========================================================

    filter_status = st.selectbox(
        "Filter Status Pengajuan",
        [
            "Semua",
            "Menunggu Verifikasi Admin",
            "Ditolak Sistem",
            "Diterima Admin",
            "Ditolak Admin"
        ]
    )


    # ========================================================
    # MAPPING FILTER
    # ========================================================

    status_mapping = {

        "Menunggu Verifikasi Admin":
            "MENUNGGU VERIFIKASI ADMIN",

        "Ditolak Sistem":
            "DITOLAK SISTEM",

        "Diterima Admin":
            "DITERIMA ADMIN",

        "Ditolak Admin":
            "DITOLAK ADMIN"
    }


    # ========================================================
    # FILTER DATA
    # ========================================================

    if filter_status == "Semua":

        data_pengajuan = (
            st.session_state.pengajuan
        )

    else:

        target_status = status_mapping[
            filter_status
        ]

        data_pengajuan = [
            item
            for item
            in st.session_state.pengajuan
            if item["status"]
            ==
            target_status
        ]


    # ========================================================
    # BELUM ADA DATA
    # ========================================================

    if not data_pengajuan:

        st.info(
            "Tidak ada dokumen pada status ini."
        )


    # ========================================================
    # DAFTAR DOKUMEN
    # ========================================================

    else:

        st.write(
            f"Menampilkan "
            f"**{len(data_pengajuan)} dokumen**"
        )


        for item in data_pengajuan:

            # =================================================
            # INDEX ASLI
            # =================================================

            original_index = (
                st.session_state.pengajuan.index(
                    item
                )
            )


            # =================================================
            # STATUS ICON
            # =================================================

            if (
                item["status"]
                ==
                "MENUNGGU VERIFIKASI ADMIN"
            ):

                status_icon = "🟡"


            elif (
                item["status"]
                ==
                "DITERIMA ADMIN"
            ):

                status_icon = "🟢"


            else:

                status_icon = "🔴"


            title = (
                f"{status_icon} "
                f"{item['kategori']} | "
                f"{item['nama_file']} | "
                f"{item['status']}"
            )


            # =================================================
            # EXPANDER DOKUMEN
            # =================================================

            with st.expander(
                title,
                expanded=False
            ):

                # =============================================
                # INFORMASI DOKUMEN
                # =============================================

                st.subheader(
                    "Informasi Dokumen"
                )


                info_col1, info_col2 = st.columns(
                    2
                )


                with info_col1:

                    st.write(
                        "**Kategori:**",
                        item["kategori"]
                    )

                    st.write(
                        "**Nama File:**",
                        item["nama_file"]
                    )


                with info_col2:

                    st.write(
                        "**Status:**",
                        item["status"]
                    )


                st.divider()


                # =============================================
                # DETAIL PEGAWAI
                # =============================================

                st.subheader(
                    "Detail yang Diajukan Pegawai"
                )


                if item["detail"]:

                    st.json(
                        item["detail"]
                    )

                else:

                    st.write(
                        "Tidak ada detail tambahan "
                        "untuk kategori ini."
                    )


                # =============================================
                # HASIL SISTEM
                # =============================================

                st.subheader(
                    "Hasil Pemeriksaan Sistem"
                )


                if item["validasi_sistem"]:

                    st.info(
                        "Dokumen diteruskan untuk "
                        "peninjauan admin."
                    )

                else:

                    st.error(
                        "Dokumen ditolak oleh "
                        "pemeriksaan otomatis."
                    )


                st.write(
                    "**Alasan Sistem:**",
                    item["reason_system"]
                )


                # =============================================
                # DATA EKSTRAKSI
                # =============================================

                with st.expander(
                    "🔎 Data Hasil Ekstraksi"
                ):

                    st.json(
                        item["extracted"]
                    )


                # =============================================
                # SIMILARITY
                # =============================================

                if item["similarity"]:

                    with st.expander(
                        "📊 Hasil Similarity"
                    ):

                        st.json(
                            item["similarity"]
                        )


                # =============================================
                # OCR
                # =============================================

                with st.expander(
                    "📝 Hasil OCR"
                ):

                    st.text(
                        item["ocr_text"]
                    )


                # =============================================
                # DOKUMEN ASLI
                # ============================================================

                st.subheader(
                    "Dokumen Asli"
                )


                st.write(
                    "📄",
                    item["nama_file"]
                )


                pdf_access_key = (
                    f"pdf_access_"
                    f"{item['id']}"
                )


                if (
                    pdf_access_key
                    not in st.session_state
                ):

                    st.session_state[
                        pdf_access_key
                    ] = False


                if not st.session_state[
                    pdf_access_key
                ]:

                    if st.button(
                        "📄 Akses Dokumen Asli",

                        key=(
                            f"open_pdf_"
                            f"{item['id']}"
                        ),

                        use_container_width=False
                    ):

                        st.session_state[
                            pdf_access_key
                        ] = True

                        st.rerun()


                else:

                    st.info(
                        "Dokumen siap diunduh."
                    )


                    pdf_col1, pdf_col2 = st.columns(
                        [1, 1]
                    )


                    with pdf_col1:

                        st.download_button(
                            label=(
                                "⬇️ Download PDF"
                            ),

                            data=item[
                                "pdf_bytes"
                            ],

                            file_name=item[
                                "nama_file"
                            ],

                            mime=(
                                "application/pdf"
                            ),

                            key=(
                                f"download_"
                                f"{item['id']}"
                            ),

                            use_container_width=True
                        )


                    with pdf_col2:

                        if st.button(
                            "❌ Tutup Akses PDF",

                            key=(
                                f"close_pdf_"
                                f"{item['id']}"
                            ),

                            use_container_width=True
                        ):

                            st.session_state[
                                pdf_access_key
                            ] = False

                            st.rerun()


                # =============================================
                # MENUNGGU VERIFIKASI ADMIN
                # =============================================

                if (
                    item["status"]
                    ==
                    "MENUNGGU VERIFIKASI ADMIN"
                ):

                    st.divider()

                    st.subheader(
                        "Keputusan Admin"
                    )


                    alasan_admin = st.text_area(
                        "Catatan / Alasan Admin",

                        key=(
                            f"alasan_"
                            f"{item['id']}"
                        ),

                        placeholder=(
                            "Opsional jika diterima. "
                            "Wajib diisi jika ditolak."
                        )
                    )


                    col_terima, col_tolak = st.columns(
                        2
                    )


                    with col_terima:

                        if st.button(
                            "✅ Terima Dokumen",

                            key=(
                                f"terima_"
                                f"{item['id']}"
                            ),

                            type="primary",

                            use_container_width=True
                        ):

                            st.session_state.pengajuan[
                                original_index
                            ][
                                "status"
                            ] = (
                                "DITERIMA ADMIN"
                            )


                            st.session_state.pengajuan[
                                original_index
                            ][
                                "keputusan_admin"
                            ] = (
                                "DITERIMA"
                            )


                            st.session_state.pengajuan[
                                original_index
                            ][
                                "alasan_admin"
                            ] = (
                                alasan_admin
                                if alasan_admin
                                else
                                (
                                    "Dokumen telah "
                                    "ditinjau dan diterima "
                                    "oleh admin."
                                )
                            )


                            st.rerun()


                    with col_tolak:

                        if st.button(
                            "❌ Tolak Dokumen",

                            key=(
                                f"tolak_"
                                f"{item['id']}"
                            ),

                            use_container_width=True
                        ):

                            if not alasan_admin.strip():

                                st.warning(
                                    "Isi alasan penolakan "
                                    "terlebih dahulu."
                                )

                            else:

                                st.session_state.pengajuan[
                                    original_index
                                ][
                                    "status"
                                ] = (
                                    "DITOLAK ADMIN"
                                )


                                st.session_state.pengajuan[
                                    original_index
                                ][
                                    "keputusan_admin"
                                ] = (
                                    "DITOLAK"
                                )


                                st.session_state.pengajuan[
                                    original_index
                                ][
                                    "alasan_admin"
                                ] = (
                                    alasan_admin
                                )


                                st.rerun()


                elif (
                    item["status"]
                    ==
                    "DITOLAK SISTEM"
                ):

                    st.divider()

                    st.error(
                        "Dokumen ini telah ditolak "
                        "oleh sistem pada tahap "
                        "pemeriksaan awal."
                    )

                    st.write(
                        "**Alasan Penolakan:**",
                        item["reason_system"]
                    )


                elif (
                    item["status"]
                    ==
                    "DITERIMA ADMIN"
                ):

                    st.divider()

                    st.success(
                        "✅ Dokumen telah diterima "
                        "oleh admin."
                    )

                    st.write(
                        "**Catatan Admin:**",
                        item["alasan_admin"]
                    )


                elif (
                    item["status"]
                    ==
                    "DITOLAK ADMIN"
                ):

                    st.divider()

                    st.error(
                        "❌ Dokumen telah ditolak "
                        "oleh admin."
                    )

                    st.write(
                        "**Alasan Admin:**",
                        item["alasan_admin"]
                    )
