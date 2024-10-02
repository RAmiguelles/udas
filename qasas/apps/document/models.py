from django.contrib.auth.models import User
from django.db import models

from ..directory.models import Directory


# Create your models here.
class Type(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='documents', on_delete=models.PROTECT)
    title = models.TextField(verbose_name='Title')
    description = models.TextField(verbose_name='Description', blank=True)
    is_public = models.BooleanField(default=False, null=True)
    type = models.ForeignKey(to=Type, related_name='documents', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Attachment(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    document = models.ForeignKey(to=Document, related_name="attachments", on_delete=models.CASCADE)
    attachment = models.FileField(verbose_name='Attachment', upload_to='attachments/', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document.title


class Attribute(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    document = models.ForeignKey(to=Document, related_name="attributes", on_delete=models.CASCADE)
    key = models.CharField(verbose_name='Field', max_length=100)
    value = models.CharField(verbose_name='Value', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.key, self.value)


class Keyword(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    document = models.ForeignKey(to=Document, related_name="keywords", on_delete=models.CASCADE)
    keyword = models.CharField(verbose_name='Keyword', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword


class Comment(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    document = models.ForeignKey(to=Document, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='comments', on_delete=models.PROTECT, null=True)
    description = models.TextField(verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} {}".format(
            self.user.first_name,
            self.user.last_name,
            self.description
        )


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='document_logs', on_delete=models.PROTECT)
    document = models.ForeignKey(to=Document, related_name="logs", on_delete=models.SET_NULL, null=True)
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


###

class DocumentDirectory(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    directory = models.ForeignKey(to=Directory, related_name="docdirs", on_delete=models.CASCADE)
    document = models.ForeignKey(to=Document, related_name="docdirs", on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False, null=True)
    is_copy = models.BooleanField(default=False)
    is_link = models.BooleanField(default=False)
    link = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    is_trashed = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.directory, self.document)

    class Meta:
        verbose_name = 'Document Directory'
        verbose_name_plural = 'Document Directories'

class Actions(models.Model):
    action = models.CharField(max_length=100, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.action)

class GlobalDirectory(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    root_directory = models.ForeignKey(Directory, null=True, blank=True, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "{}".format(self.root_directory,self.document)

    class Meta:
        verbose_name = 'GlobalDirectory'
