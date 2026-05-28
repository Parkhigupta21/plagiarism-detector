import logging
import json

from django.shortcuts import (
    render,
    redirect
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib import messages

from django.http import (
    JsonResponse,
    HttpResponseRedirect
)

from django.views.decorators.http import (
    require_POST
)

from django.core.files.storage import (
    FileSystemStorage
)

from .web_checker import (
    global_plagiarism_check
)

from .utils import (

    save_document,

    get_all_documents,

    save_plagiarism_result,

    get_results_by_user,

    get_documents_by_user,

    get_user_stats,

    delete_document,

    get_document_by_id,
)

from .gemini_service import (

    analyze_plagiarism,

    compare_two_texts,
)

from .file_utils import (

    extract_text_from_file,

    validate_file,
)

logger = logging.getLogger(__name__)


# ============================================
# DASHBOARD
# ============================================

@login_required
def dashboard_view(request):

    stats = get_user_stats(
        request.user.id
    )

    return render(

        request,

        "plagiarism_checker/dashboard.html",

        {
            "stats": stats
        }
    )


# ============================================
# UPLOAD VIEW
# ============================================

@login_required
def upload_view(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get(
            "document"
        )

        # ================================
        # NO FILE
        # ================================

        if not uploaded_file:

            messages.error(

                request,

                "Please upload a file."
            )

            return redirect(
                "upload"
            )

        try:

            # ================================
            # VALIDATE FILE
            # ================================

            validate_file(
                uploaded_file
            )

            # ================================
            # EXTRACT TEXT
            # ================================

            text, file_type = extract_text_from_file(
                uploaded_file
            )

            # ================================
            # RESET FILE POINTER
            # IMPORTANT
            # ================================

            uploaded_file.seek(0)

            # ================================
            # SAVE FILE PHYSICALLY
            # ================================

            fs = FileSystemStorage()

            saved_name = fs.save(

                uploaded_file.name,

                uploaded_file
            )

            file_url = fs.url(
                saved_name
            )

            # ================================
            # SAVE DOCUMENT TO DATABASE
            # ================================

            doc_id = save_document(

                user_id=request.user.id,

                username=request.user.username,

                filename=uploaded_file.name,

                content=text,

                file_type=file_type,

                file_path=file_url
            )

            # ================================
            # FETCH EXISTING DOCUMENTS
            # ================================

            existing_docs = get_all_documents(

                exclude_id=doc_id
            )

            # ================================
            # LOCAL DATABASE ANALYSIS
            # ================================

            analysis = analyze_plagiarism(

                text,

                existing_docs
            )

            # ================================
            # GLOBAL INTERNET ANALYSIS
            # ================================

            global_results = global_plagiarism_check(

                text
            )

            # ================================
            # FINAL SCORE
            # ================================

            final_score = max(

                analysis["overall_score"],

                global_results["overall_score"]
            )

            # ================================
            # SAVE RESULT
            # ================================

            save_plagiarism_result(

                user_id=request.user.id,

                username=request.user.username,

                source_doc_id=doc_id,

                source_filename=uploaded_file.name,

                comparisons=analysis[
                    "comparisons"
                ],

                overall_score=final_score,

                summary=analysis[
                    "summary"
                ],
            )

            # ================================
            # SUCCESS MESSAGE
            # ================================

            messages.success(

                request,

                "Document uploaded and analyzed successfully."
            )

            return redirect(
                "results"
            )

        except Exception as e:

            logger.exception(e)

            messages.error(

                request,

                str(e)
            )

    return render(

        request,

        "plagiarism_checker/upload.html"
    )


# ============================================
# RESULTS VIEW
# ============================================

@login_required
def results_view(request):

    results = get_results_by_user(
        request.user.id
    )

    latest_result = (

        results[0]

        if results

        else None
    )

    return render(

        request,

        "plagiarism_checker/results.html",

        {
            "result": latest_result
        }
    )


# ============================================
# MY DOCUMENTS VIEW
# ============================================

@login_required
def my_documents_view(request):

    documents = get_documents_by_user(
        request.user.id
    )

    return render(

        request,

        "plagiarism_checker/my_documents.html",

        {
            "documents": documents
        }
    )


# ============================================
# OPEN DOCUMENT
# ============================================

@login_required
def open_document_view(

    request,

    doc_id
):

    document = get_document_by_id(
        doc_id
    )

    # ================================
    # DOCUMENT NOT FOUND
    # ================================

    if not document:

        messages.error(

            request,

            "Document not found."
        )

        return redirect(
            "my_documents"
        )

    file_path = document.get(
        "file_path"
    )

    # ================================
    # FILE PATH MISSING
    # ================================

    if not file_path:

        messages.error(

            request,

            "File path missing."
        )

        return redirect(
            "my_documents"
        )

    return HttpResponseRedirect(
        file_path
    )


# ============================================
# DELETE DOCUMENT
# ============================================

@login_required
@require_POST
def delete_doc_view(

    request,

    doc_id
):

    delete_document(

        doc_id,

        request.user.id
    )

    messages.success(

        request,

        "Document deleted successfully."
    )

    return redirect(
        "my_documents"
    )


# ============================================
# TEXT COMPARISON API
# ============================================

@login_required
@require_POST
def compare_api_view(request):

    try:

        body = json.loads(
            request.body
        )

        text_a = body.get(
            "text_a",
            ""
        )

        text_b = body.get(
            "text_b",
            ""
        )

        result = compare_two_texts(

            text_a,

            text_b
        )

        return JsonResponse(
            result
        )

    except Exception as e:

        logger.exception(e)

        return JsonResponse({

            "error": str(e)
        })


# ============================================
# ALL RESULTS VIEW
# ============================================

@login_required
def all_results_view(request):

    results = get_results_by_user(
        request.user.id
    )

    return render(

        request,

        "plagiarism_checker/all_results.html",

        {
            "results": results
        }
    )