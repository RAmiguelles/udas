from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import UserDepartment
from .utils import get_department
from ..authentication.utils import check_token
from ..directory.models import Directory, Moderator


@csrf_exempt
def get_users(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        users = []
        query = User.objects.all()
        query = query.filter(is_active=True, is_superuser=False).distinct().order_by('first_name')
        # query = query.distinct()[:5]
        for user in query:
            if 'accreditor' in '{}{}{}'.format(
                    user.first_name,
                    ' ' if user.first_name else '',
                    user.last_name).lower(): continue
            data.append({
                'id': user.id,
                'name': '{}{}{}'.format(
                    user.first_name,
                    ' ' if user.first_name else '',
                    user.last_name)
            })
    return JsonResponse({'suggestions': data})


@csrf_exempt
def get_department_users(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        directory_id = request.POST['directory_id'] if 'directory_id' in request.POST else None
        user_id = request.POST['user_id'] if 'user_id' in request.POST else None
        department = get_department(directory_id)

        key, users = '', []
        if 'key' in request.POST:
            key = request.POST['key'].lower()

        query = UserDepartment.objects.filter(department=department.id, is_head=False)
        for user_dept in query:
            if key not in '{}{}{}'.format(
                    user_dept.user.first_name,
                    ' ' if user_dept.user.first_name else '',
                    user_dept.user.last_name).lower():
                query = query.exclude(id=user_dept.id)

        directory = Directory.objects.get(id=directory_id)
        moderators = list(Moderator.objects.all())
        while True:
            for moderator in moderators:
                if moderator.directory.id == directory.id:
                    query = query.exclude(user__id=moderator.user.id)
            if directory.parent:
                directory = directory.parent
            else:
                break

        for user_id in users:
            query = query.exclude(user__id=user_id)
        query = query.filter(user__is_active=True, user__is_superuser=False).distinct()
        query = query.distinct()[:5]
        for item in query:
            if item.user.id != int(user_id):
                data.append({
                    'id': item.user.id,
                    'name': '{}{}{}'.format(
                        item.user.first_name,
                        ' ' if item.user.first_name else '',
                        item.user.last_name)
                })
    return JsonResponse({'suggestions': data})
