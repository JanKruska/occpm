import os
from re import A
from django.http.response import Http404
from filehash import FileHash
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile

import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px


from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)

import modules.plots as plots
from . import models
import modules.utils as utils

EVENT_LOG_URL = "media/running-example.jsonocel"


def uploadfile(request):
    context = {}
    if request.method == "POST" and request.FILES["myfile"]:
        myfile = request.FILES["myfile"]
        event_log = models.EventLog.objects.create()
        event_log.name = os.path.splitext(myfile.name)[0]
        event_log.file = myfile
        sha512hasher = FileHash("sha512")
        event_log.save()
        event_log.hash = sha512hasher.hash_file(event_log.file.path)
        event_log.save()

        context.update({"uploaded_file_url": event_log.file.url})

    event_logs = models.EventLog.objects.exclude(name__exact="")
    context.update({"event_logs": event_logs})
    return render(request, "index/upload.html", context=context)


#def select_filter(request):
    # event_log = models.EventLog.objects.get(id=request.GET.get("id"))
    # df, obj_df = ocel_importer.apply(event_log.file.path)
    # attribute_list = df.columns.tolist()
    # ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
    # numerical, categorical, object_attribute_list = utils.get_column_types(df)
    # event_attribute_list = [*numerical, *categorical]

    # # Extract valid attributes associated with each object type
    # object_attributes = utils.get_object_attributes(obj_df, object_attribute_list)
    # event_dict = {}
    # for attribute in event_attribute_list:
    #     event_dict[attribute] = utils.first_valid_entry(df[attribute])

    # object_attributes_examples = {}
    # for key, values in object_attributes.items():
    #     object_attributes_examples[key] = []
    #     for value in values:
    #         object_attributes_examples[key].append(
    #             (value, utils.first_valid_entry(obj_df[value]))
    #         )

    # column_width = 1 / (len(object_attributes) + 1) * 100
    # return render(
    #     request,
    #     "index/filtering.html",
    #     context={
    #         "event_attributes": event_dict,
    #         "column_width": column_width,
    #         "object_attributes": object_attributes_examples.items(),
    #         "num_events": len(df),
    #         "num_objects": len(obj_df),
    #         "event_log": event_log,
    #     },
    # )

## trying model based filtering of log
def select_filter(request):
    event_log = models.EventLog.objects.get(id=request.GET.get("id"))
    df, obj_df = ocel_importer.apply(event_log.file.path)
    attribute_list = df.columns.tolist()
    ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
    numerical, categorical, object_attribute_list = utils.get_column_types(df)
    event_attribute_list = [*numerical, *categorical]

    

    # Extract valid attributes associated with each object type
    object_attributes = utils.get_object_attributes(obj_df, object_attribute_list)
    event_dict = {}
    for attribute in event_attribute_list:
        event_dict[attribute] = utils.first_valid_entry(df[attribute])    

    object_attributes_examples = {}
    for key, values in object_attributes.items():
        object_attributes_examples[key] = []
        for value in values:
            object_attributes_examples[key].append(
                (value, utils.first_valid_entry(obj_df[value]))
            )


    column_width = 1 / (len(object_attributes) + 1) * 100
    return render(
        request,
        "index/filtering.html",
        context={
            "event_attributes": event_dict,
            "column_width": column_width,
            "object_attributes": object_attributes_examples.items(),
            "num_events": len(df),
            "num_objects": len(obj_df),
            "event_log": event_log,
        },
    )


class PlotsView(View):
    # def post(self, request, column=None):
    #     df, obj_df = ocel_importer.apply(os.path.abspath(EVENT_LOG_URL))
    #     numerical, categorical, _ = utils.get_column_types(df)
    #     if column == None or column not in df.columns:
    #         return self.get(request)
    #     elif column in numerical:
    #         plot_div = plot(
    #             plots.histogram_boxplot(df, column),
    #             output_type="div",
    #             include_plotlyjs=False,
    #             link_text="",
    #         )
    #     elif column in categorical:
    #         plot_div = plot(
    #             plots.histogram(df, column),
    #             output_type="div",
    #             include_plotlyjs=False,
    #             link_text="",
    #         )
    #     return render(
    #         request,
    #         "index/plots.html",
    #         context={"plot_div": plot_div, "list": [*numerical, *categorical]},
    #     )

    def get(self, request, column=None):
        log_type = request.GET.get("type")
        if log_type == "event_log":
            event_log = models.EventLog.objects.get(id=request.GET.get("id"))
        elif log_type == "event_cube":
            event_log = models.EventLog.objects.get(
                id=request.GET.get("id")
            )  # Todo plotting for cube
        else:
            raise Http404("no such log type supported")
        df, obj_df = ocel_importer.apply(event_log.file.path)
        numerical, categorical, _ = utils.get_column_types(df)
        obj_numerical, obj_categorical, _ = utils.get_column_types(obj_df)

        if column == None:
            return render(
                request,
                "index/plots.html",
                context={"list": [*numerical, *categorical]},
            )
        if column in numerical or column in obj_numerical:
            plotf = plots.histogram_boxplot
        elif column in categorical or column in obj_categorical:
            plotf = plots.histogram

        if column in df.columns:
            target = df
        elif column in obj_df.columns:
            target = obj_df

        plot_div = plot(
            plotf(target, column),
            output_type="div",
            include_plotlyjs=False,
            link_text="",
        )
        return render(request, "index/raw.html", context={"object": plot_div})


#################################################


class FilterView(View):
    def post(self, request):
        event_log = models.EventLog.objects.get(id=request.POST.get("id"))
        df, obj_df = ocel_importer.apply(event_log.file.path)
        # attribute_list = df.columns.tolist()
        numerical, categorical, object_types = utils.get_column_types(df)
        # combined_attribute_list = [*numerical, *categorical, *object_types]

        # code to set cookies and obtain info on which checkboxes are checked. Gives list of values of the checkboxes.
        # reference: https://stackoverflow.com/questions/29246625/django-save-checked-checkboxes-on-reload
        # https://stackoverflow.com/questions/52687188/how-to-access-the-checkbox-data-in-django-form
        # checked = [request.POST.get('object_type') for object_type in object_types]
        checked = []
        for key in df.columns:
            values = request.POST.getlist(key)
            if values:
                checked += values

        checked = set(checked)
        df = df[[col for col in df.columns if col in checked]]
        obj_df = obj_df[[col for col in obj_df.columns if col in checked]]
        filtered_log = models.FilteredLog.objects.create(parent=event_log)
        filtered_log.name = request.POST.get("name")
        filtered_log.filter = json.dumps(checked)
        filtered_log.file.save(event_log.name + ".jsonocel", ContentFile(utils.apply_json(df,obj_df)))
        filtered_log.save()
        context = {
            "num_events": len(df),
            "columns": [*df.columns, *obj_df.columns],
            "list": [*numerical, *categorical],
            "selected_filters": checked,
        }
        return render(request, "index/filter.html", context=context)

    def filter(self, request):
        filter = {"customers": ["Marco Pegoraro"]}
        df, obj_df = ocel_importer.apply(os.path.abspath(EVENT_LOG_URL))
        attribute_list = df.columns.tolist()
        numerical, categorical, object_types = utils.get_column_types(df)
        exp = succint_mdl_to_exploded_mdl.apply(df)
        filtered_exp = utils.filter_object(exp, filter)
        filtered_df = exploded_mdl_to_succint_mdl.apply(filtered_exp)
