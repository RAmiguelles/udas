from django.urls import path
from rest_framework import routers

from ..document.api import DocumentViewSet, AttachmentViewSet, AttributeViewSet, KeywordViewSet, \
    CommentViewSet, DocumentDirectoryViewSet, TypeViewSet, request_to_publicize, request_all_to_publicize,approve_to_publicize_guest, approve_to_unpublicize_guest, get_document_details_guest,request_to_approved_guest,approve_to_publicize_global_guest,approve_to_unpublicize_global_guest, \
    approve_to_publicize, reject_to_publicize, get_requested_to_publicize, get_document_details, copy_document, \
    link_document, unlink_document, cut_document, cancel_request_all_to_publicize, upload_attachment, document_directory, get_actions, get_monitoring,cancel_request_all_to_publicize_guest
from ..document.suggestions import get_attribute_key_suggestions, get_attribute_value_suggestions, \
    get_keyword_suggestions, get_type_suggestions

router = routers.DefaultRouter()
router.register('attachment', AttachmentViewSet)
router.register('attribute', AttributeViewSet)
router.register('keyword', KeywordViewSet)
router.register('type', TypeViewSet)
router.register('comment', CommentViewSet)
router.register('document-directory', DocumentDirectoryViewSet)
router.register('', DocumentViewSet)

urlpatterns = [
    # SUGGESTIONS
    path('suggestion/attribute/key', get_attribute_key_suggestions),
    path('suggestion/attribute/value', get_attribute_value_suggestions),
    path('suggestion/keyword', get_keyword_suggestions),
    path('suggestion/type', get_type_suggestions),

    # PUBLICITY
    path('publicize/request', request_to_publicize),
    path('publicize/request-all', request_all_to_publicize),
    path('publicize/request-cancel', cancel_request_all_to_publicize),
    path('publicize/approve', approve_to_publicize),
    path('publicize/reject', reject_to_publicize),
    path('publicize/requested', get_requested_to_publicize),
    # Added by Mats 
    path('publicize/request-guest',approve_to_publicize_guest),
    path('publicize/request-cancel-guest',approve_to_unpublicize_guest),
    
    path('publicize/request-approved-guest',request_to_approved_guest),
    path('publicize/request-cancel-publicize-guests', cancel_request_all_to_publicize_guest),

    path('publicize/request-global-guest',approve_to_publicize_global_guest),
    path('publicize/request-cancel-global-guest',approve_to_unpublicize_global_guest),

    path('details', get_document_details),
    path('guests-details', get_document_details_guest), # Added by Mats
    path('copy', copy_document),
    path('link', link_document),
    path('cut', cut_document),
    path('unlink', unlink_document),
    path('document_directory', document_directory),
    path('attachment/upload/', upload_attachment),
    path('actions', get_actions),
    path('monitoring', get_monitoring),
]

urlpatterns += router.urls
