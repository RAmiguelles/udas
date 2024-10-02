from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .logger import log_create_department, get_department_info, log_update_department
from ..authentication.utils import check_token
from ..department.models import UserDepartment, Department
from ..department.serializers import DepartmentSerializer, UserDepartmentSerializer
from ..directory.models import Directory
from ..directory.models import Accreditor
from ..department.utils import get_department

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = DepartmentSerializer

    def create(self, request):
        POST = request.POST

        name = POST['name'] if 'name' in POST else None
        head = POST['head'] if 'head' in POST else None

        name = name if name else 'No name'
        head = User.objects.get(id=head) if head else None

        department = Department.objects.create(
            name=name,
            root_directory=Directory.objects.create(name=name),
        )

        if head:
            UserDepartment.objects.create(
                user=head,
                department=department,
                is_head=True
            )

        log_create_department(request, department)

        return Response({'id': department.id})

    def retrieve(self, request, pk=None):

        response_data = {}

        department = Department.objects.get(root_directory=pk)
        heads = UserDepartment.objects.filter(department=department.id, is_head=True)

        response_data['id'] = department.id
        response_data['name'] = department.name
        response_data['heads'] = []

        for item in heads:
            response_data['heads'].append({
                'id': item.user.id,
                'name': '{} {}'.format(item.user.first_name, item.user.last_name)
            })

        return JsonResponse(response_data)

    def update(self, request, pk=None):

        POST = request.POST

        name = POST['name'] if 'name' in POST else None
        head = POST['head'] if 'head' in POST else None

        name = name if name else 'No name'
        head = User.objects.get(id=head) if head else None

        directory = Directory.objects.get(id=pk)
        directory.name = name
        directory.save()
        department = Department.objects.get(root_directory=pk)
        old_details = get_department_info(department)
        department.name = name
        department.save()

        # Remove all heads
        userDeptQuery = UserDepartment.objects.filter(department=department.id)
        for userdept in userDeptQuery:
            userdept.is_head = False
            userdept.save()

        # Clean Multiple rows of same user on department
        userdeptsQuery = UserDepartment.objects.filter(department=department.id)
        for userdept in userdeptsQuery:
            userdepts = UserDepartment.objects.filter(department=department.id, user=userdept.user.id)
            if userdepts.count() > 1:
                userdepts.delete()
                UserDepartment.objects.create(
                    user=userdept.user,
                    department=department
                )

        if head:
            # Remove user in the table to make sure on one appearance of user per department
            UserDepartment.objects.filter(department=department.id, user=head.id).delete()
            UserDepartment.objects.create(
                user=head,
                department=department,
                is_head=True
            )

        log_update_department(request, old_details, department)

        return Response({})


class UserDepartmentViewSet(viewsets.ModelViewSet):
    queryset = UserDepartment.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserDepartmentSerializer


@csrf_exempt
def get_public_departments(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'departments': []
    }

    departments = Department.objects.filter(is_support=False)
    for department in departments:
        response_data['departments'].append({
            'id': department.id,
            'name': department.name,
            'root_directory': department.root_directory.id,
        })

    return JsonResponse(response_data)

@csrf_exempt
def get_user_departments(request, user_id):
    from pprint import pprint

    response_data = {
        'departments': []
    }
    processed_departments = set()
    if(Accreditor.objects.filter(user=user_id).exists()):
        dires=Accreditor.objects.filter(user=user_id)
        for dire in dires:
            department =get_department(dire.directory_id)
            if department.id not in processed_departments:
                processed_departments.add(department.id)
                response_data['departments'].append({
                    'id':department.id,
                    'name': department.name,
                    'root_directory': department.root_directory.id,
                    'is_support': department.is_support,
                })
    else:                        
        departmentQuery = UserDepartment.objects.filter(user=user_id)
        for department in departmentQuery:
            response_data['departments'].append({
                'id': department.department.id,
                'name': department.department.name,
                'root_directory': department.department.root_directory.id,
                'is_support': department.department.is_support,
                'is_head': department.is_head
            })

    return JsonResponse(response_data)


@csrf_exempt
def getDepartments(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'departments': []
    }

    departments = Department.objects.all()
    for department in departments:
        response_data['departments'].append({
            'id': department.id,
            'name': department.name,
            'is_support': department.is_support,
            'no_of_users': 100,
            'no_of_dirs': 234,
            'no_of_docs': 23324,
            'storage_usage': 231.3,
        })

    return JsonResponse(response_data)
