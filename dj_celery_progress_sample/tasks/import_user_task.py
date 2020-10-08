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

from ..utils import DataframeUtil
from .base import BaseTask


class ImportUserFromExcelTask(BaseTask):
    name = "ImportUserFromExcelTask"

    def insert_into_row(self, row: dict) -> User:
        u, _ = User.objects.get_or_create(username=row.get("username"))
        u.set_password(row.get("password"))
        u.first_name = row.get("first name")
        u.last_name = row.get("last name")
        u.email = row.get("email")
        u.save()
        return u

    def run(self, filepath, *args, **kwargs):
        progress_recorder = ProgressRecorder(self)
        dataframe = DataframeUtil.get_validated_dataframe(filepath)
        total_record = dataframe.shape[0]
        for index, row in dataframe.iterrows():
            self.insert_into_row(row)
            progress_recorder.set_progress(index + 1, total=total_record, description="Inserting row into table")
            print("Inserting row %s into table" % index)

        return {
            "detail": "Successfully import user"
        }


@celery_app.task(bind=True, base=ImportUserFromExcelTask)
def import_user_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
