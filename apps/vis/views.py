import json
import os
from wsgiref.util import FileWrapper
from django.http.response import Http404, HttpResponse

from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.views import View

from apps.index import models
import modules.utils as utils


class LogVisualizationView(View):
    def get_event_example_value(self, df, obj_df, event_attributes, object_attributes):
        event_attribute_examples = {}
        # Get event level attrs
        for attribute in event_attributes:
            event_attribute_examples[attribute] = utils.first_valid_entry(df[attribute])
        # Get objects & examples
        for attribute in object_attributes:
            event_attribute_examples[attribute] = utils.first_valid_entry(
                obj_df[obj_df["object_type"] == attribute]["object_id"]
            )

        return event_attribute_examples

    def get_object_example_value(self, obj_df, object_attributes):
        object_attributes_examples = {}
        for key, values in object_attributes.items():
            object_attributes_examples[key] = []
            for value in values:
                object_attributes_examples[key].append(
                    (value, utils.first_valid_entry(obj_df[value]))
                )
        return object_attributes_examples


class VisualizeView(LogVisualizationView):
    def save_filtered_log(self, filtered_log, obj_df, filters, request):
        json_string = utils.apply_json(filtered_log, obj_df)
        hash, attr_filtered_log = utils.event_log_by_hash(json_string)
        if attr_filtered_log is None:
            parent = models.FilteredLog.objects.get(id=request.POST.get("id"))
            attr_filtered_log = models.AttributeFilteredLog(
                column_filtered_log=parent,
            )
            attr_filtered_log.name = request.POST.get("name")
            attr_filtered_log.hash = hash
            attr_filtered_log.cell_filter = json.dumps(filters)
            attr_filtered_log.file.save(
                attr_filtered_log.name + ".jsonocel",
                ContentFile(json_string),
            )
            attr_filtered_log.save()
        return attr_filtered_log

    def extract_filter(self, request):
        row = request.POST.get("row")
        column = request.POST.get("column")
        filters = []
        for key in request.POST.keys():
            if request.POST.get(key) == "on":
                filters.append([attr.strip("'") for attr in key.split("_")])
        return row, column, filters

    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        # Determine attributes in filtered log
        numerical, categorical, object_attribute_list = utils.get_column_types(df)
        event_attributes = [*numerical, *categorical]
        object_attributes = utils.get_object_attributes(obj_df, object_attribute_list)

        context = {
            "num_events": len(df),
            "event_log": event_log,
            "event_attributes": self.get_event_example_value(
                df, obj_df, event_attributes, object_attribute_list
            ).items(),
            "column_width": 1 / (len(object_attributes) + 1) * 100,
            "object_attributes": self.get_object_example_value(
                obj_df, object_attributes
            ).items(),
        }
        return render(request, "vis/vis.html", context=context)

    def filter(self, request):
        event_log, df, obj_df = utils.get_event_log(request)

        row, column, filters = self.extract_filter(request)
        # Filter log
        filtered_log, obj_filtered = utils.filter(df, obj_df, [row, column], filters)
        attr_filtered_log = self.save_filtered_log(
            filtered_log, obj_filtered, filters, request
        )
        return redirect(f"/visualize?id={attr_filtered_log.id}")

    def download(self, request):
        path = "media/" + request.POST.get("image-name")
        try:
            wrapper = FileWrapper(open(path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                path
            )
            return response
        except Exception as e:
            raise Http404()

    def post(self, request):
        if request.POST.get("download"):
            return self.download(request)
        else:
            return self.filter(request)
