from extractor import extract_by_category

from rules import validate_document

from similarity import (
    compare_jabatan,
    compare_pns_context,
    compare_cpns_context
)


# ============================================================
# NORMALISASI KATEGORI
# ============================================================

def normalize_category(kategori):

    if kategori is None:
        return ""

    kategori = (
        str(kategori)
        .lower()
        .strip()
    )

    aliases = {
        "kursus": "kursus",

        "diklat": "diklat",

        "jabatan": "jabatan",

        "golongan": "golongan",
        "dokumen golongan": "golongan",

        "pns": "pns",
        "dokumen pns": "pns",

        "cpns": "cpns",
        "dokumen cpns": "cpns"
    }

    return aliases.get(
        kategori,
        kategori
    )


# ============================================================
# SIMILARITY
# ============================================================

def enrich_similarity(
    kategori,
    detail,
    extracted
):

    similarity_result = {}


    # ========================================================
    # JABATAN
    # ========================================================

    if kategori == "jabatan":

        jabatan_detail = detail.get(
            "jabatan_fungsional_umum",
            ""
        )

        jabatan_document = extracted.get(
            "jabatan",
            ""
        )


        if (
            jabatan_detail
            and jabatan_document
        ):

            similarity_result[
                "jabatan"
            ] = compare_jabatan(
                jabatan_detail,
                jabatan_document
            )


    # ========================================================
    # PNS
    # ========================================================

    elif kategori == "pns":

        pns_context = extracted.get(
            "pns_context",
            {}
        )

        context_text = pns_context.get(
            "context"
        )


        if context_text:

            similarity_result[
                "pns"
            ] = compare_pns_context(
                context_text
            )


    # ========================================================
    # CPNS
    # ========================================================

    elif kategori == "cpns":

        cpns_context = extracted.get(
            "cpns_context",
            {}
        )

        context_text = cpns_context.get(
            "context"
        )


        if context_text:

            similarity_result[
                "cpns"
            ] = compare_cpns_context(
                context_text
            )


    return similarity_result


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    kategori,
    ocr_text,
    detail
):

    # ========================================================
    # 1. NORMALISASI KATEGORI
    # ========================================================

    kategori = normalize_category(
        kategori
    )


    if not kategori:

        return {
            "success": False,
            "status": "ERROR",
            "reason": (
                "Kategori belum diberikan."
            )
        }


    # ========================================================
    # 2. CEK KATEGORI VALID
    # ========================================================

    valid_categories = {
        "kursus",
        "diklat",
        "jabatan",
        "golongan",
        "pns",
        "cpns"
    }


    if kategori not in valid_categories:

        return {
            "success": False,
            "status": "ERROR",
            "reason": (
                f"Kategori '{kategori}' "
                f"tidak dikenali."
            )
        }


    # ========================================================
    # 3. CEK OCR TEXT
    # ========================================================

    if (
        not ocr_text
        or not str(ocr_text).strip()
    ):

        return {
            "success": False,
            "status": "ERROR",
            "reason": (
                "OCR text kosong."
            )
        }


    # ========================================================
    # 4. CEK DETAIL
    # ========================================================

    if not isinstance(
        detail,
        dict
    ):

        return {
            "success": False,
            "status": "ERROR",
            "reason": (
                "Detail harus berbentuk dictionary."
            )
        }


    # ========================================================
    # 5. EXTRACTOR
    # ========================================================

    try:

        extracted = extract_by_category(
            kategori,
            ocr_text
        )

    except Exception as e:

        return {
            "success": False,
            "status": "ERROR",
            "stage": "extractor",
            "reason": str(e)
        }


    # ========================================================
    # 6. SIMILARITY
    # ========================================================

    try:

        similarity = enrich_similarity(
            kategori,
            detail,
            extracted
        )

    except Exception as e:

        return {
            "success": False,
            "status": "ERROR",
            "stage": "similarity",
            "reason": str(e),
            "extracted": extracted
        }


    # ========================================================
    # 7. RULES
    # ========================================================
    #
    # PENTING:
    #
    # Similarity sekarang ikut dikirim ke rules.py.
    #
    # Sebelumnya hanya:
    #
    # validate_document(
    #     kategori,
    #     detail,
    #     extracted
    # )
    #
    # Sekarang menjadi:
    #
    # validate_document(
    #     kategori,
    #     detail,
    #     extracted,
    #     similarity
    # )
    #
    # ========================================================

    try:

        validation = validate_document(
            kategori,
            detail,
            extracted,
            similarity
        )

    except Exception as e:

        return {
            "success": False,
            "status": "ERROR",
            "stage": "rules",
            "reason": str(e),
            "extracted": extracted,
            "similarity": similarity
        }


    # ========================================================
    # 8. FINAL RESULT
    # ========================================================

    return {
        "success": True,

        "kategori": kategori,

        "status": validation.get(
            "status"
        ),

        "valid": validation.get(
            "valid"
        ),

        "reason": validation.get(
            "reason"
        ),

        "extracted": extracted,

        "similarity": similarity,

        "validation": validation
    }


# ============================================================
# PRINT HASIL PIPELINE
# ============================================================

def print_pipeline_result(result):

    print("\n")
    print("=" * 60)
    print("HASIL DOCUMENT VALIDATION")
    print("=" * 60)


    # ========================================================
    # ERROR
    # ========================================================

    if not result.get(
        "success"
    ):

        print(
            "Pipeline : ERROR"
        )

        print(
            "Stage    :",
            result.get(
                "stage",
                "-"
            )
        )

        print(
            "Reason   :",
            result.get(
                "reason"
            )
        )

        print(
            "=" * 60
        )

        return


    # ========================================================
    # STATUS
    # ========================================================

    print(
        "Kategori :",
        result.get(
            "kategori"
        )
    )

    print(
        "Status   :",
        result.get(
            "status"
        )
    )

    print(
        "Valid    :",
        result.get(
            "valid"
        )
    )

    print(
        "Reason   :",
        result.get(
            "reason"
        )
    )


    # ========================================================
    # EXTRACTED
    # ========================================================

    print(
        "\n--- Extracted Data ---"
    )

    print(
        result.get(
            "extracted"
        )
    )


    # ========================================================
    # SIMILARITY
    # ========================================================

    print(
        "\n--- Similarity ---"
    )

    similarity = result.get(
        "similarity",
        {}
    )


    if similarity:

        print(
            similarity
        )

    else:

        print(
            "Tidak digunakan untuk kategori ini."
        )


    # ========================================================
    # VALIDATION
    # ========================================================

    print(
        "\n--- Validation Detail ---"
    )

    print(
        result.get(
            "validation"
        )
    )


    print(
        "=" * 60
    )