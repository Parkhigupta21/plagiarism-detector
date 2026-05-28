from django.urls import path

from . import views


urlpatterns = [

    # =====================================
    # DASHBOARD
    # =====================================

    path(
        'dashboard/',
        views.dashboard_view,
        name='dashboard'
    ),

    # =====================================
    # UPLOAD DOCUMENT
    # =====================================

    path(
        'upload/',
        views.upload_view,
        name='upload'
    ),

    # =====================================
    # LATEST RESULT
    # =====================================

    path(
        'results/',
        views.results_view,
        name='results'
    ),

    # =====================================
    # ALL USER DOCUMENTS
    # =====================================

    path(
        'my-documents/',
        views.my_documents_view,
        name='my_documents'
    ),

    # =====================================
    # OPEN DOCUMENT
    # =====================================

    path(
        'document/<str:doc_id>/',
        views.open_document_view,
        name='open_document'
    ),

    # =====================================
    # DELETE DOCUMENT
    # =====================================

    path(
        'delete-document/<str:doc_id>/',
        views.delete_doc_view,
        name='delete_document'
    ),

    # =====================================
    # API TEXT COMPARISON
    # =====================================

    path(
        'compare/',
        views.compare_api_view,
        name='compare_api'
    ),

    # =====================================
    # ALL RESULTS
    # =====================================

    path(
        'all-results/',
        views.all_results_view,
        name='all_results'
    ),
]