"""
AI Semantic Plagiarism Service
"""

import logging

from django.conf import settings

from google import genai

from .semantic_similarity import (
    semantic_similarity
)

from .highlighter import (
    find_similar_sentences,
    highlight_matching_words
)

logger = logging.getLogger(__name__)


# ============================================
# CONFIGURE GEMINI CLIENT
# ============================================

try:

    client = genai.Client(

        api_key=settings.GEMINI_API_KEY
    )

    print(

        "Gemini client initialized successfully."
    )

except Exception as e:

    logger.exception(e)

    print(

        f"Gemini initialization failed: {e}"
    )

    client = None


# ============================================
# INTERNAL GEMINI CALL
# ============================================

def _call_gemini(prompt):

    if client is None:

        raise RuntimeError(

            "Gemini client not initialized."
        )

    response = client.models.generate_content(

        model="gemini-2.0-flash",

        contents=prompt
    )

    return response.text


# ============================================
# COMPARE TWO TEXTS
# ============================================

def compare_two_texts(

    text_a,

    text_b
):

    try:

        # ================================
        # EMPTY TEXT CHECK
        # ================================

        if not text_a or not text_b:

            return {

                "similarity_score": 0.0,

                "summary":
                    "One or both documents are empty.",

                "matches": []
            }

        # ================================
        # LIMIT LARGE TEXTS
        # ================================

        text_a = text_a[:5000]

        text_b = text_b[:5000]

        # ================================
        # SEMANTIC SIMILARITY
        # ================================

        similarity_score = semantic_similarity(

            text_a,

            text_b
        )

        similarity_score = float(
            similarity_score
        )

        # ================================
        # DEFAULT SUMMARY
        # ================================

        if similarity_score > 75:

            summary = (

                "Very high semantic similarity "
                "detected."
            )

        elif similarity_score > 40:

            summary = (

                "Moderate similarity detected "
                "between documents."
            )

        elif similarity_score > 15:

            summary = (

                "Low similarity detected."
            )

        else:

            summary = (

                "Documents appear mostly unique."
            )

        # ================================
        # OPTIONAL GEMINI ANALYSIS
        # ================================

        try:

            prompt = f"""
Analyze semantic plagiarism similarity.

TEXT A:
{text_a[:1000]}

TEXT B:
{text_b[:1000]}

Explain briefly:
- copied meaning
- paraphrasing
- shared concepts
- rewritten content

Maximum 80 words.
"""

            raw = _call_gemini(prompt)

            if raw and raw.strip():

                summary = raw.strip()

        except Exception as gemini_error:

            logger.warning(

                f"Gemini analysis failed: "
                f"{gemini_error}"
            )

        # ================================
        # FIND SIMILAR SENTENCES
        # ================================

        matches = find_similar_sentences(

            text_a,

            text_b
        )

        # ================================
        # HIGHLIGHT MATCHING WORDS
        # ================================
        highlighted_matches = []
        for match in matches:

            highlighted = highlight_matching_words(

                match["text_a"],

                match["text_b"]
            )

            highlighted_matches.append({

        "score":
            float(match["score"]),

        "text_a":
            highlighted["text_a"],

        "text_b":
            highlighted["text_b"]
    })

        # ================================
        # RETURN RESULT
        # ================================

        return {

            "similarity_score":
                float(similarity_score),

            "summary":
                summary,

            "matches":
                highlighted_matches
        }

    except Exception as e:

        logger.exception(e)

        return {

            "similarity_score": 0.0,

            "summary":
                f"Comparison failed: {e}",

            "matches": []
        }


# ============================================
# ANALYZE PLAGIARISM
# ============================================

def analyze_plagiarism(

    uploaded_text,

    existing_documents
):

    comparisons = []

    highest_score = 0.0

    # ================================
    # NO DOCUMENTS
    # ================================

    if not existing_documents:

        return {

            "overall_score": 0.0,

            "summary":
                "No existing documents available "
                "for comparison.",

            "comparisons": []
        }

    # ================================
    # DOCUMENT COMPARISON LOOP
    # ================================

    for doc in existing_documents:

        try:

            existing_text = doc.get(

                "content",

                ""
            )

            # ============================
            # SKIP EMPTY DOCUMENTS
            # ============================

            if not existing_text:

                continue

            result = compare_two_texts(

                uploaded_text,

                existing_text
            )

            score = float(

                result.get(
                    "similarity_score",
                    0
                )
            )

            comparisons.append({

                "filename":
                    doc.get(
                        "filename",
                        "Unknown"
                    ),

                "score":
                    float(score),

                "summary":
                    result.get(
                        "summary",
                        ""
                    ),

                "matches":
                    result.get(
                        "matches",
                        []
                    )
            })

            # ============================
            # TRACK HIGHEST SCORE
            # ============================

            if score > highest_score:

                highest_score = float(score)

        except Exception as e:

            logger.exception(e)

    # ================================
    # SORT COMPARISONS
    # ================================

    comparisons.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    # ================================
    # FINAL SUMMARY
    # ================================

    if highest_score > 75:

        overall_summary = (

            "High plagiarism detected."
        )

    elif highest_score > 40:

        overall_summary = (

            "Moderate plagiarism detected."
        )

    elif highest_score > 15:

        overall_summary = (

            "Low plagiarism detected."
        )

    else:

        overall_summary = (

            "Document appears mostly original."
        )

    # ================================
    # RETURN FINAL RESULT
    # ================================

    return {

        "overall_score":
            float(highest_score),

        "summary":
            overall_summary,

        "comparisons":
            comparisons
    }