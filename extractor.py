import re
from datetime import datetime


# ============================================================
# BULAN INDONESIA
# ============================================================

MONTHS_ID = {
    "januari": "01",
    "februari": "02",
    "maret": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "agustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "desember": "12",
}


# ============================================================
# HELPER
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_date(
    day,
    month,
    year
):
    """
    Mengubah tanggal menjadi:
    DD-MM-YYYY
    """

    day = str(
        day
    ).zfill(2)

    if (
        isinstance(month, str)
        and not month.isdigit()
    ):

        month = MONTHS_ID.get(
            month.lower()
        )

    if month is None:
        return None

    month = str(
        month
    ).zfill(2)

    return (
        f"{day}-{month}-{year}"
    )


def is_valid_date(date_string):
    """
    Validasi tanggal kalender.
    """

    if not date_string:
        return False

    try:

        datetime.strptime(
            date_string,
            "%d-%m-%Y"
        )

        return True

    except ValueError:

        return False


# ============================================================
# HELPER GOLONGAN
# ============================================================

def normalize_roman_golongan(value):
    """
    Normalisasi hasil OCR golongan.

    Contoh:
    III/b  -> III/b
    iii/B  -> III/b
    IlI/b  -> III/b
    lII/b  -> III/b
    1II/b  -> III/b

    Golongan valid:
    I/a - IV/e
    """

    if not value:
        return None

    value = str(
        value
    ).strip()

    value = re.sub(
        r"\s+",
        "",
        value
    )

    if "/" not in value:
        return None

    parts = value.split(
        "/",
        1
    )

    if len(parts) != 2:
        return None

    roman = parts[0]

    letter = parts[1]


    # ========================================================
    # NORMALISASI OCR
    # ========================================================

    roman = (
        roman
        .replace("l", "I")
        .replace("L", "I")
        .replace("1", "I")
        .replace("i", "I")
        .replace("v", "V")
        .replace("x", "X")
        .upper()
    )

    letter = (
        letter
        .strip()
        .lower()
    )


    # ========================================================
    # VALIDASI ROMAWI
    # ========================================================

    valid_roman = {
        "I",
        "II",
        "III",
        "IV"
    }

    valid_letters = {
        "a",
        "b",
        "c",
        "d",
        "e"
    }


    if roman not in valid_roman:
        return None

    if letter not in valid_letters:
        return None


    return (
        f"{roman}/{letter}"
    )


def build_golongan(
    roman,
    letter
):
    """
    Membentuk dan menormalisasi golongan
    dari hasil regex.
    """

    if not roman or not letter:
        return None

    return normalize_roman_golongan(
        f"{roman}/{letter}"
    )


# ============================================================
# KURSUS
# ============================================================

