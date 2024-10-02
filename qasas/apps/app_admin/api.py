from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..app_admin.models import Setting
from ..app_admin.utils import populate_users_status
from ..authentication.utils import check_token

@csrf_exempt
def test_connection(request):
    return JsonResponse({})


@csrf_exempt
def staging_log_in(request):
    response_data = {}
    if request.method == 'POST':
        if 'key' in request.POST and 'key' in request.POST:
            key = request.POST['key']

            setting = Setting.objects.filter(is_active=True).first()
            if not setting:
                setting = Setting.objects.filter(is_default=True).first()
            if not setting:
                setting = Setting.objects.all().first()

            if key == setting.staging_pass_key:
                response_data['staging_authenticated'] = True
            else:
                response_data['staging_authenticated'] = False
        else:
            response_data['error'] = 'Incomplete Parameters'
    else:
        response_data['error'] = 'Non-POST Request'
    return JsonResponse(response_data)

@csrf_exempt
def populate_hris_users(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    response_data = {
        'users': []
    }
    if request.method == 'POST':
        populate_users_status('sender')
        response_data['users'] = True
    else:
        response_data['error'] = 'Non-POST Request'

    return JsonResponse(response_data)