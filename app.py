import os
import uuid
import streamlit as st

from ocr import extract_text_from_pdf
from pipeline import run_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Validasi Dokumen Kepegawaian",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
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

st.markdown(
    """
    <style>
    :root {
        --brand: #4E9AD3; --brand-hover: #3D86BE; --brand-soft: #EAF4FB;
        --canvas: #F5F8FB; --surface: #FFFFFF; --text: #17324D;
        --muted: #6F8194; --border: #DFE8F0;
        --shadow: 0 8px 24px rgba(31, 71, 103, .08);
    }
    html, body, [class*="css"] { font-family: Inter, "Segoe UI", Arial, sans-serif; }
    .stApp { background: var(--canvas); color: var(--text); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stAppViewContainer"] > .main .block-container {
        max-width: 1480px; padding: 1.5rem 2.25rem 3rem;
    }
    [data-testid="stSidebar"] {
        width: 270px !important; min-width: 270px !important;
        background: var(--surface); border-right: 1px solid var(--border);
    }
    [data-testid="stSidebarContent"] { padding: .65rem .85rem 1.25rem; }
    .sidebar-brand {
        position: sticky; top: 0; z-index: 4;
        background: var(--surface);
        margin: .2rem .55rem 1.6rem; padding: 0 .25rem 1.35rem;
        border-bottom: 1px solid #EDF2F6; color: var(--text);
        font-size: 1.15rem; font-weight: 800; line-height: 1.25;
        letter-spacing: -.02em;
    }
    .sidebar-label {
        margin: 0 .8rem .55rem; color: #93A2B2; font-size: .7rem;
        font-weight: 800; letter-spacing: .12em;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: .35rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        min-height: 2.85rem; padding: .7rem .85rem; border-radius: 10px;
        color: var(--muted); font-weight: 650; transition: all .18s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        color: var(--brand-hover); background: #F4F9FD; transform: translateX(3px);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        color: var(--brand-hover); background: var(--brand-soft);
        box-shadow: inset 3px 0 0 var(--brand);
        animation: role-card-select .24s ease-out both;
    }
    @keyframes role-card-select {
        from { opacity: .72; transform: translateX(-4px) scale(.985); }
        to { opacity: 1; transform: translateX(0) scale(1); }
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] input { accent-color: var(--brand); }
    .app-header-spacer { height: 5.25rem; margin-bottom: 1.65rem; }
    .app-header {
        position: fixed !important; top: .75rem; left: calc(270px + 1.25rem); right: 1.25rem; z-index: 100;
        min-height: 64px; margin-bottom: 1.65rem; padding: 0 1.5rem;
        border-radius: 14px; background: var(--brand);
        box-shadow: 0 10px 24px rgba(78, 154, 211, .22); color: #FFF;
        display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    }
    .app-header strong { font-size: 1.02rem; font-weight: 800; }
    .app-header span { font-size: .82rem; font-weight: 500; opacity: .88; }
    .page-intro { margin: .15rem 0 1.2rem; }
    .page-intro .eyebrow {
        margin-bottom: .35rem; color: var(--brand-hover); font-size: .72rem;
        font-weight: 800; letter-spacing: .12em;
    }
    .page-intro h1 {
        margin: 0; color: var(--text); font-size: clamp(1.75rem, 2.4vw, 2.35rem);
        font-weight: 800; line-height: 1.16; letter-spacing: -.035em;
    }
    .page-intro p {
        max-width: 720px; margin: .55rem 0 0; color: var(--muted);
        font-size: .96rem; line-height: 1.65;
    }
    .workflow-steps {
        display: flex; align-items: center; gap: .65rem; margin: 0 0 1.35rem;
        color: var(--muted); font-size: .78rem; font-weight: 700;
    }
    .workflow-step { display: inline-flex; align-items: center; gap: .45rem; }
    .workflow-step b {
        width: 1.55rem; height: 1.55rem; border-radius: 999px;
        background: var(--brand); color: #FFF; display: inline-grid;
        place-items: center; font-size: .72rem;
    }
    .workflow-line { width: 2.5rem; height: 1px; background: #C9DAE7; }
    .section-heading { margin-bottom: .2rem; color: var(--text); font-size: 1.05rem; font-weight: 800; }
    .section-copy { margin-bottom: .85rem; color: var(--muted); font-size: .82rem; line-height: 1.55; }
    h1, h2, h3 { color: var(--text); letter-spacing: -.02em; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border) !important; border-radius: 14px !important;
        background: var(--surface); box-shadow: var(--shadow);
    }
    [data-testid="stWidgetLabel"] p { color: #53697D; font-size: .85rem; font-weight: 700; }
    [data-baseweb="select"] > div, [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-color: #D7E2EB !important; border-radius: 9px !important;
        background: #FFF !important; color: var(--text) !important;
    }
    [data-baseweb="select"] > div:focus-within, [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--brand) !important;
        box-shadow: 0 0 0 3px rgba(78, 154, 211, .14) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    div.stButton > button, div[data-testid="stButton"] > button,
    [data-testid="stDownloadButton"] > button {
        min-height: 2.65rem; border-radius: 9px; border-color: #C9D9E5;
        color: #3F5A70; font-weight: 750; transition: all .18s ease;
    }
    div.stButton > button:hover, div[data-testid="stButton"] > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        border-color: var(--brand); color: var(--brand-hover); background: #F7FBFE;
    }
    div.stButton > button[kind="primary"] {
        border-color: var(--brand); background: var(--brand); color: #FFF;
        box-shadow: 0 6px 14px rgba(78, 154, 211, .2);
    }
    div.stButton > button[kind="primary"]:hover {
        border-color: var(--brand-hover); background: var(--brand-hover); color: #FFF;
    }
    div.stButton > button:disabled { cursor: not-allowed; opacity: .52; }
    [data-testid="stFileUploader"] { padding: 0; border: 0; background: transparent; }
    [data-testid="stFileUploaderDropzone"] {
        min-height: 9.2rem; border: 1.5px dashed #99C8E8;
        border-radius: 12px; background: #F8FCFF;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--brand); background: #F2F9FD;
    }
    [data-testid="stFileUploaderDropzone"] svg { display: block; color: var(--brand); }
    [data-testid="stProgress"] > div > div { background: var(--brand); }
    [data-testid="stMetric"] {
        min-height: 112px; padding: 1rem 1.05rem; border: 1px solid var(--border);
        border-radius: 13px; background: var(--surface);
        box-shadow: 0 5px 18px rgba(31, 71, 103, .055);
    }
    [data-testid="stMetricValue"] { color: var(--text); font-weight: 800; }
    [data-testid="stMetricLabel"] { color: var(--muted); font-weight: 700; }
    [data-testid="stExpander"] {
        margin-bottom: .75rem; overflow: hidden; border: 1px solid var(--border);
        border-radius: 12px; background: var(--surface);
        box-shadow: 0 4px 14px rgba(31, 71, 103, .04);
    }
    [data-testid="stAlert"] { border-radius: 11px; border-width: 1px; }
    .uploaded-file-card {
        margin: .35rem 0 .8rem; padding: .95rem 1rem;
        border: 1px solid #B9D9EE; border-radius: 11px;
        background: var(--brand-soft); color: var(--text);
    }
    .uploaded-file-card small { color: var(--muted); }
    .result-count { margin: .45rem 0 .9rem; color: var(--muted); font-size: .86rem; }
    .status-waiting { color: #966515; }
    .status-approved { color: #18754B; }
    .status-rejected { color: #B43E49; }
    hr { border-color: var(--border) !important; }
    [data-testid="stSidebarCollapseButton"] {
        position: absolute !important; top: .65rem; right: .7rem; z-index: 30;
    }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        width: 2rem !important; min-width: 2rem !important;
        height: 2rem !important; min-height: 2rem !important;
        padding: 0 !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; background: var(--surface) !important;
        color: var(--muted) !important; box-shadow: 0 3px 10px rgba(31, 71, 103, .08) !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover {
        border-color: var(--brand) !important; color: var(--brand-hover) !important;
        background: var(--brand-soft) !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important; top: .75rem !important; left: .75rem !important;
        z-index: 30 !important; padding: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        width: auto !important; min-width: 4.35rem !important;
        padding: 0 .55rem !important; gap: .3rem !important;
        justify-content: center !important;
    }
    [data-testid="stSidebarCollapseButton"] button::after {
        content: "Tutup"; font-size: .68rem; font-weight: 750;
    }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "Buka"; font-size: .68rem; font-weight: 750;
    }
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarCollapsedControl"] button svg {
        width: 13px !important; height: 13px !important;
    }
    .sidebar-toggle-brand { }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        width: 2.15rem !important; min-width: 2.15rem !important;
        height: 2.15rem !important; min-height: 2.15rem !important;
        padding: 0 !important; border: 1px solid var(--brand) !important;
        border-radius: 8px !important; background: var(--brand) !important;
        color: #FFF !important; box-shadow: 0 5px 13px rgba(78, 154, 211, .24) !important;
    }
    [data-testid="stSidebarCollapseButton"] button::after,
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: none !important; display: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarCollapsedControl"] button svg {
        width: 15px !important; height: 15px !important;
        color: #FFF !important; stroke: #FFF !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover {
        border-color: var(--brand-hover) !important; background: var(--brand-hover) !important;
        color: #FFF !important;
    }    .sidebar-collapse-visibility-fix { }
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        transition: none !important; animation: none !important;
        transform: none !important;
    }    @media (max-width: 1100px) {
        [data-testid="stSidebar"] { width: 240px !important; min-width: 240px !important; }
        .app-header { left: calc(240px + 1rem); right: 1rem; }
        [data-testid="stAppViewContainer"] > .main .block-container {
            padding-left: 1.35rem; padding-right: 1.35rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


def render_page_header(title, meta):
    st.markdown(
        f'<div class="app-header-spacer" aria-hidden="true"></div><div class="app-header"><strong>{title}</strong><span>{meta}</span></div>',
        unsafe_allow_html=True
    )


def render_intro(eyebrow, title, description):
    st.markdown(
        f"""
        <section class="page-intro">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </section>
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

st.sidebar.markdown(
    '<div class="sidebar-brand">Validasi Dokumen<br>Kepegawaian</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<div class="sidebar-label">TAMPILAN</div>',
    unsafe_allow_html=True
)

role = st.sidebar.radio(
    "Pilih Tampilan",
    [
        "Pegawai",
        "Admin"
    ],
    label_visibility="collapsed"
)


# ============================================================
# PEGAWAI
# ============================================================

if role == "Pegawai":

    render_page_header(
        "Ruang Pengajuan",
        "Sistem validasi dokumen"
    )

    render_intro(
        "PENGAJUAN BARU",
        "Ajukan dokumen kepegawaian",
        "Lengkapi detail dan unggah PDF untuk memulai "
        "pemeriksaan awal."
    )

    st.markdown(
        """
        <div class="workflow-steps">
            <span class="workflow-step"><b>1</b> Detail</span>
            <span class="workflow-line"></span>
            <span class="workflow-step"><b>2</b> Dokumen</span>
            <span class="workflow-line"></span>
            <span class="workflow-step"><b>3</b> Validasi</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    detail_col, upload_col = st.columns(
        [1.2, 0.8],
        gap="large"
    )

    detail_panel = detail_col.container(
        border=True
    )

    upload_panel = upload_col.container(
        border=True
    )

    detail_panel.markdown(
        '<div class="section-heading">Detail Dokumen</div>'
        '<div class="section-copy">Isi data sesuai dengan dokumen '
        'yang akan diunggah.</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # CATEGORY
    # ========================================================

    kategori = detail_panel.selectbox(
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

        detail_panel.subheader(
            "Detail Kursus"
        )

        tanggal_kursus = detail_panel.text_input(
            "Tanggal Kursus",
            placeholder="Contoh: 13-04-2015"
        )

        tanggal_selesai = detail_panel.text_input(
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

        detail_panel.subheader(
            "Detail Diklat"
        )

        tanggal = detail_panel.text_input(
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

        detail_panel.subheader(
            "Detail Jabatan"
        )

        jabatan = detail_panel.text_input(
            "Jabatan Fungsional Umum",
            placeholder=(
                "Contoh: Kepala Bidang "
                "Pengendalian Penduduk"
            )
        )

        nomor_sk = detail_panel.text_input(
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

        detail_panel.subheader(
            "Detail Golongan"
        )

        golongan = detail_panel.text_input(
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

        detail_panel.subheader(
            "Dokumen PNS"
        )

        detail_panel.info(
            "Silakan upload dokumen pengangkatan "
            "Pegawai Negeri Sipil."
        )

        detail = {}


    # --------------------------------------------------------
    # CPNS
    # --------------------------------------------------------

    elif kategori == "CPNS":

        detail_panel.subheader(
            "Dokumen CPNS"
        )

        detail_panel.info(
            "Silakan upload dokumen pengangkatan "
            "Calon Pegawai Negeri Sipil."
        )

        detail = {}


    # ========================================================
    # FILE UPLOAD
    # ========================================================

    upload_panel.markdown(
        '<div class="section-heading">Unggah Dokumen</div>'
        '<div class="section-copy">Gunakan satu berkas PDF untuk '
        'setiap pengajuan.</div>',
        unsafe_allow_html=True
    )

    if st.session_state.uploaded_pdf is None:

        uploaded_file = upload_panel.file_uploader(
            "Dokumen PDF",
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

        upload_panel.markdown(
            f"""
            <div class="uploaded-file-card">
                <b>{uploaded_file["name"]}</b><br>
                <small>{file_size_mb:.2f} MB</small>
            </div>
            """,
            unsafe_allow_html=True
        )

        if upload_panel.button(
            "Hapus File"
        ):

            st.session_state.uploaded_pdf = None
            st.session_state.uploader_version += 1
            st.rerun()

        upload_panel.caption(
            "Untuk mengganti dokumen, hapus file ini terlebih dahulu."
        )


    # ========================================================
    # VALIDATION BUTTON
    # ========================================================

    ui_lock = st.empty()

    submit_clicked = upload_panel.button(
        "Validasi & Ajukan Dokumen",
        type="primary",
        use_container_width=True
    )

    if submit_clicked:

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
                    "Menyiapkan dokumen..."
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
                    "Membaca isi dokumen..."
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
                    "Dokumen berhasil dibaca."
                )

                status_box.empty()


                # =============================================
                # STEP 3 - VALIDASI
                # =============================================

                progress_bar.progress(
                    85
                )

                progress_text.write(
                    "Memeriksa kesesuaian dokumen..."
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
                    "Pemeriksaan dokumen selesai."
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
                            "Dokumen Anda telah diajukan "
                            "kepada admin untuk ditinjau "
                            "lebih lanjut."
                        )


                    else:

                        st.error(
                            "Maaf, dokumen Anda "
                            "tidak dapat diajukan."
                        )

                        st.write(
                            "**Alasan:**",
                            reason
                        )


            except Exception as e:

                progress_text.write(
                    "Proses gagal."
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


    render_page_header(
        "Ruang Verifikasi",
        f"{total} dokumen tercatat"
    )

    render_intro(
        "DASHBOARD ADMIN",
        "Verifikasi dokumen",
        "Pantau status dan tinjau hasil pemeriksaan otomatis."
    )


    # ========================================================
    # METRIC
    # ========================================================

    col1, col2, col3, col4, col5 = st.columns(
        5,
        gap="small"
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

    filter_col, result_col = st.columns(
        [0.45, 0.55],
        gap="large"
    )

    filter_status = filter_col.selectbox(
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

    result_col.markdown(
        f'<div class="result-count">Menampilkan '
        f'<strong>{len(data_pengajuan)} dokumen</strong></div>',
        unsafe_allow_html=True
    )


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

                status_icon = "Menunggu"


            elif (
                item["status"]
                ==
                "DITERIMA ADMIN"
            ):

                status_icon = "Diterima"


            else:

                status_icon = "Ditolak"


            title = (
                f"{item['nama_file']}  |  "
                f"{item['kategori']}  |  "
                f"{status_icon}"
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
                    "Data Hasil Ekstraksi"
                ):

                    st.json(
                        item["extracted"]
                    )


                # =============================================
                # SIMILARITY
                # =============================================

                if item["similarity"]:

                    with st.expander(
                        "Hasil Similarity"
                    ):

                        st.json(
                            item["similarity"]
                        )


                # =============================================
                # OCR
                # =============================================

                with st.expander(
                    "Hasil OCR"
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
                    "**Nama File:**",
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
                        "Akses Dokumen Asli",

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
                                "Download PDF"
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
                            "Tutup Akses PDF",

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
                            "Terima Dokumen",

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
                            "Tolak Dokumen",

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
                        "Dokumen telah diterima "
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
                        "Dokumen telah ditolak "
                        "oleh admin."
                    )

                    st.write(
                        "**Alasan Admin:**",
                        item["alasan_admin"]
                    )