def extract_dates(text):
    """
    Mengambil tanggal dari dokumen.

    Mendukung:

    22-02-2021
    22/02/2021
    22 Februari 2021
    22 - 26 Februari 2021
    13 s/d 17 April 2015
    """

    results = []

    text_lower = str(
        text
    ).lower()

    month_names = "|".join(
        MONTHS_ID.keys()
    )


    # ========================================================
    # 1. FORMAT NUMERIK
    # ========================================================

    numeric_pattern = (
        r"\b"
        r"(\d{1,2})"
        r"[-/]"
        r"(\d{1,2})"
        r"[-/]"
        r"(\d{4})"
        r"\b"
    )

    matches = re.findall(
        numeric_pattern,
        text
    )

    for (
        day,
        month,
        year
    ) in matches:

        date = normalize_date(
            day,
            month,
            year
        )

        if (
            date
            and is_valid_date(date)
        ):

            results.append(
                date
            )


    # ========================================================
    # 2. FORMAT INDONESIA
    # ========================================================

    indo_pattern = (
        rf"\b"
        rf"(\d{{1,2}})"
        rf"\s+"
        rf"({month_names})"
        rf"\s+"
        rf"(\d{{4}})"
        rf"\b"
    )

    matches = re.findall(
        indo_pattern,
        text_lower,
        re.IGNORECASE
    )


    for (
        day,
        month,
        year
    ) in matches:

        date = normalize_date(
            day,
            month,
            year
        )

        if (
            date
            and is_valid_date(date)
        ):

            results.append(
                date
            )


    # ========================================================
    # 3. RANGE TANGGAL
    # ========================================================

    range_patterns = [

        # 22 - 26 Februari 2021
        (
            rf"\b"
            rf"(\d{{1,2}})"
            rf"\s*[-–—]\s*"
            rf"(\d{{1,2}})"
            rf"\s*"
            rf"({month_names})"
            rf"\s+"
            rf"(\d{{4}})"
            rf"\b"
        ),


        # 13 s/d 17 April 2015
        (
            rf"\b"
            rf"(\d{{1,2}})"
            rf"\s*"
            rf"(?:"
            rf"s\s*/\s*d"
            rf"|s\.?\s*d\.?"
            rf"|sampai(?:\s+dengan)?"
            rf"|hingga"
            rf")"
            rf"\s*"
            rf"(\d{{1,2}})"
            rf"\s*"
            rf"({month_names})"
            rf"\s+"
            rf"(\d{{4}})"
            rf"\b"
        )
    ]


    for range_pattern in range_patterns:

        matches = re.findall(
            range_pattern,
            text_lower,
            re.IGNORECASE
        )


        for (
            start_day,
            end_day,
            month,
            year
        ) in matches:

            start_date = normalize_date(
                start_day,
                month,
                year
            )

            end_date = normalize_date(
                end_day,
                month,
                year
            )


            if (
                start_date
                and is_valid_date(
                    start_date
                )
            ):

                results.append(
                    start_date
                )


            if (
                end_date
                and is_valid_date(
                    end_date
                )
            ):

                results.append(
                    end_date
                )


    # ========================================================
    # HAPUS DUPLIKAT
    # ========================================================

    return list(
        dict.fromkeys(
            results
        )
    )


# ============================================================
# DIKLAT
# ============================================================

def extract_diklat_years(text):
    """
    Mengambil tahun Diklat berdasarkan konteks.

    Tidak mengambil semua tahun karena watermark OCR
    dapat menghasilkan banyak timestamp.
    """

    text_norm = normalize_text(
        text
    )

    years = []

    month_names = "|".join(
        MONTHS_ID.keys()
    )


    # ========================================================
    # Pelatihan ... Tahun 2022
    # ========================================================

    pattern_pelatihan = (
        r"pelatihan"
        r".{0,120}?"
        r"\btahun\s+"
        r"((?:19|20)\d{2})\b"
    )


    matches = re.findall(
        pattern_pelatihan,
        text_norm,
        re.IGNORECASE
    )

    years.extend(
        matches
    )


    # ========================================================
    # Periode pelatihan
    # ========================================================

    pattern_periode = (
        rf"(?:dari\s+tanggal\s+)?"
        rf"\d{{1,2}}\s+"
        rf"(?:{month_names})"
        rf"\s+"
        rf"(?:\d{{4}}\s+)?"
        rf".{{0,80}}?"
        rf"(?:"
        rf"sampai\s+dengan"
        rf"|s\.?\s*d\.?"
        rf"|hingga"
        rf")"
        rf".{{0,30}}?"
        rf"\d{{1,2}}\s+"
        rf"(?:{month_names})\s+"
        rf"((?:19|20)\d{{2}})\b"
    )


    matches = re.findall(
        pattern_periode,
        text_norm,
        re.IGNORECASE
    )

    years.extend(
        matches
    )


    return list(
        dict.fromkeys(
            years
        )
    )


# ============================================================
# NOMOR SK
# ============================================================

