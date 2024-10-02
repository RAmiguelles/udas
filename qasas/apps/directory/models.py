from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class DirectoryGroup(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=100)
    description = models.TextField(verbose_name='Description', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Directory Group'
        verbose_name_plural = 'Directory Groups'


class Directory(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=100)
    description = models.TextField(verbose_name='Description', blank=True)
    parent = models.ForeignKey('self', related_name="children", null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(to=DirectoryGroup, related_name="members", null=True, blank=True,
                              on_delete=models.CASCADE)
    is_trashed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.id, self.name)

    class Meta:
        verbose_name = 'Directory'
        verbose_name_plural = 'Directories'


class LinkedDirectory(models.Model):
    directory = models.ForeignKey(Directory, null=True, blank=True, on_delete=models.CASCADE)
    parent = models.ForeignKey(Directory, related_name="links", null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} {}".format(self.id, self.parent.name, self.directory.name)

    class Meta:
        verbose_name = 'LinkedDirectory'
        verbose_name_plural = 'LinkedDirectories'


# class Subdirectory(models.Model):
#     # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     parent = models.ForeignKey(to=Directory, related_name="subdrp", on_delete=models.CASCADE, null=True)
#     child = models.ForeignKey(to=Directory, related_name="subdrc", on_delete=models.CASCADE, null=True)
#     is_direct = models.BooleanField(default=False)
#
#     class Meta:
#         verbose_name = 'Subdirectory'
#         verbose_name_plural = 'Subdirectories'


class Moderator(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='moderators', on_delete=models.PROTECT)
    directory = models.ForeignKey(to=Directory, related_name="moderators", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Accreditor(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='accreditors', on_delete=models.PROTECT)
    directory = models.ForeignKey(to=Directory, related_name="accreditors", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='directory_logs', on_delete=models.PROTECT)
    directory = models.ForeignKey(to=Directory, related_name="logs", on_delete=models.SET_NULL, null=True)
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

