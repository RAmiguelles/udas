from datetime import datetime

import requests
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from ..authentication.models import Profile


def populate_users(sender, **kwargs):
    print('\n\nPOPULATING USERS ...\n\n')
    try:
        from django.conf import settings
        USERS_API = settings.ENV('USERS_API')
        TOKEN_HRIS = settings.ENV('TOKEN_HRIS')

        users = requests.post(USERS_API, {
            'token': TOKEN_HRIS,
        }).json()

        timestamp = datetime.now()
        added = 0
        updated = 0

        for item in users:
            if User.objects.filter(username=item['PmapsId']).exists():
                user = User.objects.get(username=item['PmapsId'])
                user.first_name = item['FirstName'] if item['FirstName'] else ''
                user.last_name = item['LastName'] if item['LastName'] else ''
                user.is_staff = False
                user.save()
                updated += 1
                print('Updating ', item)
            else:
                User.objects.create(
                    username=item['PmapsId'],
                    first_name=item['FirstName'] if item['FirstName'] else '',
                    last_name=item['LastName'] if item['LastName'] else '',
                    is_staff=False
                )
                added += 1
                print('Adding ', item)

        print('''

            ####################################
            ##                                ##
            ##       USERS  SYNCRONIZED       ##
            ##                                ##
            ####################################

            Date: {timestamp}
            Users Added: {added}
            Users Updated: {updated}

            '''.format(
            timestamp=timestamp,
            added=added,
            updated=updated
        ))

        userQuery = User.objects.all()
        for user in userQuery:
            if not Profile.objects.filter(user=user.id).exists():
                Profile.objects.create(user=user)

    except:
        pass

def populate_users_status(sender, **kwargs):
    print('\n\nPOPULATING USERS ...\n\n')
    try:
        from django.conf import settings
        USERS_API = settings.ENV('USERS_API')
        TOKEN_HRIS = settings.ENV('TOKEN_HRIS')

        users = requests.post(USERS_API, {
            'token': TOKEN_HRIS,
        }).json()

        timestamp = datetime.now()
        added = 0
        updated = 0

        for item in users:
            if User.objects.filter(username=item['PmapsId']).exists():
                user = User.objects.get(username=item['PmapsId'])
                user.first_name = item['FirstName'] if item['FirstName'] else ''
                user.last_name = item['LastName'] if item['LastName'] else ''
                user.is_staff = False
                if item['Status'] == "Active":
                    user.is_active = 1
                else:
                    user.is_active = 0
                user.save()
                updated += 1
                print('Updating ', item)
            else:
                User.objects.create(
                    username=item['PmapsId'],
                    first_name=item['FirstName'] if item['FirstName'] else '',
                    last_name=item['LastName'] if item['LastName'] else '',
                    is_staff=False
                )
                added += 1
                print('Adding ', item)

        print('''

            ####################################
            ##                                ##
            ##       USERS  SYNCRONIZED       ##
            ##                                ##
            ####################################

            Date: {timestamp}
            Users Added: {added}
            Users Updated: {updated}

            '''.format(
            timestamp=timestamp,
            added=added,
            updated=updated
        ))

        userQuery = User.objects.all()
        for user in userQuery:
            if not Profile.objects.filter(user=user.id).exists():
                Profile.objects.create(user=user)

    except:
        pass

user_logged_in.connect(populate_users)
