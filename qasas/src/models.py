from django.db import models
from apps.directory.models import Directory
from django.utils import timezone
# Create your models here.

class CollegeDescription(models.Model):
    directory = models.ForeignKey(to=Directory, related_name='college_descriptions', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.title

class CollegeDescriptionDetail(models.Model):
    college_description = models.ForeignKey(to=CollegeDescription, related_name='college_description_details', on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.description