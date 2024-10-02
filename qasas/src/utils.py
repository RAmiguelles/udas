
from copy import deepcopy
from src.models import CollegeDescription, CollegeDescriptionDetail
from datetime import datetime
from django.http import JsonResponse,HttpResponse

def copy_dir_link_desc(old_id, directory_id):
    CollegeDescriptionObj =  CollegeDescription.objects.filter(directory_id = old_id).filter(is_deleted=0)
    if CollegeDescriptionObj.exists():
        for obj in CollegeDescriptionObj:
            new_obj = deepcopy(obj)
            new_obj.pk = None
            new_obj.directory_id = directory_id
            new_obj.created_at = datetime.now()
            new_obj.updated_at = None
            new_obj.save()
            CollegeDescriptionDetailObj = CollegeDescriptionDetail.objects.filter(college_description_id = obj.id).filter(is_deleted=0)
            if CollegeDescriptionDetailObj.exists():
                for detailObj in CollegeDescriptionDetailObj:
                    new_detailObj = deepcopy(detailObj)
                    new_detailObj.pk = None
                    new_detailObj.college_description_id = new_obj.id
                    new_detailObj.created_at = datetime.now()
                    new_detailObj.updated_at = None
                    new_detailObj.save()
    return