def extract_nomor_sk(text):
    """
    Mengambil Nomor SK.
    """

    patterns = [

        (
            r"(?:nomor|no\.?)"
            r"\s*[:\-]?\s*"
            r"([A-Za-z0-9./\-]+)"
        ),

        (
            r"keputusan"
            r".{0,150}?"
            r"nomor"
            r"\s*[:\-]?\s*"
            r"([A-Za-z0-9./\-]+)"
        )
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            return (
                match
                .group(1)
                .strip()
            )


    return None


# ============================================================
# JABATAN
# ============================================================

def extract_jabatan(text):
    """
    Mengambil jabatan dengan prioritas
    pada konteks pengangkatan.
    """

    text_norm = normalize_text(
        text
    )


    patterns = [

        # ====================================================
        # Mengangkat ... sebagai Kepala ...
        # ====================================================

        (
            r"\bmengangkat\b"
            r".{0,500}?"
            r"\bsebagai\s+"
            r"(.{3,180}?)"
            r"(?="
            r"\s+perwakilan\b"
            r"|\s*,?\s*eselon\b"
            r"|\s+dengan\s+mendapat\b"
            r"|\.|$"
            r")"
        ),


        # ====================================================
        # Mengangkat kembali dalam Jabatan ...
        # ====================================================

        (
            r"\bmengangkat\s+"
            r"(?:kembali\s+)?"
            r"dalam\s+jabatan\s+"
            r"(.{3,180}?)"
            r"(?="
            r"\s+pada\s+"
            r"|\s+eselon\s+"
            r"|\.|,|$"
            r")"
        ),


        # ====================================================
        # Jabatan Baru
        # ====================================================

        (
            r"\bjabatan\s+baru"
            r"\s*[:\-]?\s*"
            r"(.{3,180}?)"
            r"(?=\.|,|$)"
        ),


        # ====================================================
        # Diangkat dalam jabatan
        # ====================================================

        (
            r"\bdiangkat\s+dalam\s+jabatan\s+"
            r"(.{3,180}?)"
            r"(?="
            r"\s+pada\s+"
            r"|\s+eselon\s+"
            r"|\.|,|$"
            r")"
        )
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text_norm,
            re.IGNORECASE | re.DOTALL
        )


        if match:

            jabatan = (
                match
                .group(1)
                .strip()
            )


            jabatan = re.sub(
                r"\s+",
                " ",
                jabatan
            )


            generic_phrases = [
                "sebagaimana tersebut",
                "sebagaimana dimaksud",
                "tersebut dalam keputusan",
                "yang bersangkutan"
            ]


            if any(
                phrase in jabatan
                for phrase
                in generic_phrases
            ):

                continue


            return jabatan


    return None


# ============================================================
# GOLONGAN BARU
# ============================================================

def extract_golongan_baru(text):
    """
    Mengambil GOLONGAN BARU.

    Prinsip:
    - Jangan mengambil Golongan Lama.
    - Prioritaskan kalimat keputusan.
    - Toleransi OCR:
      III/b
      IlI/b
      lII/b
      1II/b

    Contoh dokumen kenaikan:
    Gol.Ruang Lama = III/a
    dinaikkan ... golongan ruang III/b

    Hasil:
    III/b

    Contoh pengangkatan PNS:
    diangkat menjadi Pegawai Negeri Sipil
    dalam pangkat Pengatur Muda golongan ruang II/a

    Hasil:
    II/a
    """

    if not text:

        return None


    text_norm = normalize_text(
        text
    )


    # Regex romawi dibuat agak toleran OCR
    roman_pattern = (
        r"([iIlL1vVxX]{1,4})"
    )

    letter_pattern = (
        r"([a-eA-E])"
    )


    # ========================================================
    # PRIORITAS 1
    #
    # dinaikkan pangkatnya menjadi ...
    # golongan ruang III/b
    # ========================================================

    pattern = (
        r"dinaikkan\s+pangkatnya"
        r".{0,300}?"
        r"golongan\s+ruang"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 2
    #
    # pangkatnya menjadi ...
    # golongan ruang III/b
    # ========================================================

    pattern = (
        r"pangkatnya\s+menjadi"
        r".{0,300}?"
        r"golongan\s+ruang"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 3
    #
    # Terhitung mulai tanggal ...
    # dinaikkan pangkatnya menjadi ...
    # golongan ruang III/b
    # ========================================================

    pattern = (
        r"terhitung\s+mulai\s+tanggal"
        r".{0,400}?"
        r"(?:dinaikkan|naik)"
        r".{0,300}?"
        r"golongan\s+ruang"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 4
    #
    # GOLONGAN 2:
    #
    # diangkat menjadi Pegawai Negeri Sipil
    # dalam pangkat Pengatur Muda
    # golongan ruang II/a
    # ========================================================

    pattern = (
        r"diangkat\s+menjadi\s+"
        r"pegawai\s+negeri\s+sipil"
        r".{0,400}?"
        r"golongan\s+ruang"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 5
    #
    # diangkat menjadi PNS
    # dalam pangkat ...
    # golongan ...
    #
    # Lebih fleksibel jika OCR kehilangan kata "ruang"
    # ========================================================

    pattern = (
        r"diangkat\s+menjadi\s+"
        r"pegawai\s+negeri\s+sipil"
        r".{0,400}?"
        r"golongan"
        r"(?:\s+ruang)?"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 6
    #
    # Mengangkat menjadi PNS ...
    # Pangkat/Gol.Ruang ...
    # ========================================================

    pattern = (
        r"(?:mengangkat|diangkat)"
        r".{0,200}?"
        r"menjadi\s+pegawai\s+negeri\s+sipil"
        r".{0,400}?"
        r"(?:"
        r"pangkat\s*/?\s*gol\.?\s*ruang"
        r"|gol\.?\s*ruang"
        r"|golongan\s+ruang"
        r")"
        r".{0,100}?"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 7
    #
    # Pangkat/Gol.Ruang Baru : III/b
    # Golongan Baru : III/b
    # ========================================================

    patterns_baru = [

        (
            r"(?:"
            r"pangkat\s*/?\s*gol\.?\s*ruang"
            r"|gol\.?\s*ruang"
            r"|golongan\s+ruang"
            r")"
            r"\s+baru"
            r".{0,50}?"
            + roman_pattern +
            r"\s*/\s*"
            + letter_pattern
        ),

        (
            r"golongan\s+baru"
            r".{0,50}?"
            + roman_pattern +
            r"\s*/\s*"
            + letter_pattern
        )
    ]


    for pattern in patterns_baru:

        match = re.search(
            pattern,
            text_norm,
            re.IGNORECASE | re.DOTALL
        )


        if match:

            golongan = build_golongan(
                match.group(1),
                match.group(2)
            )

            if golongan:

                return golongan


    # ========================================================
    # PRIORITAS 8
    #
    # Cari konteks "menjadi"
    #
    # berguna jika OCR agak rusak tetapi:
    #
    # menjadi ... golongan ruang III/b
    # masih terbaca.
    # ========================================================

    pattern = (
        r"\bmenjadi\b"
        r".{0,350}?"
        r"golongan"
        r"(?:\s+ruang)?"
        r"\s*"
        + roman_pattern +
        r"\s*/\s*"
        + letter_pattern
    )


    match = re.search(
        pattern,
        text_norm,
        re.IGNORECASE | re.DOTALL
    )


    if match:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )

        if golongan:

            return golongan


    # ========================================================
    # PRIORITAS 9
    #
    # Cari semua kemunculan golongan.
    #
    # Tetapi buang yang berada dekat:
    # "lama", "golongan lama", "gol.ruang lama".
    # ========================================================

    general_pattern = (
        roman_pattern
        +
        r"\s*/\s*"
        +
        letter_pattern
    )


    matches = list(
        re.finditer(
            general_pattern,
            text_norm,
            re.IGNORECASE
        )
    )


    candidates = []


    for match in matches:

        golongan = build_golongan(
            match.group(1),
            match.group(2)
        )


        if not golongan:
            continue


        # Ambil konteks sebelum kandidat
        start = max(
            0,
            match.start() - 100
        )

        end = min(
            len(text_norm),
            match.end() + 100
        )


        context = text_norm[
            start:end
        ]


        # ====================================================
        # JIKA JELAS GOLONGAN LAMA, SKIP
        # ====================================================

        old_markers = [
            "gol.ruang lama",
            "gol. ruang lama",
            "golongan ruang lama",
            "golongan lama",
            "pangkat/gol.ruang lama",
            "pangkat/gol. ruang lama"
        ]


        if any(
            marker in context
            for marker
            in old_markers
        ):

            continue


        if golongan not in candidates:

            candidates.append(
                golongan
            )


    # ========================================================
    # FALLBACK
    #
    # Jika setelah membuang konteks lama masih ada kandidat,
    # gunakan kandidat terakhir.
    #
    # Dokumen kenaikan pangkat umumnya:
    #
    # III/a = lama
    # III/b = baru
    # ========================================================

    if candidates:

        return candidates[-1]


    return None


# ============================================================
# PNS
# ============================================================

def extract_pns_context(text):
    """
    Mendeteksi dokumen pengangkatan PNS.

    Penyebutan CPNS saja tidak boleh otomatis dianggap
    dokumen CPNS.
    """

    text_norm = normalize_text(
        text
    )


    patterns = [

        (
            r"\bmengangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bdiangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bpengangkatan\s+"
            r"calon\s+pegawai\s+negeri\s+sipil"
            r"\s+menjadi\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bcalon\s+pegawai\s+negeri\s+sipil"
            r".{0,100}?"
            r"menjadi\s+pegawai\s+negeri\s+sipil\b"
        )
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text_norm,
            re.IGNORECASE
        )


        if match:

            context = match.group(
                0
            )


            if (
                "sebagai calon pegawai negeri sipil"
                in context
            ):

                continue


            return {
                "found": True,
                "context": context
            }


    return {
        "found": False,
        "context": None
    }


# ============================================================
# CPNS
# ============================================================

def extract_cpns_context(text):
    """
    Mendeteksi dokumen CPNS.

    Prioritas:
    1. Exclude jika jelas dokumen pengangkatan PNS.
    2. Explicit CPNS.
    3. Context fallback.
    """

    text_norm = normalize_text(
        text
    )


    # ========================================================
    # 1. EXCLUDE PNS
    # ========================================================

    pns_patterns = [

        (
            r"\bpengangkatan\s+"
            r"calon\s+pegawai\s+negeri\s+sipil"
            r"\s+menjadi\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bmengangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bdiangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bcalon\s+pegawai\s+negeri\s+sipil"
            r".{0,100}?"
            r"menjadi\s+pegawai\s+negeri\s+sipil\b"
        )
    ]


    for pattern in pns_patterns:

        match = re.search(
            pattern,
            text_norm,
            re.IGNORECASE
        )


        if match:

            return {
                "found": False,
                "context": None,
                "method": (
                    "excluded_as_pns"
                ),
                "indicators": {}
            }


    # ========================================================
    # 2. EXPLICIT CPNS
    # ========================================================

    cpns_patterns = [

        (
            r"\bmengangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"calon\s+pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bdiangkat\s+"
            r"(?:sebagai|menjadi)\s+"
            r"calon\s+pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bmenjadi\s+"
            r"calon\s+pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bsebagai\s+"
            r"calon\s+pegawai\s+negeri\s+sipil\b"
        ),

        (
            r"\bcalon\s+pegawai\s+negeri\s+sipil"
            r".{0,80}?"
            r"masa\s+percobaan\b"
        )
    ]


    for pattern in cpns_patterns:

        match = re.search(
            pattern,
            text_norm,
            re.IGNORECASE
        )


        if match:

            return {
                "found": True,

                "context":
                    match.group(0),

                "method":
                    "explicit_pattern",

                "indicators": {
                    "calon_pns": True
                }
            }


    # ========================================================
    # 3. CONTEXT FALLBACK
    # ========================================================

    indicators = {

        "calon_pns": bool(
            re.search(
                r"\bcalon\s+pegawai\s+negeri\s+sipil\b",
                text_norm,
                re.IGNORECASE
            )
        ),


        "mengangkat": bool(
            re.search(
                r"\bmengangkat\b",
                text_norm,
                re.IGNORECASE
            )
        ),


        "golongan_ruang": bool(
            re.search(
                r"\bgolongan\s+ruang\b",
                text_norm,
                re.IGNORECASE
            )
        ),


        "masa_kerja": bool(
            re.search(
                r"\bmasa\s+kerja"
                r"(?:\s+golongan)?\b",
                text_norm,
                re.IGNORECASE
            )
        ),


        "jabatan": bool(
            re.search(
                r"\bjabatan\b",
                text_norm,
                re.IGNORECASE
            )
        ),


        "gaji_80": bool(
            re.search(
                r"\b80\s*%",
                text_norm,
                re.IGNORECASE
            )
        ),


        "masa_percobaan": bool(
            re.search(
                r"\bmasa\s+percobaan\b",
                text_norm,
                re.IGNORECASE
            )
        )
    }


    supporting_keys = [
        "mengangkat",
        "golongan_ruang",
        "masa_kerja",
        "jabatan",
        "gaji_80",
        "masa_percobaan"
    ]


    supporting_score = sum(
        1
        for key in supporting_keys
        if indicators[key]
    )


    if (
        indicators[
            "calon_pns"
        ]
        and supporting_score >= 3
    ):

        return {
            "found": True,

            "context": (
                "Konteks CPNS terdeteksi "
                "berdasarkan kombinasi "
                "indikator dokumen."
            ),

            "method":
                "context_fallback",

            "indicators":
                indicators,

            "supporting_score":
                supporting_score
        }


    return {
        "found": False,
        "context": None,
        "method": "not_found",
        "indicators": indicators,
        "supporting_score":
            supporting_score
    }


# ============================================================
# EXTRACT BERDASARKAN KATEGORI
# ============================================================

def extract_by_category(
    kategori,
    ocr_text
):
    """
    Router extractor berdasarkan kategori.
    """

    kategori = (
        str(kategori)
        .lower()
        .strip()
    )


    # ========================================================
    # KURSUS
    # ========================================================

    if kategori == "kursus":

        return {
            "dates": extract_dates(
                ocr_text
            )
        }


    # ========================================================
    # DIKLAT
    # ========================================================

    elif kategori == "diklat":

        return {
            "years":
                extract_diklat_years(
                    ocr_text
                )
        }


    # ========================================================
    # JABATAN
    # ========================================================

    elif kategori == "jabatan":

        return {
            "nomor_sk":
                extract_nomor_sk(
                    ocr_text
                ),

            "jabatan":
                extract_jabatan(
                    ocr_text
                )
        }


    # ========================================================
    # GOLONGAN
    # ========================================================

    elif kategori == "golongan":

        return {
            "golongan_baru":
                extract_golongan_baru(
                    ocr_text
                )
        }


    # ========================================================
    # PNS
    # ========================================================

    elif kategori == "pns":

        return {
            "pns_context":
                extract_pns_context(
                    ocr_text
                )
        }


    # ========================================================
    # CPNS
    # ========================================================

    elif kategori == "cpns":

        return {
            "cpns_context":
                extract_cpns_context(
                    ocr_text
                )
        }


    return {}