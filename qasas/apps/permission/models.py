from django.contrib.auth.models import User
from django.db import models

from ..directory.models import Directory
from ..document.models import DocumentDirectory


# Create your models here.
class Permission(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DirectoryPermission(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    directory = models.ForeignKey(to=Directory, related_name='permissions', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='directory_permissions', on_delete=models.CASCADE)
    permission = models.ForeignKey(to=Permission, related_name='directory_permissions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentDirectoryPermission(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    documentdirectory = models.ForeignKey(to=DocumentDirectory, related_name='permissions', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='document_permissions', on_delete=models.CASCADE)
    permission = models.ForeignKey(to=Permission, related_name='document_ermissions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='permission_logs', on_delete=models.PROTECT)
    action = models.CharField(max_length=100, default=None)
    details = models.TextField(blank=True, null=True)
    ip_address = models.CharField(verbose_name='IP Address', max_length=20, null=True)
    country = models.CharField(verbose_name='Country', max_length=50, null=True)
    city = models.CharField(verbose_name='City', max_length=50, null=True)
    latitude = models.CharField(verbose_name='Latitude', max_length=20, null=True)
    longitude = models.CharField(verbose_name='Longitude', max_length=20, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} | {}".format(self.user.first_name, self.user.last_name, self.action)
