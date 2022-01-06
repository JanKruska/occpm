import os
from django.http.response import Http404
import json

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.core.files.base import ContentFile
from wsgiref.util import FileWrapper

from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)
from apps.vis.views import LogVisualizationView

from . import models
import modules.utils as utils


class UploadView(View):
    def render(self, request, context={}):
        event_logs = models.EventLog.objects.exclude(name__exact="")
        context.update({"event_logs": event_logs})
        return render(request, "index/upload.html", context=context)

    def set(self, request):
        event_log, _, _ = utils.get_event_log(request)
        context = {"event_log": event_log}
        return self.render(request, context)

    def delete(self, request):
        models.EventLog.objects.filter(id=request.POST.get("id")).delete()
        return self.render(request)

    def download(self, request):
        event_log, _, _ = utils.get_event_log(request)

        try:
            wrapper = FileWrapper(open(event_log.file.path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                event_log.file.path
            )
            return response
        except Exception as e:
            raise Http404()

    def upload(self, request):
        context = {}
        myfile = request.FILES["myfile"]
        hash, event_log = utils.event_log_by_hash(myfile.read())
        if event_log is None:
            event_log = models.EventLog.objects.create()
            event_log.name = os.path.splitext(myfile.name)[0]
            event_log.file = myfile
            event_log.hash = hash
            event_log.save()

        context.update({"uploaded_file_url": event_log.file.url})
        return self.render(request, context)

    def post(self, request):
        if "uploadButton" in request.POST:
            return self.upload(request)
        elif "deleteButton" in request.POST:
            return self.delete(request)
        elif "setButton" in request.POST:
            return self.set(request)
        elif "downloadButton" in request.POST:
            return self.download(request)

    def get(self, request):
        context = {}
        if request.GET.get("id"):
            event_log, _, _ = utils.get_event_log(request)
            context.update({"event_log": event_log})
        return self.render(request, context)


class SelectFilterView(LogVisualizationView):
    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
        numerical, categorical, object_attribute_list = utils.get_column_types(df)
        event_attributes = [*numerical, *categorical]

        # Extract valid attributes associated with each object type
        object_attributes = utils.get_object_attributes(obj_df, object_attribute_list)

        return render(
            request,
            "index/filtering.html",
            context={
                "column_width": 1 / (len(object_attributes) + 1) * 100,
                "event_attributes": self.get_event_example_value(
                    df, obj_df, event_attributes, object_attribute_list
                ).items(),
                "object_attributes": self.get_object_example_value(
                    obj_df, object_attributes
                ).items(),
                "num_events": len(df),
                "num_objects": len(obj_df),
                "event_log": event_log,
            },
        )


class FilterView(View):
    def save_filtered_log(self, df, obj_df, column_filter, parent, request):
        json_string = utils.apply_json(df, obj_df)
        hash, filtered_log = utils.event_log_by_hash(json_string)
        if filtered_log is None:
            filtered_log = models.FilteredLog.objects.create(unfiltered_log=parent)
            filtered_log.name = request.POST.get("name")
            filtered_log.hash = hash

            # code to set cookies and obtain info on which checkboxes are checked. Gives list of values of the checkboxes.
            # reference: https://stackoverflow.com/questions/29246625/django-save-checked-checkboxes-on-reload
            # https://stackoverflow.com/questions/52687188/how-to-access-the-checkbox-data-in-django-form
            # checked = [request.POST.get('object_type') for object_type in object_types]
            filtered_log.column_filter = json.dumps(
                column_filter, default=utils.serialize_sets
            )
            filtered_log.file.save(
                filtered_log.name + ".jsonocel", ContentFile(json_string)
            )
            filtered_log.save()
        return filtered_log

    def extract_filter(self, df, request):
        _, _, object_types = utils.get_column_types(df)
        checked = list(utils.ESSENTIAL_LOG_ATTRIBUTES)
        for key in df.columns:
            values = request.POST.getlist(key)
            if values:
                checked += values
        checked = set(checked)
        return checked

    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        numerical, categorical, object_types = utils.get_column_types(df)
        obj_numerical, obj_categorical, _ = utils.get_column_types(obj_df)

        if isinstance(event_log, models.FilteredLog):
            checked = json.loads(event_log.column_filter)
        elif isinstance(event_log, models.AttributeFilteredLog):
            checked = json.loads(event_log.column_filtered_log.column_filter)
        else:
            checked = []

        context = {
            "num_events": len(df),
            "num_objects": len(obj_df),
            "columns": ["event_activity", *categorical, *obj_categorical],
            "list": [*numerical, *categorical],
            "selected_filters": sorted(checked),
            "event_log": event_log,
        }
        return render(request, "index/filter.html", context=context)

    def post(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        numerical, categorical, object_types = utils.get_column_types(df)

        # code to set cookies and obtain info on which checkboxes are checked. Gives list of values of the checkboxes.
        # reference: https://stackoverflow.com/questions/29246625/django-save-checked-checkboxes-on-reload
        # https://stackoverflow.com/questions/52687188/how-to-access-the-checkbox-data-in-django-form

        checked = self.extract_filter(df, request)
        # Filter log
        df = df[checked.intersection(df.columns)]
        obj_df = obj_df[checked.intersection(obj_df.columns)]
        obj_df = obj_df[obj_df["object_type"].isin(checked.intersection(object_types))]
        filtered_log = self.save_filtered_log(df, obj_df, checked, event_log, request)
        return redirect(f"/filter?id={filtered_log.id}")


class ComparativeView(View):
    def get(self, request):
        event_log, _, _ = utils.get_event_log(request)
        context = {
            "event_log": event_log,
        }
        return render(request, "index/comparative.html", context=context)


class DownloadView(View):
    def post(self, request, path):
        path = "media/" + path
        try:
            wrapper = FileWrapper(open(path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                path
            )
            return response
        except Exception as e:
            raise Http404()
