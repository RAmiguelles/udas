from django.contrib.auth.models import User
from django.db import models

from ..directory.models import Directory
from ..document.models import Document


class SharedDirectory(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    source_user = models.ForeignKey(to=User, related_name="shared_directory_source", on_delete=models.CASCADE)
    target_user = models.ForeignKey(to=User, related_name="shared_directory_target", on_delete=models.CASCADE)
    directory = models.ForeignKey(to=Directory, related_name="shared", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.source_user, self.target_user, self.directory)

    class Meta:
        verbose_name = 'Shared Directory'
        verbose_name_plural = 'Shared Directories'


class SharedDocument(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    source_user = models.ForeignKey(to=User, related_name="shared_document_source", on_delete=models.CASCADE)
    target_user = models.ForeignKey(to=User, related_name="shared_document_target", on_delete=models.CASCADE)
    document = models.ForeignKey(to=Document, related_name="shared", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.source_user, self.target_user, self.document)

    class Meta:
        verbose_name = 'Shared Document'
        verbose_name_plural = 'Shared Documents'


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='sharing_logs', on_delete=models.PROTECT)
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
