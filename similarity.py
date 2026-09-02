import re

from difflib import SequenceMatcher


# ============================================================
# NORMALISASI
# ============================================================

def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SEQUENCE SIMILARITY
# ============================================================

def similarity_score(
    text_a,
    text_b
):

    text_a = normalize_text(
        text_a
    )

    text_b = normalize_text(
        text_b
    )


    if not text_a or not text_b:
        return 0.0


    return SequenceMatcher(
        None,
        text_a,
        text_b
    ).ratio()


# ============================================================
# WORD SIMILARITY
# ============================================================

def word_similarity(
    text_a,
    text_b
):

    text_a = normalize_text(
        text_a
    )

    text_b = normalize_text(
        text_b
    )


    if not text_a or not text_b:
        return 0.0


    words_a = set(
        text_a.split()
    )

    words_b = set(
        text_b.split()
    )


    intersection = (
        words_a.intersection(
            words_b
        )
    )

    union = (
        words_a.union(
            words_b
        )
    )


    if not union:
        return 0.0


    return (
        len(intersection)
        /
        len(union)
    )


# ============================================================
# COMBINED
# ============================================================

def combined_similarity(
    text_a,
    text_b
):

    sequence = similarity_score(
        text_a,
        text_b
    )

    word = word_similarity(
        text_a,
        text_b
    )


    final_score = (
        sequence + word
    ) / 2


    return round(
        final_score,
        4
    )


# ============================================================
# GENERAL COMPARE
# ============================================================

def compare_text(
    text_a,
    text_b,
    threshold=None
):

    score = combined_similarity(
        text_a,
        text_b
    )


    result = {
        "text_a": text_a,
        "text_b": text_b,
        "score": score,
        "percentage": round(
            score * 100,
            2
        )
    }


    if threshold is not None:

        result["threshold"] = threshold

        result["passed"] = (
            score >= threshold
        )


    return result


# ============================================================
# JABATAN
# ============================================================

def compare_jabatan(
    jabatan_detail,
    jabatan_document,
    threshold=None
):

    return compare_text(
        jabatan_detail,
        jabatan_document,
        threshold
    )


# ============================================================
# PNS
# ============================================================

def compare_pns_context(
    text_document,
    threshold=None
):

    references = [
        "mengangkat menjadi pegawai negeri sipil",
        "diangkat menjadi pegawai negeri sipil",
        "pengangkatan pegawai negeri sipil"
    ]


    best_score = 0.0
    best_reference = None


    for reference in references:

        score = combined_similarity(
            text_document,
            reference
        )

        if score > best_score:

            best_score = score
            best_reference = reference


    result = {
        "score": best_score,

        "percentage": round(
            best_score * 100,
            2
        ),

        "best_reference": best_reference
    }


    if threshold is not None:

        result["threshold"] = threshold

        result["passed"] = (
            best_score >= threshold
        )


    return result


# ============================================================
# CPNS
# ============================================================

def compare_cpns_context(
    text_document,
    threshold=None
):

    references = [
        "mengangkat sebagai calon pegawai negeri sipil",
        "diangkat sebagai calon pegawai negeri sipil",
        "pengangkatan calon pegawai negeri sipil"
    ]


    best_score = 0.0
    best_reference = None


    for reference in references:

        score = combined_similarity(
            text_document,
            reference
        )

        if score > best_score:

            best_score = score
            best_reference = reference


    result = {
        "score": best_score,

        "percentage": round(
            best_score * 100,
            2
        ),

        "best_reference": best_reference
    }


    if threshold is not None:

        result["threshold"] = threshold

        result["passed"] = (
            best_score >= threshold
        )


    return result