from ..department.models import Department, UserDepartment
from ..directory.models import Directory
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse

def get_ancestry(directory):
    ancestry = [{
        'id': directory.id,
        'name': directory.name,
        'has_children': directory.children.exists()
    }]
    parent = directory.parent
    while True:
        if parent:
            ancestry.append({
                'id': parent.id,
                'name': parent.name,
                'has_children': True
            })
            parent = parent.parent
        else:
            break
    ancestry.reverse()
    return ancestry


def get_tree(directory):
    def get_details():
        response_data = {}
        response_data['directory_id'] = directory.id
        response_data['name'] = directory.name
        response_data['description'] = directory.description
        response_data['is_public'] = directory.is_public
        if directory.group:
            response_data['group'] = {
                'id': directory.group.id,
                'name': directory.group.name,
                'description': directory.group.description
            }
        else:
            response_data['group'] = {
                'id': 0,
                'name': 'Ungrouped',
                'description': ''
            }
        response_data['children'] = []
        response_data['children_groups'] = []
        childrenQuery = directory.children.all()
        for child in childrenQuery:
            group_name = child.group.name if child.group else "Ungrouped"
            if group_name not in response_data['children_groups']:
                response_data['children_groups'].append(group_name)
            response_data['children'].append({
                'directory_id': child.id,
                'name': child.name,
                'has_children': child.children.exists(),
                'children': [],
                'group': {
                    'id': child.group.id,
                    'name': child.group.name,
                    'description': child.group.description
                } if child.group else {
                    'id': 0,
                    'name': 'Ungrouped',
                    'description': ''
                }
            })

    tree = {}

    ancestry = [{
        'directory_id': directory.id,
        'name': directory.name,
        'has_children': directory.children.exists()
    }]
    parent = directory.parent
    while True:
        if parent:
            ancestry.append({
                'id': parent.id,
                'name': parent.name,
                'has_children': True
            })
            parent = parent.parent
        else:
            break
    ancestry.reverse()
    return ancestry


def get_directory(directory_id):
    try:
        return Directory.objects.get(id=directory_id)
    except:
        return None


def get_directory_tree_structure(directory_id, response_data):
    directory = Directory.objects.get(id=directory_id)
    if directory:
        response_data['directory_id'] = directory.id
        response_data['name'] = directory.name
        response_data['description'] = directory.description
        response_data['is_public'] = directory.is_public
        if directory.group:
            response_data['group'] = {
                'id': directory.group.id,
                'name': directory.group.name,
                'description': directory.group.description
            }
        else:
            response_data['group'] = {
                'id': 0,
                'name': 'Ungrouped',
                'description': ''
            }
        response_data['children'] = []
        response_data['children_groups'] = []
        # childrenQuery = directory.children.all()
        # for child in childrenQuery:
        #     group_name = child.group.name if child.group else "Ungrouped"
        #     if group_name not in response_data['children_groups']:
        #         response_data['children_groups'].append(group_name)
        #     # response_data['children'].append(get_directory_tree_structure(child.id, {}))
        #     response_data['children'].append({
        #         'directory_id': child.id,
        #         'name': child.name,
        #         'has_children': child.children.exists(),
        #         'children': [],
        #         'group': {
        #             'id': child.group.id,
        #             'name': child.group.name,
        #             'description': child.group.description
        #         } if child.group else {
        #             'id': 0,
        #             'name': 'Ungrouped',
        #             'description': ''
        #         }
        #     })

    return response_data


def get_directory_count(total_dir, total_doc, directory):
    children = directory.children.all()
    total_dir += children.count()
    total_doc += directory.docdirs.all().count()
    if children.exists():
        for child in children:
            total_dir, total_doc = get_directory_count(total_dir, total_doc, child)
    return total_dir, total_doc


def get_department_by_dir(directory):
    root_id = get_ancestry(directory)[0]['id']
    department = Department.objects.get(root_directory=root_id)
    return department

def get_sub_directory_by_dirs(directory_id,response_data):
    # response_rs = {"name" : []}
    # directory = Directory.objects.filter(parent_id=directory_id)
    # return directory
    # for sub_directory in directory:
    #      response_data['names'].append({
    #             #'id': sub_directory.group.id,
    #             'name': sub_directory.group.name,
    #             # 'description': sub_directory.group.description
    #         })
    response_data['subDepartments'].append({"data" : "xx"})
    return JsonResponse(response_data)
    return directory_id
   # return response_data    

