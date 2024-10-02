from copy import deepcopy

from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pprint import pprint 
from .logger import log_create_directory, log_update_directory, log_destroy_directory, \
    log_copy_directory, log_cut_directory, get_directory_info, log_trash_directory, log_link_directory, \
    log_remove_link_directory
from ..authentication.utils import check_token, get_user_by_token
from ..department.models import Department, UserDepartment
from ..department.utils import get_my_departments
from ..directory.models import Directory, DirectoryGroup, Moderator, LinkedDirectory, Accreditor
from ..directory.serializers import DirectorySerializer, DirectoryGroupSerializer, \
    ModeratorSerializer, CollegeDescriptionSerializer, CollegeDescriptionDetailSerializer
from ..directory.utils import get_ancestry, get_directory, get_directory_tree_structure, get_tree, get_department_by_dir, get_url_permission, get_user_department_list
from ..document.models import DocumentDirectory, GlobalDirectory
from ..document.utils import parse_filter_forms, filter_document, search_document, copy_document_method
from ..trash.models import DirectoryTrash
from src.models import CollegeDescription, CollegeDescriptionDetail
from src.utils import copy_dir_link_desc

import json
from django.core.serializers import serialize
import threading

class DirectoryViewSet(viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DirectorySerializer

    def create(self, request):
        POST = request.POST

        # form = DirectoryForm(request.POST)
        # if form.is_valid():
        #     data = form.cleaned_data
        #     data['employee'] = request.session['user_details']['employee']['id']

        parent = POST['parent'] if 'parent' in POST else 0
        name = POST['name'] if 'name' in POST else ''
        description = POST['description'] if 'description' in POST else ''
        group = POST['group'] if 'group' in POST else ''
        is_public = POST['is_public'] if 'is_public' in POST else False

        moderators = []
        for field in POST:
            if field.startswith('m_'):
                moderators.append(POST['m_' + field[2:]])

        name = name if name else 'New Directory'
        description = description if description != 'undefined' else ''
        is_public = True if is_public == 'true' else False
        if group:
            try:
                group = DirectoryGroup.objects.get(name=group)
            except:
                group = DirectoryGroup.objects.create(name=group)

        parent = Directory.objects.get(id=parent)

        directory = Directory.objects.create(
            name=name,
            description=description,
            group=group if group else None,
            is_public=is_public,
            parent=parent
        )

        for user in moderators:
            Moderator.objects.create(
                user=User.objects.get(id=user),
                directory=directory
            )

        log_create_directory(request, directory)

        return Response({})

    def update(self, request, pk=None):
        POST = request.POST

        name = POST['name'] if 'name' in POST else ''
        description = POST['description'] if 'description' in POST else ''
        group = POST['group'] if 'group' in POST else ''
        is_public = POST['is_public'] if 'is_public' in POST else False

        moderators = []
        for field in POST:
            if field.startswith('m_'):
                moderators.append(POST['m_' + field[2:]])

        name = name if name else 'No name'
        is_public = True if is_public == 'true' else False

        if group:
            try:
                group = DirectoryGroup.objects.get(name=group)
            except:
                group = DirectoryGroup.objects.create(name=group)

        directory = Directory.objects.get(id=pk)

        old_details = get_directory_info(directory)

        directory.name = name
        directory.description = description
        if group: directory.group = group
        directory.is_public = is_public
        directory.save()

        Moderator.objects.filter(directory=directory).delete()
        for user in moderators:
            Moderator.objects.create(
                user=User.objects.get(id=user),
                directory=directory
            )

        log_update_directory(request, old_details, directory)

        return Response({})

    def destroy(self, request, pk=None):
        directory = Directory.objects.get(id=pk)
        directory.is_trashed = True
        log_trash_directory(request, directory)
        directory.save()

        DirectoryTrash.objects.create(
            department=get_department_by_dir(directory),
            directory=directory,
            user=get_user_by_token(request)
        )

        # directory.delete()

        # print(directory)
        return Response({})


class DirectoryGroupViewSet(viewsets.ModelViewSet):
    queryset = DirectoryGroup.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DirectoryGroupSerializer


class ModeratorViewSet(viewsets.ModelViewSet):
    queryset = Moderator.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ModeratorSerializer


# @csrf_exempt
# def get_directory_tree_by_user_id(request):
#     check = check_token(request)
#     if check: return JsonResponse(check)
#     response_data = {
#         'public': [],
#         'departments': []
#     }
#     if request.method == 'POST':
#         if 'user_id' in request.POST:
#             user_id = request.POST['user_id']
#             user = User.objects.get(id=user_id)
#             if user:
#
#                 # Office
#                 departmentQuery = UserDepartment.objects.filter(user=user.id).only('department').order_by(
#                     'department__name')
#                 for department in departmentQuery:
#                     response_data['departments'].append(
#                         get_directory_tree_structure(department.department.root_directory.id, {})
#                     )
#                     # directory = department.department.root_directory
#                     # response_data['departments'].append({
#                     #     'department_id': department.department.id,
#                     #     'directory_id': directory.id,
#                     #     'name': directory.name,
#                     #     'description': directory.description,
#                     #     'has_children': directory.children.all().exists()
#                     #     })
#
#                 # Public
#                 departmentQuery = Department.objects.filter(is_support=False).order_by('name')
#
#                 # Clone Office to Public
#                 # response_data['public'] = deepcopy(response_data['departments'])
#                 # Exclude departments in Office
#                 for department in response_data['departments']:
#                     departmentQuery = departmentQuery.exclude(root_directory__id=department['directory_id'])
#
#                 for department in departmentQuery:
#                     response_data['public'].append(
#                         get_directory_tree_structure(department.root_directory.id, {})
#                     )
#                     # directory = department.root_directory
#                     # response_data['public'].append({
#                     #     'department_id': department.id,
#                     #     'directory_id': directory.id,
#                     #     'name': directory.name,
#                     #     'description': directory.description,
#                     #     'has_children': directory.children.all().exists()
#                     # })
#
#         else:
#             response_data['error'] = 'Incomplete Parameters'
#     else:
#         response_data['error'] = 'Non-POST Request'
#     return JsonResponse(response_data)


@csrf_exempt
def get_directory_tree_by_user_id(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'public': [],
        'departments': []
    }
    processed_departments = set()
    if request.method == 'POST':
        if 'user_id' in request.POST:
            user_id = request.POST['user_id']
            user = User.objects.get(id=user_id)
            if user:
                if(Accreditor.objects.filter(user_id=request.POST['user_id']).exists()):
                    dires=Accreditor.objects.filter(user_id=request.POST['user_id'])
                    for dire in dires:
                        directory = get_directory(dire.directory_id)
                        department = get_department_by_dir(directory)
                        if department.id not in processed_departments:
                            processed_departments.add(department.id)
                            
                            dir_tree = get_directory_tree_structure(department.root_directory.id, {})
                            dir_tree["is_support"] = 1 if department.is_support else 0
                            
                            response_data['departments'].append(dir_tree)
                else:
                    # Office
                    departmentQuery = UserDepartment.objects.filter(user=user.id).only('department').order_by(
                        'department__name')

                    for department in departmentQuery:
                        dir_tree = get_directory_tree_structure(department.department.root_directory.id, {})
                        dir_tree["is_support"] =  1 if department.department.is_support else 0
                        response_data['departments'].append(
                            dir_tree
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
def get_directory_tree_by_directory_id(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {}
    if request.method == 'POST':
        if 'directory_id' in request.POST:
            directory_id = request.POST['directory_id']
            response_data = get_directory_tree_structure(directory_id, response_data)
        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)

@csrf_exempt
def get_directory_details(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {}

    if request.method == 'POST':
        filter_form = parse_filter_forms(request.POST)

        directory_id = request.POST['directory_id']
        user_id = request.POST['user_id']
        directory = get_directory(directory_id)
        user = User.objects.get(id=user_id)
        if directory is None: return JsonResponse({'error': 'Directory Not Found'})
        if user is None: return JsonResponse({'error': 'User Not Found'})

        response_data['children'] = []
        response_data['links'] = []
        response_data['children_groups'] = []
        response_data['documents'] = []
        response_data['accreds']=[]             
        if(Accreditor.objects.filter(user_id=request.POST['user_id']).exists()):
            accreds=Accreditor.objects.filter(user_id=request.POST['user_id'])
            for accred in accreds:
                response_data['accreds'].append(accred.directory_id)
                
        def get_children(directory, parent_dir=[]):
            nonlocal response_data

            for dir_id in response_data['accreds']:
                child=get_directory(dir_id)
                ance=get_ancestry(child)
                if ance[0]['id']==directory.id and directory.id not in response_data['accreds']:
                    if child.is_trashed: continue
                    if filter_form['search_key']:
                        if filter_form['search_key'].lower() not in child.name.lower(): continue
                    group_name = child.group.name if child.group else "Ungrouped"
                    if group_name not in response_data['children_groups']:
                        response_data['children_groups'].append(group_name)
                    response_data['children'].append({
                        'id': child.id,
                        'name': child.name,
                        'description': child.description,
                        'group': group_name,
                        'has_children': child.children.all().exists()
                    })

            if response_data['accreds']==[] or any(ance['id'] in response_data['accreds'] for ance in get_ancestry(directory)):
                if filter_form['search_key']:
                    children_query = Directory.objects.filter(name__icontains=filter_form['search_key']).only('name', 'description', 'group')
                else:
                    children_query = directory.children.all().only('name', 'description', 'group')
                    
                if children_query.exists():
                    for child in children_query:
                        if child.is_trashed: continue
                        if parent_dir:
                            if get_ancestry(child)[0]['id'] not in parent_dir: continue
                        if filter_form['search_scope'] == 'anywhere':
                            group_name = get_ancestry(child)[0]['name']
                            if group_name not in response_data['children_groups']: response_data['children_groups'].append(group_name)
                        else:
                            group_name = child.group.name if child.group else "Ungrouped"
                            if group_name not in response_data['children_groups']:
                                response_data['children_groups'].append(group_name)

                        response_data['children'].append({
                            'id': child.id,
                            'name': child.name,
                            'description': child.description,
                            'group': group_name,
                            'has_children': child.children.all().exists()
                        })

        def get_links(directory):
            nonlocal response_data

            link_query = directory.links.all()

            if link_query.exists():
                if 'LINKS' not in response_data['children_groups']:
                    response_data['children_groups'].append('LINKS')
                for link in link_query:
                    if link.directory.is_trashed: continue
                    if filter_form['search_key']:
                        if filter_form['search_key'].lower() not in link.directory.name.lower(): continue
                    # response_data['links'].append({
                    #     'id': link.directory.id,
                    #     'name': link.directory.name,
                    #     'description': link.directory.description,
                    # })
                    response_data['children'].append({
                        'id': link.directory.id,
                        'name': link.directory.name,
                        'description': link.directory.description,
                        'group': 'LINKS',
                        'is_link': True,
                        'has_children': link.directory.children.all().exists()
                    })

        def get_documents(directory_id, filter_public=False):
            nonlocal response_data

            docdir_query = DocumentDirectory.objects.filter(directory=directory_id).only('document')
            docdir_query = filter_document(docdir_query, filter_form)
            if filter_public: docdir_query = docdir_query.filter(is_public=True)
            if filter_form['search_key']: docdir_query = search_document(docdir_query, filter_form['search_key'])

            if docdir_query.exists():
                for docdir in docdir_query:
                    if docdir.is_trashed: continue
                    document = docdir.document
                    attachments = []

                    attachment_query = document.attachments.all().only('attachment')
                    if attachment_query.exists():
                        for attachment in attachment_query:
                            attachments.append(attachment.attachment.name)
                    attachments.reverse()

                    response_data['documents'].append({
                        'id': document.id,
                        'title': document.title,
                        'is_public': docdir.is_public,
                        'attachments': attachments,
                        'created_at': document.created_at,
                        'updated_at': document.updated_at,
                        'directory_id': docdir.directory.id,
                        'docdir_id': docdir.id,
                        'is_copy': docdir.is_copy,
                        'is_link': docdir.is_link,
                        'link': docdir.link.id if docdir.link else None,
                        'link_directory': docdir.link.directory.id if docdir.link else None,
                        'is_guest': docdir.is_guest,
                    })

        # def get_subdirectories_and_documents(directory, include_sub=False, filter_public=False):
        #     nonlocal response_data

        #     get_documents(directory.id, filter_public)
        #     get_children(directory)
        #     get_links(directory)

        #     if include_sub:
        #         children_query = directory.children.all()
        #         for child in children_query:
        #             get_subdirectories_and_documents(child, include_sub, filter_public)

        # if filter_form['search_scope'] == 'anywhere':

        #     # Collect all directories and documents within user offices and
        #     # all directories and public documents on all offices with regards
        #     # to search_key

        #     dep_query = Department.objects.filter(is_support=False).only('root_directory')
        #     my_departments = get_my_departments(user_id)
        #     for dep in my_departments:
        #         get_subdirectories_and_documents(dep.root_directory, True)
        #         dep_query = dep_query.exclude(id=dep.id)
        #     for dep in dep_query:
        #         get_subdirectories_and_documents(dep.root_directory, True, True)

        # elif filter_form['search_scope'] == 'directory':

        #     # Collect directories and documents within directory
        #     # with regards to search_key

        #     get_subdirectories_and_documents(directory, True)

        def get_subdirectories_and_documents(directory, include_sub=False, filter_public=False,parent_dir=[]):
            nonlocal response_data

            threading.Thread(get_documents(directory.id, filter_public)).start()
            threading.Thread(get_children(directory,parent_dir)).start()
            # get_links(directory)

            if parent_dir:
                for id in parent_dir:
                    directory1=get_directory(id)
                    children_query = directory1.children.all()
                    for child in children_query:
                        threading.Thread(get_documents(child.id, filter_public)).start()

        if filter_form['search_scope'] == 'anywhere':
            dirIDs=[]
            # Collect all directories and documents within user offices and
            # all directories and public documents on all offices with regards
            # to search_key
            dep_query = Department.objects.filter(is_support=False).only('root_directory')
            my_departments = get_my_departments(user_id,1)
            for dep in my_departments:
            #     # get_subdirectories_and_documents(dep.root_directory, False,False,[dep.root_directory])
            #     # dirIDs+=dep.root_directory
                dirIDs.append(dep.root_directory.id)
                dep_query = dep_query.exclude(id=dep.id)
            for dep in dep_query:
                dirIDs.append(dep.root_directory.id)
            get_subdirectories_and_documents(dep.root_directory, False,False,dirIDs)

        elif filter_form['search_scope'] == 'directory':

            # Collect directories and documents within directory
            # with regards to search_key
            dirID=get_ancestry(directory)[0]['id']
            get_subdirectories_and_documents(directory,False,False,[dirID])

        else:

            # Collect Directory Properties
            response_data['name'] = directory.name
            response_data['description'] = directory.description
            response_data['is_public'] = directory.is_public

            group = directory.group
            response_data['group'] = {
                'id': group.id if group else 0,
                'name': group.name if group else 'Ungrouped',
                'description': group.description if group else ''
            }

            response_data['moderators'] = []
            response_data['accreditors'] = []

            get_subdirectories_and_documents(directory)

            # Ancestry
            response_data['ancestry'] = get_ancestry(directory)

            # Tree
            response_data['tree'] = get_tree(directory)

            # Moderators
            moderators_query = directory.moderators.all().only('user')
            for item in moderators_query:
                response_data['moderators'].append({
                    'id': item.user.id,
                    'name': '{}{}{}'.format(item.user.first_name, ' ' if item.user.first_name else '',
                                            item.user.last_name)
                })

            # Accreditors
            accreditor_query = directory.accreditors.all().only('user')
            for item in accreditor_query:
                response_data['accreditors'].append({
                    'id': item.user.id,
                    'name': '{}{}{}'.format(item.user.first_name, ' ' if item.user.first_name else '',
                                            item.user.last_name)
                })

        # Data Sorting
        response_data['children_groups'].sort()
        response_data['children'] = sorted(
            response_data['children'],
            key=lambda x: x['name'],
            reverse=not filter_form['ascending']
        )
        response_data['documents'] = sorted(
            response_data['documents'],
            key=lambda x: x[filter_form['sort_by']],
            reverse=not filter_form['ascending']
        )

    else:
        response_data['error'] = 'Non-POST Request'

    return JsonResponse(response_data)

@csrf_exempt
def copy_directory(request):
    check = check_token(request)
    if check: return JsonResponse(check)

    POST = request.POST
    response_data = {
        "success": False
    }

    if request.method == 'POST':
        src_directory_id = POST['src_directory_id'] if 'src_directory_id' in POST else None
        dst_directory_id = POST['dst_directory_id'] if 'dst_directory_id' in POST else None
        is_public_only = POST['public'] if 'public' in POST else False

        #  FIXTURES
        is_public_only = True if is_public_only == 'true' else False
        # TRAVERSE ON ALL SUBDIRECTORIES AND DOCUMENTS OF SRC AND DUPLICATE TO DST
        def copy_dir(src_directory, parent):
            # NEW ID
            directory = deepcopy(src_directory)
            old_id = directory.id

            directory.pk = None
            directory.parent = None
            directory.save()

            # CLONE DOCUMENTS
            docdirs_query = DocumentDirectory.objects.filter(directory=old_id).only('document')
            if docdirs_query.exists():
                if is_public_only:
                    docdirs_query = docdirs_query.filter(is_public=True)

                for docdir in docdirs_query:
                    new_docdir = copy_document_method(directory, docdir)
                    # log_copy_document(request, docdir, new_docdir)

            # CLONE SUBDIRECTORIES
            if src_directory.children.all().exists():
                for child in src_directory.children.all():
                    copy_dir(child, directory)

            # ASSIGN PARENT
            directory.parent = parent
            directory.save()

            # CLONE DIRECTORY LINK DESCRIPTION
            # @PARAMS PREVIOUS DIRECTORY ID, NEW DIRECTORY ID (AUTO INCREMENT)
            copy_dir_link_desc(old_id, directory.id)

        src_directory = Directory.objects.get(id=src_directory_id)
        dst_directory = Directory.objects.get(id=dst_directory_id)
        copy_dir(src_directory, dst_directory)
        log_copy_directory(request, src_directory, dst_directory)
        response_data["success"] = True
    return JsonResponse(response_data)


@csrf_exempt
def link_directory(request):
    check = check_token(request)
    if check: return JsonResponse(check)

    POST = request.POST
    response_data = {
        "success": False
    }
    if request.method == 'POST':
        directory_id = POST['directory_id'] if 'directory_id' in POST else None
        parent_id = POST['parent_id'] if 'parent_id' in POST else None

        directory = Directory.objects.get(id=directory_id)
        parent = Directory.objects.get(id=parent_id)

        if LinkedDirectory.objects.filter(directory=directory, parent=parent).exists():
            response_data["error"] = 'Already exists'
        else:
            LinkedDirectory.objects.create(
                directory=directory,
                parent=parent
            )
        log_link_directory(request, directory, parent)
        response_data["success"] = True

    return JsonResponse(response_data)


@csrf_exempt
def remove_link_directory(request):
    check = check_token(request)
    if check: return JsonResponse(check)

    POST = request.POST
    response_data = {
        "success": False
    }
    if request.method == 'POST':
        directory_id = POST['directory_id'] if 'directory_id' in POST else None
        parent_id = POST['parent_id'] if 'parent_id' in POST else None
        directory = Directory.objects.get(id=directory_id)
        parent = Directory.objects.get(id=parent_id)
        if LinkedDirectory.objects.filter(directory=directory, parent=parent).exists():
            link = LinkedDirectory.objects.get(directory=directory,
                                               parent=parent)
            link.delete()
        log_remove_link_directory(request, directory, parent)
        response_data["success"] = True

    return JsonResponse(response_data)


@csrf_exempt
def cut_directory(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        src_directory_id = POST['src_directory_id'] if 'src_directory_id' in POST else None
        dst_directory_id = POST['dst_directory_id'] if 'dst_directory_id' in POST else None

        directory = Directory.objects.get(id=src_directory_id)
        dst_directory = Directory.objects.get(id=dst_directory_id)

        # Replace New Parent
        directory.parent = dst_directory
        directory.save()

        log_cut_directory(request, src_directory_id, directory)

    return JsonResponse(response_data)


@csrf_exempt
def get_ancestry_api(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        directory = Directory.objects.get(id=directory_id)

        response_data['ancestry'] = get_ancestry(directory)

    return JsonResponse(response_data)


@csrf_exempt
def get_descendance_api(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    POST = request.POST
    response_data = {}
    if request.method == 'POST':
        directory_id = POST['directory_id'] if 'directory_id' in POST else None

        directory = Directory.objects.get(id=directory_id)

        # response_data['descendance'] = get_descendance(directory)

    return JsonResponse(response_data)

@csrf_exempt
def get_department_guests(request,user_id):
    # check = check_token(request)
    # if check: return JsonResponse(check)
    from pprint import pprint
    response_data = {
        'public': [],
       
    }

    userDepartmentList = get_user_department_list(user_id, True) if (user_id != '' and user_id != 0) else []

     # Public
    departmentQuery = Department.objects.filter(is_support=False).order_by('name')
                # Clone Office to Public
                # response_data['public'] = deepcopy(response_data['departments'])
                # Exclude departments in Office
    

    for department in departmentQuery:
        departmentData = get_directory_tree_structure(department.root_directory.id, {})
        urlPermission = "pub"
        # pprint(departmentData)
        # exit()
        if len(userDepartmentList):
            urlPermission = get_url_permission(departmentData['directory_id'], userDepartmentList)

        departmentData.update({'urlPermission': urlPermission})
        
        response_data['public'].append(departmentData)
        
    return JsonResponse(response_data)

@csrf_exempt
def get_directory_tree_by_guest(request):
    response_data = {
        'public': [],
        'departments': []
    }
    # if request.method == 'POST':
        # if 'user_id' in request.POST:
        #     user_id = request.POST['user_id']
        #     user = User.objects.get(id=user_id)
        #     if user:

                # Office
                # departmentQuery = UserDepartment.objects.filter(user=user.id).only('department').order_by(
                #     'department__name')
                # for department in departmentQuery:
                #     response_data['departments'].append(
                #         get_directory_tree_structure(department.department.root_directory.id, {})
                #     )
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
    # for department in response_data['departments']:
    #     departmentQuery = departmentQuery.exclude(root_directory__id=department['directory_id'])

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

        # else:
        #     response_data['error'] = 'Incomplete Parameters'
    # else:
    #     response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)


@csrf_exempt
def get_directory_details_guest(request):
   
    response_data = {}

    if request.method == 'POST':
        filter_form = parse_filter_forms(request.POST)

        directory_id = request.POST['directory_id']
        # user_id = request.POST['user_id']
        directory = get_directory(directory_id)
        # user = User.objects.get(id=user_id)
        if directory is None: return JsonResponse({'error': 'Directory Not Found'})
        # if user is None: return JsonResponse({'error': 'User Not Found'})

        response_data['children'] = []
        response_data['links'] = []
        response_data['children_groups'] = []
        response_data['documents'] = []

        def get_children(directory):
            nonlocal response_data

            children_query = directory.children.all().only('name', 'description', 'group')

            if children_query.exists():
                for child in children_query:
                    if child.is_trashed: continue
                    if filter_form['search_key']:
                        if filter_form['search_key'].lower() not in child.name.lower(): continue
                    group_name = child.group.name if child.group else "Ungrouped"
                    if group_name not in response_data['children_groups']:
                        response_data['children_groups'].append(group_name)
                    response_data['children'].append({
                        'id': child.id,
                        'name': child.name,
                        'description': child.description,
                        'group': group_name,
                        'has_children': child.children.all().exists()
                    })

        def get_links(directory):
            nonlocal response_data

            link_query = directory.links.all()

            if link_query.exists():
                if 'LINKS' not in response_data['children_groups']:
                    response_data['children_groups'].append('LINKS')
                for link in link_query:
                    if link.directory.is_trashed: continue
                    if filter_form['search_key']:
                        if filter_form['search_key'].lower() not in link.directory.name.lower(): continue
                    # response_data['links'].append({
                    #     'id': link.directory.id,
                    #     'name': link.directory.name,
                    #     'description': link.directory.description,
                    # })
                    response_data['children'].append({
                        'id': link.directory.id,
                        'name': link.directory.name,
                        'description': link.directory.description,
                        'group': 'LINKS',
                        'is_link': True,
                        'has_children': link.directory.children.all().exists()
                    })

        def get_documents(directory_id, filter_public=False):
            nonlocal response_data

            docdir_query = DocumentDirectory.objects.filter(directory=directory_id).only('document')
            docdir_query = filter_document(docdir_query, filter_form)
            if filter_public: docdir_query = docdir_query.filter(is_public=True)
            if filter_form['search_key']: docdir_query = search_document(docdir_query, filter_form['search_key'])

            if docdir_query.exists():
                for docdir in docdir_query:
                    if docdir.is_trashed: continue
                    document = docdir.document
                    attachments = []

                    attachment_query = document.attachments.all().only('attachment')
                    if attachment_query.exists():
                        for attachment in attachment_query:
                            attachments.append(attachment.attachment.name)
                    attachments.reverse()

                    response_data['documents'].append({
                        'id': document.id,
                        'title': document.title,
                        'is_public': docdir.is_public,
                        'attachments': attachments,
                        'created_at': document.created_at,
                        'updated_at': document.updated_at,
                        'directory_id': docdir.directory.id,
                        'docdir_id': docdir.id,
                        'is_copy': docdir.is_copy,
                        'is_link': docdir.is_link,
                        'link': docdir.link.id if docdir.link else None,
                        'link_directory': docdir.link.directory.id if docdir.link else None,
                        'is_guest': docdir.is_guest,
                    })

        def get_subdirectories_and_documents(directory, include_sub=False, filter_public=False):
            nonlocal response_data

            get_documents(directory.id, filter_public)
            get_children(directory)
            get_links(directory)

            if include_sub:
                children_query = directory.children.all()
                for child in children_query:
                    get_subdirectories_and_documents(child, include_sub, filter_public)

        if filter_form['search_scope'] == 'anywhere':

            # Collect all directories and documents within user offices and
            # all directories and public documents on all offices with regards
            # to search_key

            # dep_query = Department.objects.filter(is_support=False).only('root_directory')
            # my_departments = get_my_departments(user_id)
            # for dep in my_departments:
            #     get_subdirectories_and_documents(dep.root_directory, True)
            #     dep_query = dep_query.exclude(id=dep.id)
            for dep in dep_query:
                get_subdirectories_and_documents(dep.root_directory, True, True)

        elif filter_form['search_scope'] == 'directory':

            # Collect directories and documents within directory
            # with regards to search_key

            get_subdirectories_and_documents(directory, True)

        else:

            # Collect Directory Properties
            response_data['name'] = directory.name
            response_data['description'] = directory.description
            response_data['is_public'] = directory.is_public

            group = directory.group
            response_data['group'] = {
                'id': group.id if group else 0,
                'name': group.name if group else 'Ungrouped',
                'description': group.description if group else ''
            }

            response_data['moderators'] = []
            response_data['accreditors'] = []

            get_subdirectories_and_documents(directory)

            # Ancestry
            response_data['ancestry'] = get_ancestry(directory)

            # Tree
            response_data['tree'] = get_tree(directory)

            # Moderators
            moderators_query = directory.moderators.all().only('user')
            for item in moderators_query:
                response_data['moderators'].append({
                    'id': item.user.id,
                    'name': '{}{}{}'.format(item.user.first_name, ' ' if item.user.first_name else '',
                                            item.user.last_name)
                })

            # Accreditors
            accreditor_query = directory.accreditors.all().only('user')
            for item in accreditor_query:
                response_data['accreditors'].append({
                    'id': item.user.id,
                    'name': '{}{}{}'.format(item.user.first_name, ' ' if item.user.first_name else '',
                                            item.user.last_name)
                })

        # Data Sorting
        response_data['children_groups'].sort()
        response_data['children'] = sorted(
            response_data['children'],
            key=lambda x: x['name'],
            reverse=not filter_form['ascending']
        )
        response_data['documents'] = sorted(
            response_data['documents'],
            key=lambda x: x[filter_form['sort_by']],
            reverse=not filter_form['ascending']
        )

    else:
        response_data['error'] = 'Non-POST Request'

    return JsonResponse(response_data)

@csrf_exempt
def get_public_documents(request):
    response_data = {}

    if request.method == 'POST':
        filter_form = parse_filter_forms(request.POST)

        response_data['documents'] = []
        response_data['children_groups'] = []

        directory_id = request.POST['directory_id']

        directory = get_directory(directory_id)

        if directory is None: return JsonResponse({'error': 'Directory Not Found'})
        
        # Collect Directory Properties
        response_data['name'] = directory.name
        response_data['description'] = directory.description
        response_data['is_public'] = directory.is_public

        globaldir_query = GlobalDirectory.objects.filter(root_directory=directory_id)
        from pprint import pprint
        if globaldir_query.exists():
            for globaldir in globaldir_query:
                docdir = DocumentDirectory.objects.filter(document=globaldir.document_id).first()
                if docdir.is_trashed: continue
                
                document = globaldir.document
                attachments = []

                attachment_query = document.attachments.all().only('attachment')
                if attachment_query.exists():
                    for attachment in attachment_query:
                        attachments.append(attachment.attachment.name)
                attachments.reverse()

                response_data['documents'].append({
                    'id': document.id,
                    'title': document.title,
                    'is_public': docdir.is_public,
                    'attachments': attachments,
                    'created_at': document.created_at,
                    'updated_at': document.updated_at,
                    'directory_id': docdir.directory.id,
                    'docdir_id': docdir.id,
                    'is_copy': docdir.is_copy,
                    'is_link': docdir.is_link,
                    'link': docdir.link.id if docdir.link else None,
                    'link_directory': docdir.link.directory.id if docdir.link else None,
                    'is_guest': docdir.is_guest,
                })
            
            response_data['documents'] = sorted(
                response_data['documents'],
                key=lambda x: x[filter_form['sort_by']],
                reverse=not filter_form['ascending']
            )
    else:
        response_data['error'] = 'Non-POST Request'
    
    return JsonResponse(response_data)

@csrf_exempt
def get_parents_directory(request):
    response_data = {
        'directories':[]
    }

    user_id = request.POST['user_id'] if request.POST['user_id'] != '0' else ''

    from django.conf import settings
    BASE_URL = settings.ENV('BASE_URL')

    userDepartmentList = get_user_department_list(user_id) if user_id != '' else []
            
    departmentQuery = Department.objects.filter(is_support=False).order_by('name')

    for department in departmentQuery:
        urlPermission = "pub"

        if len(userDepartmentList):
            urlPermission = get_url_permission(department.id, userDepartmentList)

        url = str(BASE_URL + urlPermission + str(department.root_directory_id))

        datum = {
            'id':department.root_directory_id,
            'key':department.id,
            'name':department.name,
            'url': url,
            'deptPrefix': urlPermission,
            }

        children = get_child_directory(department.root_directory_id, urlPermission)

        if children:
            datum.update({'children':children})

        response_data['directories'].append(datum)

    return JsonResponse(response_data)

def get_directory_link_description(request,directory_id=None):
    response_data = {
        'linkDescription':[]
    }

    collegeDescriptionQuery = CollegeDescription.objects.filter(directory_id=directory_id, is_deleted=0).order_by('id')
    for description in collegeDescriptionQuery:
        details = []
        detailsQuery = CollegeDescriptionDetail.objects.filter(is_deleted=0).filter(college_description_id=description.id)
        for detail in detailsQuery:
            datum = {
                'id': detail.id,
                'description': detail.description,
                'link': detail.link,
                'college_description_id': detail.college_description_id,
            }
            details.append(datum)
        datum = {
            'id':description.id,
            'title':description.title,
            'directory_id':description.directory_id,
            'details': details
        }
        response_data['linkDescription'].append(datum)

    return JsonResponse(response_data)

@csrf_exempt
def get_child_directory(directory_id, urlPermission):
    from django.conf import settings
    BASE_URL = settings.ENV('BASE_URL')

    children = []
    subDepartmentQuery = Directory.objects.filter(parent_id=directory_id).order_by('name')
    if subDepartmentQuery:
        for subDepartment in subDepartmentQuery:
            b = {
                'key': subDepartment.id,
                "id": subDepartment.id,
                "name": subDepartment.name,
                "description": subDepartment.description,
                "url": str(BASE_URL + urlPermission + str(subDepartment.id)),
                'deptPrefix': urlPermission,
            }
            grand_child = get_grand_child_directory(subDepartment.id, urlPermission)
            if grand_child:
                b.update({'children': grand_child})
            children.append(b)
            
    return children

@csrf_exempt
def get_grand_child_directory(directory_id, urlPermission):
    from django.conf import settings
    BASE_URL = settings.ENV('BASE_URL')

    children = []
    subDepartmentQuery = Directory.objects.filter(parent_id=directory_id).order_by('name')
    if subDepartmentQuery:
        for subDepartment in subDepartmentQuery:
            b = {
                 'key': subDepartment.id,
                 "id":subDepartment.id,
                 "name":subDepartment.name,
                 "description":subDepartment.description,
                 "url": str(BASE_URL + urlPermission + str(subDepartment.id)),
                 'deptPrefix': urlPermission,
            }
            children.append(b)
    return children

@csrf_exempt
def get_child_directory_by_parent_id(request):
    directory_id = request.POST['directory_id']
    dept_prefix = request.POST['dept_prefix']

    response_data = {
        'children_directories':[]
    }
    children = get_child_directory(directory_id, dept_prefix)
    response_data['children_directories'] = children
    return JsonResponse(response_data)

@csrf_exempt
def update_directory_link(request):
    response_data = {
        'success': False,
        'id': 0,
    }
    post = request.POST
    id = post.get('id', None)
    directory_id = post.get('directory_id', None)
    title = post.get('title', None)
    details = json.loads(post['details'])

    try:
        collegeDescriptionObj = CollegeDescription.objects.get(id=id)
        collegeDescriptionObj.title = title
        collegeDescriptionObj.save()
    except:
        CollegeDescription.objects.create(
            title=title,
            directory_id=directory_id,
        )
        id = CollegeDescription.objects.latest('id').id
    CollegeDescriptionDetail.objects.filter(college_description_id=id).filter(is_deleted=0).update(is_deleted=1)
    for detail in details:
        if 'id' in detail:
            try:
                detailObj = CollegeDescriptionDetail.objects.get(id=detail['id'])
                detailObj.description = detail['description']
                detailObj.link = detail['link']
                detailObj.is_deleted = 0
                detailObj.save()
                response_data['success'] = True
            except:
                pass
        else:
            try:
                CollegeDescriptionDetail.objects.create(
                    description=detail['description'],
                    link=detail['link'],
                    college_description_id= id,
                )
                response_data['success'] = True
            except:
                pass
    response_data['id'] = id
    return JsonResponse(response_data)

@csrf_exempt
def delete_directory_link(request):
    response_data = {
        'success': False,
    }
    post = request.POST
    id = post.get('id', None)
    try:
        collegeDescriptionObj = CollegeDescription.objects.get(id=id)
        collegeDescriptionObj.is_deleted = 1
        collegeDescriptionObj.save()
        CollegeDescriptionDetail.objects.filter(college_description_id=id).filter(is_deleted=0).update(is_deleted=1)
        response_data['success'] = True
        CollegeDescriptionDetail.save()
    except:
        pass

    return JsonResponse(response_data)