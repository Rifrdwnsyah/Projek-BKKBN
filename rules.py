import re
from difflib import SequenceMatcher


# ============================================================
# HELPER
# ============================================================

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower()

    # Rapikan whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_sk(text):
    """
    Normalisasi Nomor SK.

    Contoh:
    1031/III/PEG/2011
    1031/III/Peg/2011

    Keduanya dianggap sama.
    """

    if text is None:
        return ""

    text = str(text).upper()

    # Hilangkan semua spasi
    text = re.sub(
        r"\s+",
        "",
        text
    )

    return text.strip()


def normalize_golongan(text):
    if text is None:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"\s+",
        "",
        text
    )

    return text.lower()


def extract_year_from_date(date_text):
    """
    Contoh:

    13-08-2009 -> 2009
    """

    if not date_text:
        return None

    match = re.search(
        r"\b(?:19|20)\d{2}\b",
        str(date_text)
    )

    if match:
        return match.group(0)

    return None


# ============================================================
# SIMILARITY HELPER
# ============================================================

def calculate_text_similarity(text_a, text_b):
    """
    Menghitung similarity sederhana sebagai fallback.

    Digunakan jika similarity dari similarity.py
    belum dikirim ke rules.py.
    """

    text_a = normalize_text(text_a)
    text_b = normalize_text(text_b)

    if not text_a or not text_b:
        return 0.0

    return SequenceMatcher(
        None,
        text_a,
        text_b
    ).ratio()


# ============================================================
# KURSUS
# ============================================================

def validate_kursus(detail, extracted):
    """
    Rule Kursus:

    - Yang diperiksa hanya TAHUN.
    - Hari dan bulan tidak diperiksa.
    - Jika tanggal diinput, tahun input harus
      ditemukan pada dokumen.
    """

    document_dates = extracted.get(
        "dates",
        []
    )

    tanggal_kursus = detail.get(
        "tanggal_kursus"
    )

    tanggal_selesai = detail.get(
        "tanggal_selesai_kursus"
    )


    # ========================================================
    # TIDAK ADA INPUT
    # ========================================================

    if not tanggal_kursus and not tanggal_selesai:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Tanggal kursus belum diberikan."
            )
        }


    # ========================================================
    # AMBIL TAHUN DOKUMEN
    # ========================================================

    document_years = []

    for date in document_dates:

        date = str(
            date
        ).strip()

        parts = date.split(
            "-"
        )

        if len(parts) == 3:

            year = parts[-1]

            if year not in document_years:

                document_years.append(
                    year
                )


    # ========================================================
    # AMBIL TAHUN INPUT
    # ========================================================

    detail_years = []

    if tanggal_kursus:

        parts = str(
            tanggal_kursus
        ).strip().split(
            "-"
        )

        if len(parts) == 3:

            detail_years.append(
                parts[-1]
            )


    if tanggal_selesai:

        parts = str(
            tanggal_selesai
        ).strip().split(
            "-"
        )

        if len(parts) == 3:

            detail_years.append(
                parts[-1]
            )


    if not detail_years:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Format tanggal kursus "
                "tidak dapat dibaca."
            )
        }


    # ========================================================
    # VALIDASI TAHUN
    # ========================================================

    for year in detail_years:

        if year not in document_years:

            return {
                "valid": False,
                "status": "DITOLAK",
                "reason": (
                    f"Tahun kursus {year} "
                    f"tidak sesuai dengan dokumen."
                )
            }


    return {
        "valid": True,
        "status": "DIAJUKAN KE ADMIN",
        "reason": (
            "Tahun kursus sesuai dengan dokumen "
            f"({', '.join(detail_years)})."
        )
    }


# ============================================================
# DIKLAT
# ============================================================

