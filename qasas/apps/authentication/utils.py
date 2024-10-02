import os

import geoip2.database
from rest_framework.authtoken.models import Token
from ..department.models import Department, UserDepartment

reader = geoip2.database.Reader(os.path.abspath('utils/GeoLite2-City.mmdb'))


def check_token(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        key = request.META['HTTP_AUTHORIZATION'][6:]
        token = Token.objects.filter(key=key)
        if not token:
            return {"detail": "Invalid token."}
    else:
        return {"detail": "Authentication credentials were not provided."}


def get_user_by_token(request):
    key = request.META['HTTP_AUTHORIZATION'][6:]
    token = Token.objects.get(key=key)
    return token.user


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_geo(ip_address):
    response = None
    try:
        response = reader.city(ip_address)
    except:
        pass
    geo = {
        'country': response.country.name if response else '',
        'city': response.city.name if response else '',
        'latitude': response.location.latitude if response else '',
        'longitude': response.location.longitude if response else '',
    }
    return geo

def check_is_support(user_id):
    userDepartmentQuery = UserDepartment.objects.values('department_id').filter(user_id=user_id).filter(is_active=1)
    deptQuery = Department.objects.filter(is_support=1).filter(id__in=userDepartmentQuery.values('department_id')).values('is_support')
    return userDepartmentQuery.filter(department_id__in=deptQuery.values('is_support')).exists()