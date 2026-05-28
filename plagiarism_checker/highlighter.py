import re
from difflib import SequenceMatcher

from .semantic_similarity import (
    semantic_similarity
)

# ============================================
# SPLIT TEXT INTO CHUNKS
# ============================================

def split_chunks(

    text,

    chunk_size=400
):

    text = text.replace("\n", " ")

    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:

        current_chunk.append(word)

        current_length += len(word)

        if current_length >= chunk_size:

            chunks.append(

                " ".join(current_chunk)
            )

            current_chunk = []

            current_length = 0

    if current_chunk:

        chunks.append(

            " ".join(current_chunk)
        )

    return chunks
# ============================================
# FIND SIMILAR SENTENCES
# ============================================

def find_similar_sentences(

    text_a,

    text_b,

    threshold=40
):

    matches = []

    sentences_a = split_chunks(
        text_a
    )[:8]

    sentences_b = split_chunks(
        text_b
    )[:8]

    # ========================================
    # COMPARE SENTENCE BY SENTENCE
    # ========================================

    for sentence_a in sentences_a:

        for sentence_b in sentences_b:

            score = semantic_similarity(

                sentence_a,

                sentence_b
            )

            if score >= threshold:

                matches.append({

                    "text_a":
                        sentence_a,

                    "text_b":
                        sentence_b,

                    "score":
                        float(score)
                })

    # ========================================
    # SORT BY SCORE
    # ========================================

    matches.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    return matches[:3]
# ============================================
# SMART WORD HIGHLIGHTING
# ============================================

def highlight_matching_words(

    text_a,

    text_b
):

    words_a = text_a.split()

    words_b = text_b.split()

    common_words = set()

    # ========================================
    # FIND COMMON IMPORTANT WORDS
    # ========================================

    for word in words_a:

        cleaned = word.lower().strip(
            ".,!?()[]{}:;"
        )

        if (

            cleaned in [
                w.lower().strip(
                    ".,!?()[]{}:;"
                )
                for w in words_b
            ]

            and len(cleaned) > 4
        ):

            common_words.add(cleaned)

    # ========================================
    # HIGHLIGHT TEXT A
    # ========================================

    highlighted_a = []

    for word in words_a:

        cleaned = word.lower().strip(
            ".,!?()[]{}:;"
        )

        if cleaned in common_words:

            highlighted_a.append(

                f"<mark>{word}</mark>"
            )

        else:

            highlighted_a.append(word)

    # ========================================
    # HIGHLIGHT TEXT B
    # ========================================

    highlighted_b = []

    for word in words_b:

        cleaned = word.lower().strip(
            ".,!?()[]{}:;"
        )

        if cleaned in common_words:

            highlighted_b.append(

                f"<mark>{word}</mark>"
            )

        else:

            highlighted_b.append(word)

    return {

        "text_a":
            " ".join(highlighted_a),

        "text_b":
            " ".join(highlighted_b)
    }