from ..department.models import Department, UserDepartment
from ..directory.models import Directory


def get_department(directory_id):
    department = None
    directory = Directory.objects.get(id=directory_id)
    while True:
        try:
            department = Department.objects.get(root_directory=directory.id)
            if department: break
        except:
            directory = directory.parent
    return department


def get_my_departments(user_id,is_active=0):
    departments = []
    for item in UserDepartment.objects.filter(is_active=is_active).all():
        if item.user.id == int(user_id): departments.append(item.department)
    return departments