def get_user_department_list(user_id, by_department=False):
    user = User.objects.get(id=user_id)

    userDepartmentList = []

    if user:
        userDepartmentQuery = UserDepartment.objects.filter(user=user.id).only('department').order_by('department__name')

        for userDept in userDepartmentQuery:
            if not by_department:
                userDepartmentList.append(userDept.department_id)
            else:
                userDepartmentList.append(userDept.department.root_directory_id)

    return userDepartmentList


def get_url_permission(directory_id, list):
    setList = set(list)

    canAccess = True if directory_id in setList else False
        
    url = "dep" if canAccess else "pub" 

    return url

# #  # OF DIRECTORIES PER COLLEGE
# deptQuery = Department.objects.all()

# for dept in deptQuery:
#     total_dir = 0
#     total_doc = 0
#     total_affiliated_user = dept.users.all().count()
#     root = dept.root_directory
#     total_dir, total_doc = get_directory_count(total_dir, total_doc, root)

#     print()
#     print(dept.name)
#     print('# OF AFFILIATED USERS:', total_affiliated_user)
#     print('# OF DIRECTORIES:', total_dir)
#     print('# OF DOCUMENTS:', total_doc)

# directories = [
#     # {
#     #     'name': 'CEd BEED',
#     #     'directory_id': 6306
#     # },
#     # {
#     #     'name': 'CEd BSED',
#     #     'directory_id': 227236
#     # },
# ]
#
# for dir in directories:
#     total_dir = 0
#     total_doc = 0
#     directory = Directory.objects.get(id=dir['directory_id'])
#     total_dir, total_doc = get_directory_count(total_dir, total_doc, directory)
#
#     print()
#     print(dir['name'])
#     print('# OF DIRECTORIES:', total_dir)
#     print('# OF DOCUMENTS:', total_doc)
#
# from .models import Log as DirectoryLog
# from ..document.models import Log as DocumentLog
# import datetime
#
# ranges = [
#     {"name": "March 2020", "start": [2020, 3, 1], "end": [2020, 3, 31]},
#     {"name": "April 2020", "start": [2020, 4, 1], "end": [2020, 4, 30]},
#     {"name": "May 2020", "start": [2020, 5, 1], "end": [2020, 5, 31]},
#     {"name": "June 2020", "start": [2020, 6, 1], "end": [2020, 6, 30]},
#     {"name": "July 2020", "start": [2020, 7, 1], "end": [2020, 7, 31]},
#     {"name": "August 2020", "start": [2020, 8, 1], "end": [2020, 8, 31]},
#     {"name": "September 2020", "start": [2020, 9, 1], "end": [2020, 9, 30]},
#     {"name": "October 2020", "start": [2020, 10, 1], "end": [2020, 10, 31]},
#     {"name": "November 2020", "start": [2020, 11, 1], "end": [2020, 11, 30]},
#     {"name": "December 2020", "start": [2020, 12, 1], "end": [2020, 12, 31]},
#     {"name": "January 2021", "start": [2021, 1, 1], "end": [2021, 1, 31]},
#     {"name": "February 2021", "start": [2021, 2, 1], "end": [2021, 2, 28]},
#     {"name": "March 2021", "start": [2021, 3, 1], "end": [2021, 3, 31]},
# ]
#
# print("MONTHLY TREND REPORT")
# for range in ranges:
#     dir_created = DirectoryLog.objects.filter(
#         action='CREATE',
#         timestamp__range=[datetime.date(range['start'][0], range['start'][1], range['start'][2]),
#                           datetime.date(range['end'][0], range['end'][1], range['end'][2])])
#     dir_deleted = DirectoryLog.objects.filter(
#         action='DELETE',
#         timestamp__range=[datetime.date(range['start'][0], range['start'][1], range['start'][2]),
#                           datetime.date(range['end'][0], range['end'][1], range['end'][2])])
#     print(range["name"], 'directory', 'created:', dir_created.count(), 'deleted:',  dir_deleted.count())
#
#     doc_created = DocumentLog.objects.filter(
#         action='CREATE',
#         timestamp__range=[datetime.date(range['start'][0], range['start'][1], range['start'][2]),
#                           datetime.date(range['end'][0], range['end'][1], range['end'][2])])
#     doc_deleted = DocumentLog.objects.filter(
#         action='DELETE',
#         timestamp__range=[datetime.date(range['start'][0], range['start'][1], range['start'][2]),
#                           datetime.date(range['end'][0], range['end'][1], range['end'][2])])
#     print(range["name"], 'document', 'created:', doc_created.count(), 'deleted:',  doc_deleted.count())
