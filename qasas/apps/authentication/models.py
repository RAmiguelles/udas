from django.contrib.auth.models import User
from django.db import models


# class Role(models.Model):
#     name = models.CharField(max_length=100, default=None)
#
#     # user = models.ForeignKey(to=User, related_name='roles', on_delete=models.PROTECT)


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='profile')

    # is_accreditor = models.BooleanField(default=False)

    def __str__(self):
        return "{} {} {}".format(self.user.username, self.user.first_name, self.user.last_name, )


class Log(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(to=User, related_name='auth_logs', on_delete=models.PROTECT)
    action = models.CharField(max_length=100, default=None)
    ip_address = models.CharField(verbose_name='IP Address', max_length=20, null=True)
    country = models.CharField(verbose_name='Country', max_length=50, null=True)
    city = models.CharField(verbose_name='City', max_length=50, null=True)
    latitude = models.CharField(verbose_name='Latitude', max_length=20, null=True)
    longitude = models.CharField(verbose_name='Longitude', max_length=20, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {} | {}".format(self.user.first_name, self.user.last_name, self.action)


# Create your models here.
def get_name(self):
    return '{} {} {}'.format(self.username, self.first_name, self.last_name)


User.add_to_class("__str__", get_name)
