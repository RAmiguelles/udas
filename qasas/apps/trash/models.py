import uuid

from django.db import models
from django.contrib.auth.models import User
from ..department.models import Department
from ..directory.models import Directory
from ..document.models import DocumentDirectory


# Create your models here.
class DirectoryTrash(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    department = models.ForeignKey(to=Department, related_name="directory_trash", on_delete=models.CASCADE)
    directory = models.ForeignKey(to=Directory, related_name="directory_trash", on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='directory_trash', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.department.name, self.directory.name)


class DocumentTrash(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    department = models.ForeignKey(to=Department, related_name="document_trash", on_delete=models.CASCADE)
    docdir = models.ForeignKey(to=DocumentDirectory, related_name="document_trash", on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='document_trash', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.department.name, self.docdir)
