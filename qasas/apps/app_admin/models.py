from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Setting(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default='Template')
    session_time_limit = models.IntegerField(verbose_name='Session Time Limit (minutes)', default=15)
    upload_filesize_limit = models.IntegerField(verbose_name='Upload Filesize Limit (MB)', default=25)
    staging_pass_key = models.CharField(max_length=100, default='USeP-UDAS')
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='admin_logs', on_delete=models.PROTECT)
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
