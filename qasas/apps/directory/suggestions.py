from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..authentication.utils import check_token
from ..directory.models import Directory


@csrf_exempt
def get_directory_group_suggestion(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        if 'directory_id' in request.POST:
            key = ''
            if 'key' in request.POST:
                key = request.POST['key']
            directory_id = request.POST['directory_id']
            children = Directory.objects.get(id=directory_id).children.all()
            for child in children:
                if child.group and child.group.name not in data \
                        and child.group.name.lower().startswith(key.lower()):
                    data.append(child.group.name)
    return JsonResponse({
        'suggestions': data
    })
