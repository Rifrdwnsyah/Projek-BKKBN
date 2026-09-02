# ocr.py

import os

# ============================================================
# ENVIRONMENT CONFIG
# ============================================================

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"


# ============================================================
# IMPORT
# ============================================================

import io
import re
from collections import Counter

import pymupdf
import numpy as np

from PIL import Image
from paddleocr import PaddleOCR


# ============================================================
# INISIALISASI PADDLEOCR
# ============================================================

print("Menyiapkan PaddleOCR...")

ocr = PaddleOCR(
    lang="en",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

print("PaddleOCR siap.")


# ============================================================
# CEK KUALITAS TEXT LAYER
# ============================================================

def is_text_layer_usable(text, min_length=100):
    """
    Mengecek apakah text layer PDF benar-benar berguna.
    """

    if not text:
        return False

    text = str(text).strip()

    if len(text) < min_length:
        return False

    letters = re.findall(
        r"[A-Za-z]",
        text
    )

    letter_ratio = (
        len(letters) / len(text)
        if len(text) > 0
        else 0
    )

    if letter_ratio < 0.35:
        return False

    words = re.findall(
        r"[A-Za-z]{3,}",
        text.lower()
    )

    if len(words) < 15:
        return False

    unique_words = set(
        words
    )

    unique_ratio = (
        len(unique_words) / len(words)
        if words
        else 0
    )

    if unique_ratio < 0.25:
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) >= 5:

        unique_lines = set(
            lines
        )

        line_ratio = (
            len(unique_lines) / len(lines)
        )

        if line_ratio < 0.35:
            return False

    return True


# ============================================================
# NORMALISASI BARIS UNTUK DETEKSI NOISE
# ============================================================

def normalize_noise_line(line):
    """
    Normalisasi ringan agar variasi watermark seperti:

    31/08/2026,08.39.51
    31/08/2026.08.39.51
    |31/08/2026,08.39.51

    bisa dianggap sebagai pola yang sama.
    """

    line = str(line).lower().strip()

    # Hilangkan spasi
    line = re.sub(
        r"\s+",
        "",
        line
    )

    # Samakan pemisah umum
    line = line.replace(
        ",",
        "."
    )

    # Buang karakter pinggir/noise
    line = re.sub(
        r"^[|:;_\-]+",
        "",
        line
    )

    line = re.sub(
        r"[|:;_\-]+$",
        "",
        line
    )

    return line


# ============================================================
# DETEKSI TIMESTAMP WATERMARK
# ============================================================

def is_timestamp_noise(text):
    """
    Mendeteksi timestamp scanner/watermark.

    Contoh:
    31/08/2026,08.39.51
    31/08/2026.08.39.51
    """

    text = str(text).strip()

    pattern = (
        r"\d{1,2}/\d{1,2}/\d{4}"
        r"\s*[,.\-]?\s*"
        r"\d{1,2}[.:]\d{2}[.:]\d{2}"
    )

    return bool(
        re.search(
            pattern,
            text
        )
    )


# ============================================================
# CEK APAKAH BARIS DIDOMINASI ANGKA
# ============================================================

def is_numeric_heavy(line):
    """
    Digunakan hanya sebagai indikator tambahan.
    Tidak otomatis menghapus NIP.
    """

    line = str(line).strip()

    if not line:
        return False

    digits = len(
        re.findall(
            r"\d",
            line
        )
    )

    letters = len(
        re.findall(
            r"[A-Za-z]",
            line
        )
    )

    total = len(line)

    if total == 0:
        return False

    digit_ratio = digits / total

    return (
        digit_ratio >= 0.75
        and letters <= 2
    )


# ============================================================
# BERSIHKAN WATERMARK / NOISE OCR
# ============================================================

