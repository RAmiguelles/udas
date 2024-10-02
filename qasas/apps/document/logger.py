from ..authentication.utils import get_client_ip, get_client_geo, get_user_by_token
from ..document.models import Log


def log(request, document, action, details):
    ip_address = get_client_ip(request)
    geo = get_client_geo(ip_address)
    Log.objects.create(
        user=get_user_by_token(request),
        document=document,
        action=action,
        details=details,
        ip_address=ip_address,
        country=geo['country'],
        city=geo['city'],
        latitude=geo['latitude'],
        longitude=geo['longitude'],
    )
    return


def get_document_info(document):
    attachments = []
    for attachment in document.attachments.all():
        attachments.append(attachment.id)
    attributes = []
    for attribute in document.attributes.all():
        attributes.append(attribute.id)
    keywords = []
    for keyword in document.keywords.all():
        keywords.append(keyword.id)
    details = {
        'id': document.id,
        'title': document.title,
        'description': document.description,
        'type': document.type,
        'is_public': document.is_public,
        'attachments': attachments,
        'attributes': attributes,
        'keywords': keywords,
    }
    return details


def append_document_log_details(details):
    log_details = ''

    if details['title']:
        log_details += ' | TITLE: {}'.format(details['title'])
    if details['description']:
        log_details += ' | DESCRIPTION: {}'.format(details['description'])
    if details['type']:
        log_details += ' | TYPE: {}'.format(details['type'])
    if details['is_public']:
        log_details += ' | IS PUBLIC: {}'.format(details['is_public'])

    log_details += append_document_attributes_log_details(details)
    return log_details


def append_document_attributes_log_details(details):
    log_details = ''

    attachments = ''
    if len(details['attachments']) > 0:
        for i, attachment in enumerate(details['attachments']):
            if i: attachments += ', '
            attachments += str(attachment)
        log_details += ' | ATTACHMENT ID: {}'.format(attachments)

    attributes = ''
    if len(details['attributes']) > 0:
        for i, attribute in enumerate(details['attributes']):
            if i: attributes += ', '
            attributes += str(attribute)
        log_details += ' | ATTRIBUTE ID: {}'.format(attributes)

    keywords = ''
    if len(details['keywords']) > 0:
        for i, keyword in enumerate(details['keywords']):
            if i: keywords += ', '
            keywords += str(keyword)
        log_details += ' | KEYWORD ID: {}'.format(keywords)
    return log_details


def log_create_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'DOCDIR ID: {}'.format(docdir.id)
    log_details += ' | DIRECTORY ID: {}'.format(docdir.directory.id)
    log_details += append_document_log_details(details)

    log(request, docdir.document, 'CREATE', log_details)
    return


def log_update_document(request, document, old_details, new_details):
    log_details = 'UPDATES => '

    if old_details['title'] != new_details['title']:
        log_details += ' | TITLE: {}'.format(new_details['title'])
    if old_details['description'] != new_details['description']:
        log_details += ' | DESCRIPTION: {}'.format(new_details['description'])
    if old_details['type'] != new_details['type']:
        log_details += ' | TYPE: {}'.format(new_details['type'])
    if old_details['is_public'] != new_details['is_public']:
        log_details += ' | IS PUBLIC: {}'.format(new_details['is_public'])

    log_details += append_document_attributes_log_details(new_details)

    log(request, document, 'UPDATE', log_details)
    return


def log_destroy_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'ID: {}'.format(details['id'])
    log_details += append_document_log_details(details)
    log(request, docdir.document, 'DELETE', log_details)
    return


def log_destroy_all_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'ID: {}'.format(details['id'])
    log_details += append_document_log_details(details)
    log(request, docdir.document, 'DELETE ALL', log_details)
    return


def log_trash_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'ID: {}'.format(details['id'])
    log_details += append_document_log_details(details)
    log(request, docdir.document, 'TRASH', log_details)
    return


def log_restore_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'ID: {}'.format(details['id'])
    log_details += append_document_log_details(details)
    log(request, docdir.document, 'RESTORE', log_details)
    return


def log_restore_all_document(request, docdir):
    details = get_document_info(docdir.document)
    log_details = 'ID: {}'.format(details['id'])
    log_details += append_document_log_details(details)
    log(request, docdir.document, 'RESTORE ALL', log_details)
    return


def log_copy_document(request, source_docdir, docdir):
    details = get_document_info(docdir.document)
    log_details = 'DOCDIR ID: {}'.format(docdir.id)
    log_details += ' | SOURCE DOCDIR ID: {}'.format(source_docdir)

    log_details += append_document_log_details(details)

    log(request, docdir.document, 'COPY', log_details)
    return


def log_link_document(request, source_docdir, docdir):
    details = get_document_info(docdir.document)
    log_details = 'DOCDIR ID: {}'.format(docdir.id)
    log_details += ' | SOURCE DOCDIR ID: {}'.format(source_docdir)

    log_details += append_document_log_details(details)

    log(request, docdir.document, 'LINK', log_details)
    return


def log_cut_document(request, source_docdir, docdir):
    details = get_document_info(docdir.document)
    log_details = 'DOCDIR ID: {}'.format(docdir.id)
    log_details += ' | SOURCE DOCDIR ID: {}'.format(source_docdir)

    log_details += append_document_log_details(details)

    log(request, docdir.document, 'MOVE', log_details)
    return


def log_request_document_to_publicize(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE REQUEST', log_details)
    return


def log_cancel_request_document_to_publicize(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE REQUEST CANCEL', log_details)
    return


def log_publicize_document(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE', log_details)
    return


def log_unpublicize_document(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'UNPUBLICIZE', log_details)
    return

def log_publicize_document_guest(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE GUEST', log_details)
    return

def log_unpublicize_document_guest(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'UNPUBLICIZE GUEST', log_details)
    return

def log_request_document_to_publicize_guest(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE REQUEST GUEST', log_details)
    return

def log_cancel_request_document_to_publicize_guest(request, docdir):
    log_details = 'DOCDIR ID: {}'.format(docdir.id)

    log(request, docdir.document, 'PUBLICIZE REQUEST CANCEL GUEST', log_details)
    return
