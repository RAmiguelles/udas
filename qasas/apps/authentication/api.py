import requests
import json
from django.contrib.auth import authenticate
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

from .logger import log_login, log_logout
from ..app_admin.models import Setting
from ..app_admin.utils import populate_users
from ..authentication.utils import check_token, check_is_support
from ..department.models import Department,UserDepartment
from ..directory.models import Moderator, Accreditor
from ..department.utils import get_department
from django.db.models import Q

@csrf_exempt
def log_in(request):
    response_data = {}
    if request.method == 'POST':
        if 'employee_id' in request.POST and 'password' in request.POST:

            from django.conf import settings
            employee_id = request.POST['employee_id'].lstrip('0')
            password = request.POST['password']

            login, user = {}, None

            if not (settings.ENV('TEST_PASSWORD') and password == settings.ENV('TEST_PASSWORD')):

                # TRY TO AUTHENTICATE AT HRIS
                from django.conf import settings
                try:
                    USER_LOGIN_API = settings.ENV('USER_LOGIN_API')
                    TOKEN_HRIS = settings.ENV('TOKEN_HRIS')
                    login = requests.post(USER_LOGIN_API, {
                        'token': TOKEN_HRIS,
                        'pmaps_id': employee_id,
                        'password': password
                    }).json()
                except:
                    response_data['error'] = 'Unable to Connect'

            if 'id' in login:
                if not User.objects.filter(username=employee_id).exists():
                    populate_users('sender')

                user = User.objects.get(username=employee_id) or None
                if user is not None:
                    response_data['id'] = user.id
                    response_data['employee_id'] = employee_id
                    response_data['first_name'] = login['FirstName']
                    response_data['last_name'] = login['LastName']
                    response_data['avatar'] = login['FirstName'] + ' ' + login['LastName']
            else:
                user = authenticate(request, username=employee_id, password=password)
                if password == settings.ENV('TEST_PASSWORD'):
                    user = User.objects.get(username=employee_id) if \
                        User.objects.filter(username=employee_id).exists() else None
                if user is not None:
                    response_data['id'] = user.id
                    response_data['employee_id'] = user.username
                    response_data['first_name'] = user.first_name
                    response_data['last_name'] = user.last_name
                    response_data['avatar'] = user.username
                    response_data['error'] = None
                else:
                    if User.objects.filter(username=employee_id).exists():
                        response_data['error'] = 'Invalid Credentials'
                    else:
                        response_data['error'] = login['Error'] if 'Error' in login else 'Unable to Connect'

            if user is not None:
                response_data['is_accreditor'] = Accreditor.objects.filter(user=user.id).exists()
                response_data['is_admin'] = user.is_superuser

                response_data['privileges'] = {}
                response_data['CRUD_dirs'] = []
                for item in UserDepartment.objects.filter(user=user.id, is_head=True):
                    response_data['CRUD_dirs'].append(item.department.root_directory.id)
                for item in Moderator.objects.filter(user=user.id):
                    response_data['CRUD_dirs'].append(item.directory.id)

                response_data['test'] = []
                response_data['department'] = [] 
                processed_departments = set() 
                response_data['privileges']['accreditor'] = []
                for item in Accreditor.objects.filter(user=user.id):
                    response_data['privileges']['accreditor'].append(item.directory.id)
                    department = get_department(item.directory.id)
                    if department.id not in processed_departments:
                        processed_departments.add(department.id)
                        response_data['department'].append({
                            'id': department.id,
                            'name': department.name,
                            'root_directory': department.root_directory.id,
                            'is_support': department.is_support
                        })

                departmentQuery = UserDepartment.objects.filter(user=user.id)
                for department in departmentQuery:
                    response_data['department'].append({
                        'id': department.department.id,
                        'name': department.department.name,
                        'root_directory': department.department.root_directory.id,
                        'is_support': department.department.is_support,
                        'is_head': department.is_head
                    })

                try:
                    token = Token.objects.get(user=user.id)
                    if token: token.delete()
                except:
                    pass
                token = Token.objects.create(user=user)
                response_data['token'] = token.key

                settings = Setting.objects.filter(is_active=True).first()

                response_data['session_time_limit'] = settings.session_time_limit
                response_data['upload_filesize_limit'] = settings.upload_filesize_limit

                log_login(request, user)

        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'

    return JsonResponse(response_data)


@csrf_exempt
def log_out(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {}
    if request.method == 'POST':
        if 'user_id' in request.POST:
            user_id = request.POST['user_id']
            user = User.objects.get(id=user_id)
            try:
                token = Token.objects.get(user=user.id)
                if token: token.delete()
            except:
                pass
            response_data = {'detail': 'Success.'}
            log_logout(request, user)
        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)


@csrf_exempt
def getUsers(request):
    check = check_token(request)
    if check: return JsonResponse(check)

    response_data = {
        'users': []
    }
    users = User.objects.all()
    for user in users:
        response_data['users'].append({
            'username': user.username,
            'lastname': user.last_name,
            'firstname': user.first_name,
        })

    return JsonResponse(response_data)


@csrf_exempt
def getUsersInDepartment(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'users': []
    }
    if request.method == 'POST':
        if 'department_id' in request.POST:
            department_id = request.POST['department_id']
            user_departments = UserDepartment.objects.filter(department=department_id)
            for user_dept in user_departments:
                response_data['users'].append({
                    'username': user_dept.user.username,
                    'lastname': user_dept.user.last_name,
                    'firstname': user_dept.user.first_name,
                    'role': 'Head' if user_dept.is_head else 'Member',
                    'date_added': user_dept.created_at,
                })

        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)

@csrf_exempt
def getUsersUserDepartments(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'users': []
    }
    if request.method == 'POST':
        root_directory_id = request.POST.get("root_directory_id",False)
        if root_directory_id is not False:
            SUPPORT_DEPT = True
            userDepartmentQuery = UserDepartment.objects.filter(Q(department_id=Department.objects.get(root_directory_id=root_directory_id)) | Q(department__is_support=SUPPORT_DEPT)).filter(is_active=1).values('user_id').annotate(count=Count('*'))
            if userDepartmentQuery is not None:
                userQuerySet = User.objects.filter(id__in=userDepartmentQuery.values('user_id')).exclude(first_name='').exclude(last_name='').filter(is_active=1).order_by('last_name')
                for u in userQuerySet:
                    response_data['users'].append({
                        'id': u.id,
                        'username': u.username,
                        'lastname': u.last_name,
                        'firstname': u.first_name,
                    })
        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'

    return JsonResponse(response_data)
