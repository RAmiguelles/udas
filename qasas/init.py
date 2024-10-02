from django.contrib.auth.models import User

from apps.app_admin.models import Setting
from apps.department.models import Department
from apps.directory.models import Directory
from apps.document.models import Type

# SUPER USER
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        'admin',
        'cjvlazo@usep.edu.ph',
        'Admin1010'
    )

# Support Office Department
if not Department.objects.filter(name='Support Office').exists():
    Department.objects.create(
        name='Support Office',
        root_directory=Directory.objects.create(name='Support Office'),
        is_support=True
    )

# Default Setting
if not Setting.objects.filter(name='Initial').exists():
    Setting.objects.create(
        name='Initial',
        session_time_limit=15,
        upload_filesize_limit=25,
        is_active=True,
        is_default=True
    )

# Default Document Types
types = ['Others', ]
for type in types:
    if not Type.objects.filter(name=type).exists():
        Type.objects.create(name=type)