def validate_diklat(
    detail,
    extracted
):

    tanggal = detail.get(
        "tanggal"
    )


    detail_year = extract_year_from_date(
        tanggal
    )


    # ========================================================
    # TAHUN DETAIL TIDAK ADA
    # ========================================================

    if not detail_year:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Tahun Diklat tidak ditemukan "
                "pada detail."
            )
        }


    document_years = extracted.get(
        "years",
        []
    )


    # ========================================================
    # TAHUN SESUAI
    # ========================================================

    if detail_year in document_years:

        return {
            "valid": True,
            "status": "DIAJUKAN KE ADMIN",
            "reason": (
                f"Tahun Diklat {detail_year} "
                f"ditemukan pada dokumen."
            )
        }


    # ========================================================
    # TAHUN TIDAK SESUAI
    # ========================================================

    return {
        "valid": False,
        "status": "DITOLAK",
        "reason": (
            f"Tahun Diklat {detail_year} "
            f"tidak ditemukan pada dokumen."
        )
    }


# ============================================================
# JABATAN
# ============================================================

def validate_jabatan(
    detail,
    extracted,
    similarity=None
):
    """
    Rule Jabatan:

    1. Nomor SK harus sesuai setelah normalisasi.
    2. Jabatan tidak wajib 100% sama.
    3. Jabatan menggunakan similarity.
    4. Threshold sementara = 80%.
    5. Huruf besar/kecil tidak berpengaruh.

    Contoh:

    Input:
    Kepala Sub Bidang Analis Dampak Kependudukan

    Dokumen:
    Kepala Sub Bidang Analisis Dampak Kependudukan

    Tetap dapat lolos jika similarity >= 80%.
    """


    # ========================================================
    # DATA JABATAN
    # ========================================================

    detail_jabatan = normalize_text(
        detail.get(
            "jabatan_fungsional_umum"
        )
    )

    document_jabatan = normalize_text(
        extracted.get(
            "jabatan"
        )
    )


    # ========================================================
    # DATA NOMOR SK
    # ========================================================

    detail_sk = normalize_sk(
        detail.get(
            "nomor_sk"
        )
    )

    document_sk = normalize_sk(
        extracted.get(
            "nomor_sk"
        )
    )


    # ========================================================
    # CEK INPUT JABATAN
    # ========================================================

    if not detail_jabatan:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Jabatan belum diberikan."
            )
        }


    # ========================================================
    # CEK INPUT NOMOR SK
    # ========================================================

    if not detail_sk:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Nomor SK belum diberikan."
            )
        }


    # ========================================================
    # CEK JABATAN HASIL EKSTRAKSI
    # ========================================================

    if not document_jabatan:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Jabatan tidak berhasil "
                "ditemukan pada dokumen."
            )
        }


    # ========================================================
    # CEK NOMOR SK HASIL EKSTRAKSI
    # ========================================================

    if not document_sk:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Nomor SK tidak berhasil "
                "ditemukan pada dokumen."
            )
        }


    # ========================================================
    # CEK NOMOR SK
    #
    # 1031/III/PEG/2011
    # dan
    # 1031/III/Peg/2011
    #
    # dianggap sama karena normalize_sk()
    # mengubah semuanya menjadi uppercase.
    # ========================================================

    sk_match = (
        detail_sk
        ==
        document_sk
    )


    if not sk_match:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Nomor SK tidak sesuai."
            )
        }


    # ========================================================
    # AMBIL SIMILARITY DARI PIPELINE
    # ========================================================

    jabatan_score = None


    if similarity:

        jabatan_similarity = similarity.get(
            "jabatan",
            {}
        )


        try:

            jabatan_score = float(
                jabatan_similarity.get(
                    "score",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            jabatan_score = None


    # ========================================================
    # FALLBACK SIMILARITY
    #
    # Kalau pipeline belum mengirim similarity,
    # hitung langsung di rules.py.
    # ========================================================

    if (
        jabatan_score is None
        or jabatan_score <= 0
    ):

        jabatan_score = calculate_text_similarity(
            detail_jabatan,
            document_jabatan
        )


    # ========================================================
    # THRESHOLD JABATAN
    # ========================================================

    JABATAN_THRESHOLD = 0.80


    # ========================================================
    # JABATAN TIDAK CUKUP MIRIP
    # ========================================================

    if jabatan_score < JABATAN_THRESHOLD:

        return {
            "valid": False,
            "status": "DITOLAK",
            "reason": (
                "Jabatan tidak sesuai "
                f"(similarity "
                f"{jabatan_score * 100:.2f}%)."
            )
        }


    # ========================================================
    # LOLOS
    # ========================================================

    return {
        "valid": True,
        "status": "DIAJUKAN KE ADMIN",
        "reason": (
            "Nomor SK sesuai dan jabatan "
            f"memiliki similarity "
            f"{jabatan_score * 100:.2f}%."
        )
    }


# ============================================================
# GOLONGAN
# ============================================================

def validate_golongan(
    detail,
    extracted
):

    detail_golongan = normalize_golongan(
        detail.get(
            "golongan"
        )
    )

    document_golongan = normalize_golongan(
        extracted.get(
            "golongan_baru"
        )
    )


    if (
        detail_golongan
        and
        document_golongan
        and
        detail_golongan
        ==
        document_golongan
    ):

        return {
            "valid": True,
            "status": "DIAJUKAN KE ADMIN",
            "reason": (
                f"Golongan "
                f"{detail.get('golongan')} "
                f"sesuai dengan dokumen."
            )
        }


    return {
        "valid": False,
        "status": "DITOLAK",
        "reason": (
            "Golongan tidak sesuai "
            "dengan dokumen."
        )
    }


# ============================================================
# PNS
# ============================================================

def validate_pns(
    detail,
    extracted
):

    pns_context = extracted.get(
        "pns_context",
        {}
    )


    found = pns_context.get(
        "found",
        False
    )


    if found:

        return {
            "valid": True,
            "status": "DIAJUKAN KE ADMIN",
            "reason": (
                "Konteks pengangkatan PNS "
                "ditemukan pada dokumen."
            )
        }


    return {
        "valid": False,
        "status": "DITOLAK",
        "reason": (
            "Konteks pengangkatan PNS "
            "tidak ditemukan pada dokumen."
        )
    }


# ============================================================
# CPNS
# ============================================================

def validate_cpns(
    detail,
    extracted
):

    cpns_context = extracted.get(
        "cpns_context",
        {}
    )


    found = cpns_context.get(
        "found",
        False
    )


    if found:

        return {
            "valid": True,
            "status": "DIAJUKAN KE ADMIN",
            "reason": (
                "Konteks pengangkatan CPNS "
                "ditemukan pada dokumen."
            )
        }


    return {
        "valid": False,
        "status": "DITOLAK",
        "reason": (
            "Konteks pengangkatan CPNS "
            "tidak ditemukan pada dokumen."
        )
    }


# ============================================================
# VALIDASI BERDASARKAN KATEGORI
# ============================================================

def validate_document(
    kategori,
    detail,
    extracted,
    similarity=None
):

    kategori = (
        str(kategori)
        .lower()
        .strip()
    )


    # ========================================================
    # KURSUS
    # ========================================================

    if kategori == "kursus":

        return validate_kursus(
            detail,
            extracted
        )


    # ========================================================
    # DIKLAT
    # ========================================================

    elif kategori == "diklat":

        return validate_diklat(
            detail,
            extracted
        )


    # ========================================================
    # JABATAN
    # ========================================================

    elif kategori == "jabatan":

        return validate_jabatan(
            detail,
            extracted,
            similarity
        )


    # ========================================================
    # GOLONGAN
    # ========================================================

    elif kategori == "golongan":

        return validate_golongan(
            detail,
            extracted
        )


    # ========================================================
    # PNS
    # ========================================================

    elif kategori == "pns":

        return validate_pns(
            detail,
            extracted
        )


    # ========================================================
    # CPNS
    # ========================================================

    elif kategori == "cpns":

        return validate_cpns(
            detail,
            extracted
        )


    # ========================================================
    # UNKNOWN
    # ========================================================

    return {
        "valid": False,
        "status": "ERROR",
        "reason": (
            f"Kategori '{kategori}' "
            f"tidak dikenali."
        )
    }