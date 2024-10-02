from ..authentication.utils import get_user_by_token, get_client_ip, get_client_geo
from ..department.models import Log, UserDepartment


def log(request, department, action, details):
    ip_address = get_client_ip(request)
    geo = get_client_geo(ip_address)
    Log.objects.create(
        user=get_user_by_token(request),
        department=department,
        action=action,
        details=details,
        ip_address=ip_address,
        country=geo['country'],
        city=geo['city'],
        latitude=geo['latitude'],
        longitude=geo['longitude'],
    )
    return


def get_department_info(department):
    heads = []
    for userdept in UserDepartment.objects.filter(department=department.id, is_head=True):
        heads.append(userdept.user)
    details = {
        'id': department.id,
        'name': department.name,
        'root_directory': department.root_directory,
        'is_support': department.is_support,
        'heads': heads,
    }
    return details


def append_department_log_details(details):
    log_details = ''

    if details['name']:
        log_details += 'Name: {}'.format(details['name'])
    if details['is_support']:
        log_details += ' | IS SUPPORT: {}'.format(details['is_support'])

    log_details += append_department_heads_log_details(details)

    return log_details


def append_department_heads_log_details(details):
    log_details = ''
    heads = ''
    if len(details['heads']) > 0:
        for i, head in enumerate(details['heads']):
            if i: heads += ', '
            heads += '(id:{}, name:{} {})'.format(head.id, head.first_name, head.last_name)
        log_details += ' | HEADS: {}'.format(heads)

    return log_details


def log_create_department(request, department):
    details = get_department_info(department)
    log_details = append_department_log_details(details)

    log(request, department, 'CREATE', log_details)
    return


def log_update_department(request, old_details, department):
    new_details = get_department_info(department)

    log_details = 'UPDATES => '

    if old_details['name'] != new_details['name']:
        log_details += ' | NAME: {}'.format(new_details['name'])
    if old_details['is_support'] != new_details['is_support']:
        log_details += ' | IS SUPPORT: {}'.format(new_details['is_support'])

    heads = ''
    if old_details['heads'] != new_details['heads'] and len(new_details['heads']) > 0:
        for i, head in enumerate(new_details['heads']):
            if i: heads += ', '
            heads += '(id:{}, name:{} {})'.format(head.id, head.first_name, head.last_name)
        log_details += ' | HEADS: {}'.format(heads)

    log(request, department, 'UPDATE', log_details)
    return
