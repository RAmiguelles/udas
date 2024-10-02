from copy import deepcopy

from django.db.models import Q

from ..document.models import Attribute, Keyword, Attachment, DocumentDirectory


def get_document_data(document, data):
    doc = {
        'id': document.id,
        'user_id': document.user.id,
        'title': document.title,
        'description': document.description,
        'attributes': []
    }

    attributesQuery = Attribute.objects.filter(document=document.id).values('id', 'key', 'value').distinct()
    for attribute in attributesQuery:
        doc['attributes'].append(attribute)

    doc['keywords'] = []
    keywordsQuery = Keyword.objects.filter(document=document.id).values('id', 'keyword').distinct()
    for keyword in keywordsQuery:
        doc['keywords'].append(keyword)

    doc['attachments'] = []
    attachmentsQuery = Attachment.objects.filter(document=document.id).values('id', 'attachment').distinct()
    for attachment in attachmentsQuery:
        doc['attachments'].append(attachment.name)

    doc['author'] = '{} {}'.format(document.user.first_name, document.user.last_name)
    doc['created_at'] = document.created_at
    doc['updated_at'] = document.updated_at

    data.append(doc)

    return data


def search_document(queryset, search_key):
    queryset = queryset.filter(
        Q(document__user__first_name__icontains=search_key) |
        Q(document__user__last_name__icontains=search_key) |
        Q(document__title__icontains=search_key) |
        Q(document__description__icontains=search_key)
        # Q(document__type__name__icontains=search_key) |
        # Q(document__attributes__key__icontains=search_key) |
        # Q(document__attributes__value__icontains=search_key) |
        # Q(document__keywords__keyword__icontains=search_key)
    ).distinct()

    return queryset


def filter_document(docdirQuery, form):
    if form['type']:
        docdirQuery = docdirQuery.filter(
            Q(document__type__name=form['type'])
        )
    if form['is_public'] is not None:
        docdirQuery = docdirQuery.filter(
            Q(is_public=form['is_public'], is_guest=False)
        )
    for attr in form['attributes']:
        docdirQuery = docdirQuery.filter(
            Q(
                document__attributes__key=attr['key'],
                document__attributes__value=attr['value']
            )
        )
    for key in form['keywords']:
        docdirQuery = docdirQuery.filter(
            Q(document__keywords__keyword=key)
        )
    return docdirQuery


def parse_document_form(request):
    form = {}
    POST = request.POST
    FILES = request.FILES

    form['user_id'] = POST['user_id'] if 'user_id' in POST else 0
    form['directory_id'] = POST['directory_id'] if 'directory_id' in POST else 0
    form['title'] = POST['title'] if 'title' in POST else "Untitled"
    form['description'] = POST['description'] if 'description' in POST else ""
    form['is_public'] = POST['is_public'] if 'is_public' in POST else False
    form['type'] = POST['type'] if 'type' in POST else 0

    # POSTMAN FIXTURE
    form['is_public'] = True if form['is_public'] == 'true' else False
    form['title'] = 'Untitled' if form['title'] == '' else form['title']

    form['attachments'] = []
    for item in FILES.getlist('attachments[]'):
        form['attachments'].append(item)

    form['deletedAttachments'] = []
    for item in POST.getlist('deletedAttachments[]'):
        form['deletedAttachments'].append(item)

    form['attributes'] = []
    form['keywords'] = []

    for field in POST:
        if field.startswith('ak_'):
            form['attributes'].append({
                'key': POST['ak_' + field[3:]],
                'value': POST['av_' + field[3:]],
            })
        if field.startswith('k_'):
            form['keywords'].append(POST['k_' + field[2:]])

    return form


def parse_filter_forms(POST):
    form = {
        'search_key': POST['search_key'] if 'search_key' in POST else None,
        'search_scope': POST['search_scope'] if 'search_scope' in POST else None,
        'type': POST['type'] if 'type' in POST else None,
        'is_public': POST['is_public'] if 'is_public' in POST else None,
        'sort_by': POST['sort_by'] if 'sort_by' in POST else None,
        'ascending': POST['ascending'] if 'ascending' in POST else None,
        'attributes': [],
        'keywords': []
    }

    form['is_public'] = True if form['is_public'] == 'true' else False if form['is_public'] == 'false' else None
    form['sort_by'] = None if form['sort_by'] == 'null' else form['sort_by']
    form['ascending'] = True if form['ascending'] == 'true' else False

    for field in POST:
        if field.startswith('ak_'):
            form['attributes'].append({
                'key': POST['ak_' + field[3:]],
                'value': POST['av_' + field[3:]],
            })
        if field.startswith('k_'):
            form['keywords'].append(POST['k_' + field[2:]])

    return form


def copy_document_method(directory, docdir):
    document = deepcopy(docdir.document)
    document.pk = None
    document.save()

    def clone(CLASS):
        nonlocal docdir
        nonlocal document
        query = CLASS.objects.filter(document=docdir.document.id)
        if query.exists():
            for OBJECT in query:
                OBJECT.pk = None
                OBJECT.document = document
                OBJECT.save()

    clone(Attachment)
    clone(Attribute)
    clone(Keyword)

    docdir = DocumentDirectory.objects.create(
        directory=directory,
        document=document,
        is_copy=True,
        link=docdir
    )

    return docdir
