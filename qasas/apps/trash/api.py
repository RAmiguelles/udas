from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import DirectoryTrash, DocumentTrash
from ..directory.logger import log_trash_directory, log_restore_directory, log_destroy_directory, \
    log_destroy_all_directory, log_restore_all_directory
from ..directory.models import Directory
from ..directory.utils import get_department_by_dir, get_ancestry
from ..document.logger import log_restore_document, log_destroy_document, log_restore_all_document, \
    log_destroy_all_document


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_office_trash(request, directory_id):
    response_data = {
        "directory": [],
        "document": [],
    }

    department = get_department_by_dir(Directory.objects.get(id=directory_id))

    dir_queryset = DirectoryTrash.objects.filter(department=department)
    doc_queryset = DocumentTrash.objects.filter(department=department)

    if dir_queryset.exists():
        for trash in dir_queryset:
            response_data['directory'].append({
                "id": trash.id,
                "directory": {
                    "id": trash.directory.id,
                    "name": trash.directory.name,
                    "description": trash.directory.description,
                    "group": trash.directory.group.name if trash.directory.group else '',
                    "ancestry": get_ancestry(trash.directory)
                },
                "user": {
                    "username": trash.user.username,
                    "first_name": trash.user.first_name,
                    "last_name": trash.user.last_name,
                },
                "created_at": trash.created_at
            })
    if doc_queryset.exists():
        for trash in doc_queryset:
            response_data['document'].append({
                "id": trash.id,
                "docdir_id": trash.docdir.id,
                "document": {
                    "id": trash.docdir.document.id,
                    "title": trash.docdir.document.title,
                    "description": trash.docdir.document.description,
                    "type": trash.docdir.document.type.name,
                },
                "directory": {
                    "id": trash.docdir.directory.id,
                    "name": trash.docdir.directory.name,
                    "description": trash.docdir.directory.description,
                    "group": trash.docdir.directory.group.name if trash.docdir.directory.group else '',
                    "ancestry": get_ancestry(trash.docdir.directory)
                },
                "is_copy": trash.docdir.is_copy,
                "is_link": trash.docdir.is_link,
                "is_public": trash.docdir.is_public,
                "user": {
                    "username": trash.user.username,
                    "first_name": trash.user.first_name,
                    "last_name": trash.user.last_name,
                },
                "created_at": trash.created_at
            })

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def restore_directory_trash(request, trash_id):
    try:
        trash = DirectoryTrash.objects.get(id=trash_id)
        directory = trash.directory

        directory.is_trashed = False
        log_restore_directory(request, directory)
        directory.save()
        trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def restore_document_trash(request, trash_id):
    try:
        trash = DocumentTrash.objects.get(id=trash_id)
        docdir = trash.docdir

        docdir.is_trashed = False
        log_restore_document(request, docdir)
        docdir.save()
        trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_directory_trash(request, trash_id):
    try:
        trash = DirectoryTrash.objects.get(id=trash_id)
        directory = trash.directory
        log_destroy_directory(request, directory)
        directory.delete()
        trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_document_trash(request, trash_id):
    try:
        trash = DocumentTrash.objects.get(id=trash_id)
        docdir = trash.docdir
        log_destroy_document(request, docdir)
        docdir.delete()
        trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def restore_all_trash(request, directory_id):
    try:
        department = get_department_by_dir(Directory.objects.get(id=directory_id))
        dir_queryset = DirectoryTrash.objects.filter(department=department)
        doc_queryset = DocumentTrash.objects.filter(department=department)

        for trash in dir_queryset:
            directory = trash.directory
            directory.is_trashed = False
            log_restore_all_directory(request, directory)
            directory.save()
            trash.delete()
        for trash in doc_queryset:
            docdir = trash.docdir
            docdir.is_trashed = False
            log_restore_all_document(request, docdir)
            docdir.save()
            trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_all_trash(request, directory_id):
    try:
        department = get_department_by_dir(Directory.objects.get(id=directory_id))
        dir_queryset = DirectoryTrash.objects.filter(department=department)
        doc_queryset = DocumentTrash.objects.filter(department=department)

        for trash in dir_queryset:
            directory = trash.directory
            log_destroy_all_directory(request, directory)
            directory.delete()
            trash.delete()
        for trash in doc_queryset:
            docdir = trash.docdir
            log_destroy_all_document(request, docdir)
            docdir.delete()
            trash.delete()

        return Response({"success": True})
    finally:
        return Response({"success": False})
