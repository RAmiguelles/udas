from ..authentication.utils import get_user_by_token, get_client_ip, get_client_geo
from ..directory.models import Log
from ..directory.utils import get_ancestry


def log(request, directory, action, details):
    ip_address = get_client_ip(request)
    geo = get_client_geo(ip_address)
    Log.objects.create(
        user=get_user_by_token(request),
        directory=directory,
        action=action,
        details=details,
        ip_address=ip_address,
        country=geo['country'],
        city=geo['city'],
        latitude=geo['latitude'],
        longitude=geo['longitude'],
    )
    return


def get_directory_info(directory):
    moderators = []
    for moderator in directory.moderators.all():
        moderators.append(moderator.user)
    details = {
        'id': directory.id,
        'name': directory.name,
        'description': directory.description,
        'group': directory.group,
        'is_public': directory.is_public,
        'moderators': moderators,
        'ancestry': get_ancestry(directory)
    }
    return details


def append_directory_log_details(details):
    log_details = ''

    log_details += append_directory_path_log_details(details)

    if details['description']:
        log_details += ' | DESCRIPTION: {}'.format(details['description'])
    if details['group']:
        log_details += ' | GROUP: {}'.format(details['group'])
    if details['is_public']:
        log_details += ' | IS PUBLIC: {}'.format(details['is_public'])

    log_details += append_directory_moderators_log_details(details)

    return log_details


def append_directory_moderators_log_details(details):
    log_details = ''
    moderators = ''
    if len(details['moderators']) > 0:
        for i, moderator in enumerate(details['moderators']):
            if i: moderators += ', '
            moderators += '(id:{}, name:{} {})'.format(moderator.id, moderator.first_name, moderator.last_name)
        log_details += ' | MODERATOR: {}'.format(moderators)

    return log_details


def append_directory_path_log_details(details):
    log_details = ''
    path = ''
    for i, directory in enumerate(details['ancestry']):
        if i: path += ' > '
        path += directory['name']
    log_details += 'PATH: {}'.format(path)

    return log_details


def log_create_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)

    log(request, directory, 'CREATE', log_details)
    return


def log_update_directory(request, old_details, directory):
    new_details = get_directory_info(directory)

    log_details = append_directory_path_log_details(new_details)

    log_details += ' | UPDATES => '

    if old_details['name'] != new_details['name']:
        log_details += ' | NAME: {}'.format(new_details['name'])
    if old_details['description'] != new_details['description']:
        log_details += ' | DESCRIPTION: {}'.format(new_details['description'])
    if old_details['group'] != new_details['group']:
        log_details += ' | GROUP: {}'.format(new_details['group'])
    if old_details['is_public'] != new_details['is_public']:
        log_details += ' | IS PUBLIC: {}'.format(new_details['is_public'])

    moderators = ''
    if old_details['moderators'] != new_details['moderators'] and len(new_details['moderators']) > 0:
        for i, moderator in enumerate(new_details['moderators']):
            if i: moderators += ', '
            moderators += '(id:{}, name:{} {})'.format(moderator.id, moderator.first_name, moderator.last_name)
        log_details += ' | MODERATOR: {}'.format(moderators)

    log_details += append_directory_moderators_log_details(new_details)

    log(request, directory, 'UPDATE', log_details)
    return


def log_destroy_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log(request, directory, 'DELETE', log_details)
    return


def log_destroy_all_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log(request, directory, 'DELETE ALL', log_details)
    return


def log_trash_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log(request, directory, 'TRASH', log_details)
    return


def log_restore_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log(request, directory, 'RESTORE', log_details)
    return


def log_restore_all_directory(request, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log(request, directory, 'RESTORE ALL', log_details)
    return


def log_copy_directory(request, source_directory, directory):
    details = get_directory_info(directory)
    log_details = 'SOURCE DIRECTORY ID: {} | '.format(source_directory)
    log_details += append_directory_log_details(details)

    log(request, directory, 'COPY', log_details)
    return


def log_link_directory(request, directory, parent):
    log_details = 'DIRECTORY ID: {} | '.format(directory.id)
    log_details += append_directory_log_details(get_directory_info(directory))
    log_details += ' PARENT ID: {} | '.format(parent.id)
    log_details += append_directory_log_details(get_directory_info(directory))
    log(request, directory, 'LINK', log_details)
    return


def log_remove_link_directory(request, directory, parent):
    log_details = 'DIRECTORY ID: {} | '.format(directory.id)
    log_details += append_directory_log_details(get_directory_info(directory))
    log_details += ' PARENT ID: {} | '.format(parent.id)
    log_details += append_directory_log_details(get_directory_info(directory))
    log(request, directory, 'REMOVE LINK', log_details)
    return


def log_cut_directory(request, source_directory, directory):
    details = get_directory_info(directory)
    log_details = append_directory_log_details(details)
    log_details += ' | OLD PARENT DIRECTORY ID: {}'.format(source_directory)

    log(request, directory, 'MOVE', log_details)
    return
