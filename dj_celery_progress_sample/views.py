import json
import os
from logging import raiseExceptions

from celery_progress.backend import Progress
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView

from celery.result import AsyncResult

from .forms import ImportFileForm
from .tasks import export_user_task, import_user_task
from .utils import in_memory_file_to_temp


class IndexTemplateView(TemplateView):
    template_name = "index.html"


def export_user_view(request):
    task = export_user_task.delay()
    return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')


def import_user_view(request):
    """
    The column of the excel file should be part of
    [Username, Password, Email, First Name, Last Name]
    """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_user_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


def get_progress_view(request):
    progress = Progress(request.GET.get("task_id"))
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')


def download_file_view(request):
    celery_result = AsyncResult(request.GET.get("task_id"))
    filepath = celery_result.result.get("data", {}).get("outfile")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/ms-excel")
            outfile = os.path.basename(filepath)
            response['Content-Disposition'] = "attachment; filename=%s" % outfile
            return response
    raise Http404
