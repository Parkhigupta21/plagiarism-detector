from pymongo import MongoClient

from django.conf import settings

from bson.objectid import ObjectId

from datetime import datetime


# ============================================
# GLOBAL DATABASE VARIABLE
# ============================================

_db = None


# ============================================
# DATABASE CONNECTION
# ============================================

def get_db():

    global _db

    if _db is None:

        client = MongoClient(
            settings.MONGODB_URI
        )

        _db = client[
            settings.MONGODB_DB
        ]

    return _db


# ============================================
# SAVE DOCUMENT
# ============================================

def save_document(
    user_id,
    username,
    filename,
    content,
    file_type,
    file_path=None
):

    db = get_db()

    document = {

        "user_id":
            user_id,

        "username":
            username,

        "filename":
            filename,

        "content":
            content,

        "file_type":
            file_type,

        "file_path":
            file_path,

        "created_at":
            datetime.utcnow(),
    }

    result = db.documents.insert_one(
        document
    )

    return str(
        result.inserted_id
    )


# ============================================
# GET SINGLE DOCUMENT
# ============================================

def get_document_by_id(doc_id):

    db = get_db()

    document = db.documents.find_one({

        "_id":
            ObjectId(doc_id)
    })

    if document:

        document["id"] = str(
            document["_id"]
        )

    return document


# ============================================
# GET ALL DOCUMENTS
# ============================================

def get_all_documents(exclude_id=None):

    db = get_db()

    query = {}

    if exclude_id:

        query["_id"] = {

            "$ne":
                ObjectId(exclude_id)
        }

    documents = list(
        db.documents.find(query)
    )

    # Convert MongoDB _id to id
    for doc in documents:

        doc["id"] = str(
            doc["_id"]
        )

    return documents


# ============================================
# SAVE PLAGIARISM RESULT
# ============================================

def save_plagiarism_result(
    user_id,
    username,
    source_doc_id,
    source_filename,
    comparisons,
    overall_score,
    summary,
):

    db = get_db()

    result_data = {

        "user_id":
            user_id,

        "username":
            username,

        "source_doc_id":
            source_doc_id,

        "source_filename":
            source_filename,

        "comparisons":
            comparisons,

        "overall_score":
            overall_score,

        "summary":
            summary,

        "created_at":
            datetime.utcnow(),
    }

    result = db.results.insert_one(
        result_data
    )

    return str(
        result.inserted_id
    )


# ============================================
# GET RESULT BY ID
# ============================================

def get_result_by_id(result_id):

    db = get_db()

    result = db.results.find_one({

        "_id":
            ObjectId(result_id)
    })

    if result:

        result["id"] = str(
            result["_id"]
        )

    return result


# ============================================
# GET RESULTS BY USER
# ============================================

def get_results_by_user(user_id):

    db = get_db()

    results = list(

        db.results.find({

            "user_id":
                user_id

        }).sort(

            "created_at",
            -1
        )
    )

    # Convert _id to id
    for result in results:

        result["id"] = str(
            result["_id"]
        )

    return results


# ============================================
# GET DOCUMENTS BY USER
# ============================================

def get_documents_by_user(user_id):

    db = get_db()

    documents = list(

        db.documents.find({

            "user_id":
                user_id

        }).sort(

            "created_at",
            -1
        )
    )

    # Convert _id into normal id
    for doc in documents:

        doc["id"] = str(
            doc["_id"]
        )

    return documents


# ============================================
# USER DASHBOARD STATS
# ============================================

def get_user_stats(user_id):

    db = get_db()

    total_documents = db.documents.count_documents({

        "user_id":
            user_id
    })

    total_checks = db.results.count_documents({

        "user_id":
            user_id
    })

    results = list(

        db.results.find({

            "user_id":
                user_id
        })
    )

    if results:

        scores = [

            r.get(
                "overall_score",
                0
            )

            for r in results
        ]

        average_score = round(

            sum(scores) / len(scores),

            2
        )

        highest_score = max(
            scores
        )

    else:

        average_score = 0

        highest_score = 0

    return {

        "total_documents":
            total_documents,

        "total_checks":
            total_checks,

        "average_score":
            average_score,

        "highest_score":
            highest_score,
    }


# ============================================
# DELETE DOCUMENT
# ============================================

def delete_document(
    doc_id,
    user_id
):

    db = get_db()

    db.documents.delete_one({

        "_id":
            ObjectId(doc_id),

        "user_id":
            user_id
    })