def clean_ocr_noise(text, min_repeat=3):
    """
    Membersihkan noise hasil OCR berdasarkan:

    1. timestamp scanner
    2. baris yang muncul berulang
    3. fragmen angka repetitif
    4. simbol OCR yang menempel di awal baris

    Penting:
    NIP / nomor SK / tanggal asli tidak dihapus hanya
    karena berbentuk angka.
    """

    if not text:
        return ""

    raw_lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    # ========================================================
    # NORMALISASI UNTUK MENGHITUNG PENGULANGAN
    # ========================================================

    normalized_lines = [
        normalize_noise_line(line)
        for line in raw_lines
    ]

    counts = Counter(
        normalized_lines
    )


    # ========================================================
    # DETEKSI FRAGMEN NUMERIK REPETITIF
    # ========================================================

    repeated_numeric_tokens = Counter()

    for line in raw_lines:

        numeric_tokens = re.findall(
            r"\d{6,}",
            line
        )

        for token in numeric_tokens:

            repeated_numeric_tokens[
                token
            ] += 1


    repeated_numeric_noise = {
        token
        for token, count
        in repeated_numeric_tokens.items()
        if count >= min_repeat
    }


    # ========================================================
    # CLEANING BARIS
    # ========================================================

    clean_lines = []

    for original_line in raw_lines:

        line = original_line.strip()

        normalized = normalize_noise_line(
            line
        )


        # ----------------------------------------------------
        # 1. HEADER HALAMAN JANGAN DIHAPUS
        # ----------------------------------------------------

        if line.startswith(
            "===== HALAMAN"
        ):

            clean_lines.append(
                line
            )

            continue


        # ----------------------------------------------------
        # 2. HAPUS TIMESTAMP DI DALAM BARIS
        # ----------------------------------------------------

        timestamp_pattern = (
            r"\d{1,2}/\d{1,2}/\d{4}"
            r"\s*[,.\-]?\s*"
            r"\d{1,2}[.:]\d{2}[.:]\d{2}"
        )

        line = re.sub(
            timestamp_pattern,
            " ",
            line
        )


        # ----------------------------------------------------
        # 3. HAPUS FRAGMEN ANGKA YANG TERBUKTI BERULANG
        # ----------------------------------------------------

        for token in repeated_numeric_noise:

            line = line.replace(
                token,
                " "
            )


        # ----------------------------------------------------
        # 4. RAPIIKAN SIMBOL AWAL
        # ----------------------------------------------------

        line = re.sub(
            r"^[|;:_]+\s*",
            "",
            line
        )

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        line = line.strip()


        if not line:
            continue


        # ----------------------------------------------------
        # 5. HAPUS BARIS IDENTIK YANG BERULANG
        # ----------------------------------------------------

        normalized_after = normalize_noise_line(
            line
        )

        if (
            counts.get(
                normalized_after,
                0
            )
            >= min_repeat
        ):

            # Jangan otomatis hapus kalau terlihat seperti
            # teks dokumen normal
            words = re.findall(
                r"[A-Za-z]{3,}",
                line
            )

            if (
                len(words) <= 2
                or is_numeric_heavy(line)
                or is_timestamp_noise(line)
            ):

                continue


        # ----------------------------------------------------
        # 6. HAPUS BARIS YANG SETELAH CLEANING HANYA
        #    ANGKA PENDEK / FRAGMEN WATERMARK
        # ----------------------------------------------------

        if re.fullmatch(
            r"\d{5,12}",
            line
        ):

            # Hanya hapus jika angka ini juga muncul berulang
            if any(
                line in token
                or token in line
                for token in repeated_numeric_noise
            ):

                continue


        clean_lines.append(
            line
        )


    # ========================================================
    # HILANGKAN DUPLIKAT NOISE BERDEKATAN
    # ========================================================

    final_lines = []

    previous_normalized = None

    for line in clean_lines:

        current_normalized = (
            normalize_noise_line(
                line
            )
        )

        # Jangan tampilkan baris identik dua kali berturut
        if (
            current_normalized
            and current_normalized
            == previous_normalized
        ):

            continue

        final_lines.append(
            line
        )

        previous_normalized = (
            current_normalized
        )


    final_text = "\n".join(
        final_lines
    )

    final_text = re.sub(
        r"\n{3,}",
        "\n\n",
        final_text
    )

    return final_text.strip()


# ============================================================
# AMBIL HASIL PADDLEOCR
# ============================================================

def get_rec_texts(result):

    if not result:
        return []

    try:

        texts = result[0][
            "rec_texts"
        ]

        if texts:
            return texts

    except Exception:
        pass

    try:

        texts = (
            result[0]
            .json["res"]["rec_texts"]
        )

        if texts:
            return texts

    except Exception:
        pass

    return []


# ============================================================
# OCR SATU HALAMAN
# ============================================================

def ocr_page(
    page,
    nomor_halaman,
    dpi=200
):

    print(
        f"Menjalankan PaddleOCR halaman "
        f"{nomor_halaman}..."
    )

    pix = page.get_pixmap(
        dpi=dpi
    )

    img_bytes = pix.tobytes(
        "png"
    )

    image = Image.open(
        io.BytesIO(
            img_bytes
        )
    ).convert(
        "RGB"
    )

    image_np = np.array(
        image
    )

    print(
        "Ukuran gambar:",
        image_np.shape
    )

    result = ocr.predict(
        image_np
    )

    texts = get_rec_texts(
        result
    )

    clean_texts = []

    for text in texts:

        text = str(
            text
        ).strip()

        if text:

            clean_texts.append(
                text
            )

    return clean_texts


# ============================================================
# FUNCTION UTAMA
# ============================================================

