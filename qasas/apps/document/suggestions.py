from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..authentication.utils import check_token
from ..document.models import Attribute, Keyword, Type


@csrf_exempt
def get_attribute_key_suggestions(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        key = ''
        attributesQuery = Attribute.objects
        if 'key' in request.POST:
            key = request.POST['key']
        attributesQuery = attributesQuery.filter(key__istartswith=key).distinct().values('key')[:5]
        for attribute in attributesQuery:
            data.append(attribute['key'])
    return JsonResponse({
        'suggestions': data
    })


@csrf_exempt
def get_attribute_value_suggestions(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        key, value = '', ''
        attributesQuery = Attribute.objects
        if 'key' in request.POST:
            key = request.POST['key']
        attributesQuery = attributesQuery.filter(value__istartswith=key).distinct().values('value')[:5]
        for attribute in attributesQuery:
            data.append(attribute['value'])
    return JsonResponse({
        'suggestions': data
    })


@csrf_exempt
def get_keyword_suggestions(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        key, keywords = '', []
        if 'key' in request.POST:
            key = request.POST['key']
        for form in request.POST:
            if form.startswith('k_'):
                keywords.append(request.POST['k_' + form[2:]])
        keywordsQuery = Keyword.objects.filter(keyword__istartswith=key)
        for key in keywords:
            keywordsQuery = keywordsQuery.exclude(keyword=key)
        keywordsQuery = keywordsQuery.distinct().values('keyword')[:5]
        for keyword in keywordsQuery:
            data.append(keyword['keyword'])
    return JsonResponse({
        'suggestions': data
    })


@csrf_exempt
def get_type_suggestions(request):
    check = check_token(request)
    if check: return JsonResponse(check)
    data = []
    if request.method == 'POST':
        key, types = '', []
        if 'key' in request.POST:
            key = request.POST['key']
        for form in request.POST:
            if form.startswith('type_'):
                types.append(request.POST['type_' + form[4:]])
        query = Type.objects.filter(name__istartswith=key).order_by('name')
        query = query.exclude(name='Others')
        for item in types:
            query = query.exclude(name=item)
        query = query.distinct().values('name')
        for item in query:
            data.append(item['name'])
        data.append('Others')
    return JsonResponse({
        'suggestions': data
    })
