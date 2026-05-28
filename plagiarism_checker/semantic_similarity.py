from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

# ============================================
# LOAD MODEL
# ============================================

model = SentenceTransformer(

    'all-MiniLM-L6-v2'
)

# ============================================
# SEMANTIC SIMILARITY
# ============================================

def semantic_similarity(

    text1,

    text2
):

    # ================================
    # EMPTY TEXT CHECK
    # ================================

    if not text1 or not text2:

        return 0.0

    # ================================
    # LIMIT HUGE TEXTS
    # ================================

    text1 = text1[:1000]

    text2 = text2[:1000]

    # ================================
    # CREATE EMBEDDINGS
    # ================================

    embeddings = model.encode(

        [text1, text2]
    )

    # ================================
    # COSINE SIMILARITY
    # ================================

    similarity = cosine_similarity(

        [embeddings[0]],

        [embeddings[1]]
    )[0][0]

    # ================================
    # CONVERT TO %
    # ================================

    score = float(

        similarity * 100
    )

    return round(

        score,

        2
    )