def extract_text_from_pdf(
    pdf_path,
    min_text_length=100,
    dpi=200
):

    if not os.path.exists(
        pdf_path
    ):

        raise FileNotFoundError(
            f"File '{pdf_path}' tidak ditemukan."
        )


    print("\n" + "=" * 60)
    print("HYBRID DOCUMENT READER")
    print("=" * 60)


    try:

        doc = pymupdf.open(
            pdf_path
        )

    except Exception as e:

        raise RuntimeError(
            f"PDF gagal dibuka: {e}"
        )


    jumlah_halaman = len(
        doc
    )


    print(
        f"Jumlah halaman: "
        f"{jumlah_halaman}"
    )


    all_texts = []

    jumlah_text_layer = 0
    jumlah_ocr = 0


    # ========================================================
    # LOOP SEMUA HALAMAN
    # ========================================================

    for page_index in range(
        jumlah_halaman
    ):

        nomor_halaman = (
            page_index + 1
        )


        print("\n" + "-" * 60)

        print(
            f"Memproses halaman "
            f"{nomor_halaman}/"
            f"{jumlah_halaman}"
        )

        print("-" * 60)


        page = doc[
            page_index
        ]


        # ====================================================
        # COBA TEXT LAYER
        # ====================================================

        try:

            direct_text = (
                page.get_text(
                    "text"
                )
                .strip()
            )

        except Exception:

            direct_text = ""


        usable_text_layer = (
            is_text_layer_usable(
                direct_text,
                min_length=min_text_length
            )
        )


        # ====================================================
        # TEXT LAYER VALID
        # ====================================================

        if usable_text_layer:

            print(
                "Text layer valid ditemukan."
            )

            print(
                f"Jumlah karakter: "
                f"{len(direct_text)}"
            )

            print(
                "PaddleOCR dilewati."
            )


            all_texts.append(
                f"===== HALAMAN "
                f"{nomor_halaman} ====="
            )

            all_texts.append(
                direct_text
            )

            all_texts.append(
                ""
            )


            jumlah_text_layer += 1


        # ====================================================
        # FALLBACK KE OCR
        # ====================================================

        else:

            if direct_text:

                print(
                    "Text layer ditemukan, "
                    "tetapi kualitasnya buruk."
                )

            else:

                print(
                    "Text layer tidak ditemukan."
                )


            print(
                "Fallback ke PaddleOCR..."
            )


            try:

                texts = ocr_page(
                    page=page,
                    nomor_halaman=nomor_halaman,
                    dpi=dpi
                )

            except Exception as e:

                print(
                    f"OCR halaman "
                    f"{nomor_halaman} gagal: {e}"
                )

                continue


            if not texts:

                print(
                    f"Tidak ada teks yang "
                    f"berhasil dikenali pada "
                    f"halaman {nomor_halaman}."
                )

                continue


            all_texts.append(
                f"===== HALAMAN "
                f"{nomor_halaman} ====="
            )

            all_texts.extend(
                texts
            )

            all_texts.append(
                ""
            )


            jumlah_ocr += 1


            print(
                f"OCR halaman "
                f"{nomor_halaman} selesai."
            )


    # ========================================================
    # TUTUP PDF
    # ========================================================

    doc.close()


    # ========================================================
    # GABUNGKAN RAW OCR
    # ========================================================

    raw_text = "\n".join(
        all_texts
    )


    if not raw_text.strip():

        raise RuntimeError(
            "Tidak ada teks yang berhasil dibaca."
        )


    # ========================================================
    # CLEAN WATERMARK / NOISE
    # ========================================================

    print(
        "Membersihkan watermark / noise..."
    )

    final_text = clean_ocr_noise(
        raw_text,
        min_repeat=3
    )


    if not final_text.strip():

        raise RuntimeError(
            "Tidak ada teks yang tersisa "
            "setelah proses cleaning."
        )


    # ========================================================
    # INFO
    # ========================================================

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)

    print(
        f"Text layer : "
        f"{jumlah_text_layer} halaman"
    )

    print(
        f"PaddleOCR  : "
        f"{jumlah_ocr} halaman"
    )

    print(
        f"Raw chars  : "
        f"{len(raw_text)}"
    )

    print(
        f"Clean chars: "
        f"{len(final_text)}"
    )

    print("=" * 60)


    return final_text


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    PDF_PATH = "dokumen.pdf"
    OUTPUT_PATH = "hasil_ocr.txt"


    try:

        ocr_text = extract_text_from_pdf(
            pdf_path=PDF_PATH,
            min_text_length=100,
            dpi=200
        )


        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                ocr_text
            )


        print(
            f"Hasil OCR disimpan ke: "
            f"{OUTPUT_PATH}"
        )


    except Exception as e:

        print(
            f"ERROR: {e}"
        )