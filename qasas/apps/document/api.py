from datetime import datetime, timedelta
import pprint
from django.db.models import Subquery
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from ..department.models import Department, UserDepartment
from .logger import log_create_document, log_update_document, log_destroy_document, \
    log_copy_document, get_document_info, log_link_document, log_cut_document, log_request_document_to_publicize,log_request_document_to_publicize_guest, \
    log_cancel_request_document_to_publicize, log_publicize_document, log_unpublicize_document, log_trash_document, log_publicize_document_guest, log_unpublicize_document_guest, log_cancel_request_document_to_publicize_guest
from .utils import parse_document_form, copy_document_method
from ..authentication.utils import check_token, get_user_by_token, check_is_support
from ..department.utils import get_department,get_my_departments
from ..directory.api import parse_filter_forms, filter_document
from ..directory.models import Directory
from ..directory.utils import get_ancestry, get_department_by_dir,get_directory_tree_structure
from ..document.models import Document, Attachment, Attribute, Keyword, Comment, DocumentDirectory, Type, Actions, Log, GlobalDirectory
from ..document.serializers import DocumentSerializer, AttachmentSerializer, AttributeSerializer, KeywordSerializer, \
    CommentSerializer, DocumentDirectorySerializer, TypeSerializer
from ..document.utils import search_document
from ..trash.models import DocumentTrash

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DocumentSerializer

    def create(self, request):

        form = parse_document_form(request)
        user = User.objects.get(id=form['user_id'])
        directory = Directory.objects.get(id=form['directory_id'])
        type = Type.objects.get(name=form['type'])
        document = Document.objects.create(
            user=user,
            title=form['title'],
            description=form['description'],
            type=type,
            is_public=form['is_public'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for attachment in form['attachments']:
            Attachment.objects.create(
                document=document,
                attachment=attachment
            )
        for attribute in form['attributes']:
            Attribute.objects.create(
                document=document,
                key=attribute['key'],
                value=attribute['value']
            )
        for keyword in form['keywords']:
            Keyword.objects.create(
                document=document,
                keyword=keyword
            )
        docdir = DocumentDirectory.objects.create(
            directory=directory,
            document=document
        )

        log_create_document(request, docdir)

        return Response({
            'document_id': document.id
        })

    def update(self, request, pk=None):
        form = parse_document_form(request)
        document = Document.objects.get(id=pk)
        old_details = get_document_info(document)

        document.title = form['title']
        document.description = form['description']
        document.is_public = form['is_public']
        document.type = Type.objects.get(name=form['type'])
        document.updated_at = timezone.now()
        document.save()

        if form['deletedAttachments']:
            for id in form['deletedAttachments']:
                Attachment.objects.filter(
                    id=id
                ).delete()

        if form['attachments']:
            for attachment in form['attachments']:
                Attachment.objects.create(
                    document=document,
                    attachment=attachment
                )

        Attribute.objects.filter(document=document.id).delete()
        for attribute in form['attributes']:
            Attribute.objects.create(
                document=document,
                key=attribute['key'],
                value=attribute['value']
            )

        Keyword.objects.filter(document=document.id).delete()
        for keyword in form['keywords']:
            Keyword.objects.create(
                document=document,
                keyword=keyword
            )

        new_details = get_document_info(document)
        log_update_document(request, document, old_details, new_details)

        return Response({
            'document_id': document.id
        })

    def destroy(self, request, pk=None):
        docdir = DocumentDirectory.objects.get(id=pk)
        docdir.is_trashed = True
        log_trash_document(request, docdir)
        docdir.save()

        DocumentTrash.objects.create(
            department=get_department_by_dir(docdir.directory),
            docdir=docdir,
            user=get_user_by_token(request)
        )

        # docdirs.delete()
        # attachments = Attachment.objects.filter(document=document.id)
        # for attachment in attachments:
        #     file = Attachment.objects.get(id=attachment.id)
        #     try: os.remove(os.path.join(settings.MEDIA_ROOT, file.attachment.name))
        #     except: pass
        # for docdir in docdirs:

        return Response({})


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = AttachmentSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = AttributeSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = KeywordSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = CommentSerializer


class DocumentDirectoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentDirectory.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DocumentDirectorySerializer


class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = TypeSerializer

class GlobalDirectoryViewSet(viewsets.ModelViewSet):
    queryset = GlobalDirectory.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = TypeSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_attachment(request):
    POST = request.POST
    FILES = request.FILES
    response_data = {}

    document_id = POST['document_id'] if 'document_id' in POST else None
    attachment = FILES['attachment'] if 'attachment' in FILES else None

    if document_id and attachment:
        document = Document.objects.get(id=document_id)
        Attachment.objects.create(
            document=document,
            attachment=attachment
        )
    else:
        response_data['error'] = 'Invalid data'

    return Response(response_data)

@csrf_exempt
def get_document_details(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        docdir = DocumentDirectory.objects.get(id=docdir_id)

        if docdir:
            document = docdir.document
            response_data['id'] = document.id
            response_data['title'] = document.title
            response_data['description'] = document.description
            response_data['directory_id'] = directory_id
            response_data['is_public'] = docdir.is_public
            response_data['type'] = document.type.name

            attributes = []
            queryset = Attribute.objects.filter(document=document.id).values('key', 'value').distinct()
            if queryset.exists():
                for attribute in queryset:
                    attributes.append(attribute)

            keywords = []
            queryset = Keyword.objects.filter(document=document.id).values('keyword').distinct()
            if queryset.exists():
                for keyword in queryset:
                    keywords.append(keyword['keyword'])

            attachments = []
            queryset = Attachment.objects.filter(document=document.id).distinct()
            if queryset.exists():
                for attachment in queryset:
                    attachments.append({
                        'id': attachment.id,
                        'dir': attachment.attachment.name[0:12],
                        'name': attachment.attachment.name[12:],
                        'size': '{0:.2f} MB'.format(attachment.attachment.size / 1000000) \
                            if attachment.attachment.storage.exists(attachment.attachment.name) else 'FILE NOT FOUND'
                    })
            attachments.reverse()

            response_data = {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'type': document.type.name,
                'is_public': docdir.is_public,
                'keywords': keywords,
                'attributes': attributes,
                'attachments': attachments,
                'user_id': document.user.id,
                'author': '{} {}'.format(document.user.first_name, document.user.last_name),
                'created_at': document.created_at.strftime('%B %d, %Y'),
                'updated_at': document.updated_at.strftime('%B %d, %Y'),
                'directory_id': directory_id,
                'department_id': get_department(docdir.directory.id).id,
                'docdir_id': docdir.id,
                'is_copy': docdir.is_copy,
                'is_link': docdir.is_link,
                'link': docdir.link.id if docdir.link else None,
                'link_directory': docdir.link.directory.id if docdir.link else None,
                'this_path': get_ancestry(docdir.directory),
                'source_path': get_ancestry(docdir.link.directory) if docdir.link and (
                        docdir.is_copy or docdir.is_link) else None,
                'is_guest': docdir.is_guest
            }

    return JsonResponse(response_data)


@csrf_exempt
def get_document_details_guest(request):
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        docdir = DocumentDirectory.objects.get(id=docdir_id)

        if docdir:
            document = docdir.document
            response_data['id'] = document.id
            response_data['title'] = document.title
            response_data['description'] = document.description
            response_data['directory_id'] = directory_id
            response_data['is_public'] = docdir.is_public
            response_data['type'] = document.type.name

            attributes = []
            queryset = Attribute.objects.filter(document=document.id).values('key', 'value').distinct()
            if queryset.exists():
                for attribute in queryset:
                    attributes.append(attribute)

            keywords = []
            queryset = Keyword.objects.filter(document=document.id).values('keyword').distinct()
            if queryset.exists():
                for keyword in queryset:
                    keywords.append(keyword['keyword'])

            attachments = []
            queryset = Attachment.objects.filter(document=document.id).distinct()
            if queryset.exists():
                for attachment in queryset:
                    attachments.append({
                        'id': attachment.id,
                        'dir': attachment.attachment.name[0:12],
                        'name': attachment.attachment.name[12:],
                        'size': '{0:.2f} MB'.format(attachment.attachment.size / 1000000) \
                            if attachment.attachment.storage.exists(attachment.attachment.name) else 'FILE NOT FOUND'
                    })
            attachments.reverse()

            response_data = {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'type': document.type.name,
                'is_public': docdir.is_public,
                'keywords': keywords,
                'attributes': attributes,
                'attachments': attachments,
                'user_id': document.user.id,
                'author': '{} {}'.format(document.user.first_name, document.user.last_name),
                'created_at': document.created_at.strftime('%B %d, %Y'),
                'updated_at': document.updated_at.strftime('%B %d, %Y'),
                'directory_id': directory_id,
                'department_id': get_department(docdir.directory.id).id,
                'docdir_id': docdir.id,
                'is_copy': docdir.is_copy,
                'is_link': docdir.is_link,
                'link': docdir.link.id if docdir.link else None,
                'link_directory': docdir.link.directory.id if docdir.link else None,
                'this_path': get_ancestry(docdir.directory),
                'source_path': get_ancestry(docdir.link.directory) if docdir.link and (
                        docdir.is_copy or docdir.is_link) else None,
                'is_guest': docdir.is_guest
            }

    return JsonResponse(response_data)


@csrf_exempt
def copy_document(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        directory = Directory.objects.get(id=directory_id)
        docdir = DocumentDirectory.objects.get(id=docdir_id)

        new_docdir = copy_document_method(directory, docdir)
        log_copy_document(request, docdir, new_docdir)

    return JsonResponse(response_data)


@csrf_exempt
def link_document(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        docdir = DocumentDirectory.objects.get(id=docdir_id)
        directory = Directory.objects.get(id=directory_id)
        for docdir in DocumentDirectory.objects.filter(
                directory=directory_id,
                document=docdir.document.id
        ):
            if docdir.link == docdir_id or \
                    docdir.id == docdir.id:
                return JsonResponse({'error': 'Already Exists!'})

        docdir = DocumentDirectory.objects.create(
            directory=directory,
            document=docdir.document,
            is_link=True,
            link=docdir
        )

        log_link_document(request, docdir_id, docdir)

    return JsonResponse(response_data)


@csrf_exempt
def cut_document(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        directory = Directory.objects.get(id=directory_id)
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.directory = directory
        docdir.save()

        log_cut_document(request, docdir_id, docdir)

    return JsonResponse(response_data)


@csrf_exempt
def unlink_document(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        DocumentDirectory.objects.get(id=docdir_id).delete()

    return JsonResponse(response_data)


@csrf_exempt
def get_requested_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'departments': [],
        'documents': []
    }

    if request.method == 'POST':
        filter_form = parse_filter_forms(request.POST)
        search_key = request.POST['search_key'] if 'search_key' in request.POST else None

        docdirQuery = DocumentDirectory.objects.filter(is_public=None)
        docdirQuery = filter_document(docdirQuery, filter_form)
        if search_key: docdirQuery = search_document(docdirQuery, search_key)
        for docdir in docdirQuery:
            document = docdir.document

            attachments = []
            for attachment in Attachment.objects.filter(document=document.id):
                attachments.append(attachment.attachment.name)
            attachments.reverse()
            department = get_department(docdir.directory.id).name
            if department not in response_data['departments']:
                response_data['departments'].append(department)

            response_data['documents'].append({
                'id': document.id,
                'title': document.title,
                'department': department,
                'attachments': attachments,
                'created_at': document.created_at,
                'updated_at': document.updated_at,
                'directory_id': docdir.directory.id,
                'docdir_id': docdir.id,
                'is_copy': docdir.is_copy,
                'is_link': docdir.is_link,
                'link': docdir.link.id if docdir.link else None,
                'link_directory': docdir.link.directory.id if docdir.link else None,
            })

            response_data['documents'] = sorted(
                response_data['documents'],
                key=lambda x: x[filter_form['sort_by']],
                reverse=not filter_form['ascending']
            )
            response_data['departments'].sort()

    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)


@csrf_exempt
def request_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_public = None
        docdir.save()

        log_request_document_to_publicize(request, docdir)

    return JsonResponse({})


@csrf_exempt
def request_all_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':

        # GET DOCDIRS
        docdirs = []
        for field in POST:
            if field.startswith('docdir_id_'):
                docdirs.append(int(POST[field]))

        for docdir in docdirs:
            docdir = DocumentDirectory.objects.get(id=docdir)
            if docdir.is_public == False:
                docdir.is_public = None
                docdir.save()
                log_request_document_to_publicize(request, docdir)

    return JsonResponse({})


@csrf_exempt
def cancel_request_all_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_public = False
        docdir.save()

        log_cancel_request_document_to_publicize(request, docdir)

    return JsonResponse({})


@csrf_exempt
def approve_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_public = True
        docdir.save()

        log_publicize_document(request, docdir)

    return JsonResponse({})


@csrf_exempt
def reject_to_publicize(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_public = False
        docdir.save()

        log_unpublicize_document(request, docdir)

    return JsonResponse({})

@csrf_exempt
def approve_to_publicize_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = True
        docdir.save()

        log_publicize_document_guest(request, docdir)

    return JsonResponse({})

@csrf_exempt
def approve_to_unpublicize_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = False
        docdir.is_public = False
        docdir.save()

        log_unpublicize_document_guest(request, docdir)
    
    return JsonResponse({})


@csrf_exempt
def document_directory(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'public': [],
        'departments': []
    }
    if request.method == 'POST':
        if 'user_id' in request.POST:
            user_id = request.POST['user_id']
            user = User.objects.get(id=user_id)
            if user:

                # Office
                departmentQuery = UserDepartment.objects.filter(user=user.id).only('department').order_by(
                    'department__name')
                for department in departmentQuery:
                    response_data['departments'].append(
                        get_directory_tree_structure(department.department.root_directory.id, {})
                    )
                    # directory = department.department.root_directory
                    # response_data['departments'].append({
                    #     'department_id': department.department.id,
                    #     'directory_id': directory.id,
                    #     'name': directory.name,
                    #     'description': directory.description,
                    #     'has_children': directory.children.all().exists()
                    # })

                # Public
                departmentQuery = Department.objects.filter(is_support=False).order_by('name')

                # Clone Office to Public
                # response_data['public'] = deepcopy(response_data['departments'])
                # Exclude departments in Office
                for department in response_data['departments']:
                    departmentQuery = departmentQuery.exclude(root_directory__id=department['directory_id'])

                for department in departmentQuery:
                    response_data['public'].append(
                        get_directory_tree_structure(department.root_directory.id, {})
                    )
                    # directory = department.root_directory
                    # response_data['public'].append({
                    #     'department_id': department.id,
                    #     'directory_id': directory.id,
                    #     'name': directory.name,
                    #     'description': directory.description,
                    #     'has_children': directory.children.all().exists()
                    # })

        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)

@csrf_exempt
def get_actions(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'actions': []
    }
    if request.method == 'POST':
        tmp = []
        actionsQuery = Actions.objects.all()
        for action in actionsQuery:
            response_data['actions'].append({
                'id': action.id,
                'action': action.action
            })
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)

@csrf_exempt
def get_monitoring(request):
     check = check_token(request)
     serializer_class = DocumentSerializer
     if check: return JsonResponse(check)
     response_data = {
         'log': []
     }
     if request.method == 'POST':
         if 'date_from' in request.POST and 'date_to' in request.POST:

             user_id = request.POST['user_id']
             action = request.POST['actions']
             office = request.POST['offices']
             user = request.POST['users']
             date_from =  datetime.strptime(request.POST['date_from'],'%Y-%m-%d')
             date_to =  datetime.strptime(request.POST['date_to'],'%Y-%m-%d')

             logQuery = Log.objects.select_related('document').select_related('user').filter(user__isnull=False).filter(document__isnull=False).filter(timestamp__date__range=(date_from, date_to)).order_by('-timestamp')
#              userDepartmentQuery = UserDepartment.objects.values('department_id').filter(user_id=user_id).filter(is_active=1)
#              is_support = check_is_support(user_id)

             if action != 'all':
                 try:
                     logQuery = logQuery.filter(action=Actions.objects.get(id=action))
                 except:
                     pass
             if user != 'all':
                  logQuery = logQuery.filter(user_id=user)
#              else:
#                 if is_support is False:
#                     userListQuery = UserDepartment.objects.values('user_id').filter(department_id__in=userDepartmentQuery.values('department_id'))
#                     logQuery.filter(user_id__in=userListQuery.values('user_id'))

             for log in logQuery:
                 try:
                    documentDirectoryQuery = DocumentDirectory.objects.get(document_id=log.document_id)
                    document_department = get_department(documentDirectoryQuery.directory.id)

                    addList = True
#                     if office == 'all':
#                         if is_support is False:
#                             addList = userDepartmentQuery.filter(department_id=document_department.id).exists()
#                     else:
                    if int(office) != int(document_department.root_directory_id):
                           addList = False


                    if addList is True and document_department.is_support == False:
                        response_data['log'].append({
                            'action': log.action,
                            'date': timezone.localtime(log.timestamp),
                            'department': document_department.name,
                            'document': log.document.title,
                            'description': log.document.description,
                            'user': log.user.first_name + " " + log.user.last_name
                        })

                 except:
                    pass
         else:
             response_data['error'] = 'Incomplete Parameters'
     else:
         response_data['error'] = 'Non-POST Request'
     return JsonResponse(response_data)


@csrf_exempt
def approve_to_publicize_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None

        root_directory_id = POST['root_directory_id'] if 'root_directory_id' in POST else None
        
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = True
        docdir.is_public = True
        docdir.save()

        approve_publicize_global(docdir,root_directory_id)

        log_publicize_document_guest(request, docdir)

    return JsonResponse({})

@csrf_exempt
def approve_to_unpublicize_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None

        root_directory_id = POST['root_directory_id'] if 'root_directory_id' in POST else None

        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = False
        docdir.is_public = False
        docdir.save()

        approve_unpublicize_global(docdir, root_directory_id)
        log_unpublicize_document_guest(request, docdir)
    
    return JsonResponse({})

@csrf_exempt
def request_to_approved_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = None
        docdir.is_public = None
        docdir.save()

        log_request_document_to_publicize_guest(request, docdir)
        log_request_document_to_publicize(request, docdir)

    return JsonResponse({})

@csrf_exempt
def cancel_request_all_to_publicize_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = False
        docdir.is_public = False
        docdir.save()

        log_cancel_request_document_to_publicize_guest(request, docdir)
        log_cancel_request_document_to_publicize(request, docdir)

    return JsonResponse({})

@csrf_exempt
def approve_to_publicize_global_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        
        root_directory_id = POST['root_directory_id'] if 'root_directory_id' in POST else None
        
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = True
        docdir.is_public = True
        docdir.save()

        approve_publicize_global(docdir, root_directory_id)

        log_publicize_document_guest(request, docdir)
        log_publicize_document(request, docdir)
    return JsonResponse({})

@csrf_exempt
def approve_to_unpublicize_global_guest(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST

    if request.method == 'POST':
        docdir_id = POST['docdir_id'] if 'docdir_id' in POST else None
        docdir = DocumentDirectory.objects.get(id=docdir_id)
        docdir.is_guest = False
        docdir.is_public = False
        docdir.save()

        
        log_unpublicize_document_guest(request, docdir)
        log_unpublicize_document(request, docdir)

    return JsonResponse({})

@csrf_exempt
def approve_publicize_global(docdir, root_directory):
    globaldirectory = GlobalDirectory()
    globaldirectory.root_directory_id = root_directory
    globaldirectory.document_id =  docdir.document_id
    globaldirectory.save()

@csrf_exempt
def approve_unpublicize_global(docdir, root_directory_id):

    globaldirectory = GlobalDirectory.objects.get(root_directory_id=root_directory_id,document_id = docdir.document_id)
    globaldirectory.delete()

    return JsonResponse({})