import os
import shutil
import tempfile
from os import name
from re import template

from celery_progress.backend import ProgressRecorder
from dj_celery_progress_sample import celery_app
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.utils import timezone
from openpyxl import Workbook, load_workbook

from .base import BaseTask


class ExportUserIntoExcelTask(BaseTask):
    name = "ExportUserIntoExcelTask"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queryset = User.objects.all()

    def copy_and_get_copied_path(self):
        template_path = os.path.join(settings.BASE_DIR, "static/docs/users-template.xlsx")
        destination_path = "%s/%s-exported-users.xlsx" % (tempfile.gettempdir(), int(timezone.now().timestamp()))
        shutil.copy(template_path, destination_path)
        return destination_path

    def create_row(self, instance: User):
        return (
            instance.username,
            instance.first_name,
            instance.last_name,
            instance.is_active,
            instance.is_staff,
            instance.is_superuser
        )

    def create_workbook(self, workbook: Workbook):
        progress_recorder = ProgressRecorder(self)
        total_record = self.queryset.count()
        sheet = workbook.active
        for index, instance in enumerate(self.queryset):
            print("Appending %s into excel" % instance.username)
            sheet.append(self.create_row(instance))
            progress_recorder.set_progress(index + 1, total=total_record, description="Inserting record into row")
        return workbook

    def run(self, *args, **kwargs):
        destination_path = self.copy_and_get_copied_path()
        workbook = load_workbook(destination_path)
        workbook = self.create_workbook(workbook)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export user",
            "data": {
                "outfile": destination_path
            }
        }


@celery_app.task(bind=True, base=ExportUserIntoExcelTask)
def export_user_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
