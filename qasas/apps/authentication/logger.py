from ..authentication.models import Log
from ..authentication.utils import get_client_ip, get_client_geo


def log(request, action, user):
    ip_address = get_client_ip(request)
    geo = get_client_geo(ip_address)
    Log.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        country=geo['country'],
        city=geo['city'],
        latitude=geo['latitude'],
        longitude=geo['longitude'],
    )
    return


def log_login(request, user):
    log(request, 'LOGIN', user)
    return


def log_logout(request, user):
    log(request, 'LOGOUT', user)
    return
