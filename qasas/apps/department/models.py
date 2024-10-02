from django.contrib.auth.models import User
from django.db import models

from ..directory.models import Directory


# Create your models here.
class Department(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=100)
    root_directory = models.ForeignKey(to=Directory, related_name="department", on_delete=models.PROTECT)
    is_support = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserDepartment(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name="departments", on_delete=models.CASCADE)
    department = models.ForeignKey(to=Department, related_name="users", on_delete=models.CASCADE)
    is_head = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "{} {}".format(self.user, self.department)

    class Meta:
        verbose_name = 'User Department'
        verbose_name_plural = 'User Departments'
        unique_together = ('user', 'department')


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='department_logs', on_delete=models.PROTECT)
    action = models.CharField(max_length=100, default=None)
    department = models.ForeignKey(to=Department, related_name="logs", on_delete=models.SET_NULL, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.CharField(verbose_name='IP Address', max_length=20, null=True)
    country = models.CharField(verbose_name='Country', max_length=50, null=True)
    city = models.CharField(verbose_name='City', max_length=50, null=True)
    latitude = models.CharField(verbose_name='Latitude', max_length=20, null=True)
    longitude = models.CharField(verbose_name='Longitude', max_length=20, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} | {}".format(self.user.first_name, self.user.last_name, self.action)




