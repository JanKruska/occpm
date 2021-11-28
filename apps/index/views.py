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
from apps.vis.views import LogVisualizationView

import modules.plots as plots
from . import models
import modules.utils as utils

# EVENT_LOG_URL = "media/running-example.jsonocel"


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

class SelectFilterView(LogVisualizationView):
    def get(self,request):
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
                "event_attributes": self.get_event_example_value(df,event_attributes),
                "object_attributes": self.get_object_example_value(obj_df,object_attributes).items(),
                "num_events": len(df),
                "num_objects": len(obj_df),
                "event_log": event_log,
            },
        )

class PlotsView(View):
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
    def save_filtered_log(self,df,obj_df,column_filter,parent,request):
        filtered_log = models.FilteredLog.objects.create(parent=parent)
        filtered_log.name = request.POST.get("name")

        # code to set cookies and obtain info on which checkboxes are checked. Gives list of values of the checkboxes.
        # reference: https://stackoverflow.com/questions/29246625/django-save-checked-checkboxes-on-reload
        # https://stackoverflow.com/questions/52687188/how-to-access-the-checkbox-data-in-django-form
        # checked = [request.POST.get('object_type') for object_type in object_types]
        filtered_log.filter = json.dumps(column_filter, default=utils.serialize_sets)
        filtered_log.file.save(
            filtered_log.name + ".jsonocel", ContentFile(utils.apply_json(df, obj_df))
        )
        filtered_log.save()
        return filtered_log
    
    def extract_filter(self,df,request):
        checked = ["event_id","object_id","object_type"]
        for key in df.columns:
            values = request.POST.getlist(key)
            if values:
                checked += values
        checked = set(checked)
        return checked
    
    def post(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        numerical, categorical, object_types = utils.get_column_types(df)
        obj_numerical, obj_categorical, _ = utils.get_column_types(obj_df)

        # code to set cookies and obtain info on which checkboxes are checked. Gives list of values of the checkboxes.
        # reference: https://stackoverflow.com/questions/29246625/django-save-checked-checkboxes-on-reload
        # https://stackoverflow.com/questions/52687188/how-to-access-the-checkbox-data-in-django-form
        
        checked = self.extract_filter(df,request)
        #Filter log
        df = df[[col for col in df.columns if col in checked]]
        obj_df = obj_df[[col for col in obj_df.columns if col in checked]]
        filtered_log = self.save_filtered_log(df,obj_df,checked,event_log,request)
        context = {
            "num_events": len(df),
            "columns": [*categorical, *obj_categorical],
            "list": [*numerical, *categorical],
            "selected_filters": sorted(checked),
            "event_log": filtered_log,
        }
        return render(request, "index/filter.html", context=context)


##########################################
# Code implementation from sample project:
# from upload_eventlog/views.py
##########################################

# def upload_page(request):
#     log_attributes = {}
#     event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
#     n_event_logs_path = os.path.join(settings.MEDIA_ROOT, "none_event_logs")

#     if request.method == 'POST':
#         if request.is_ajax():  # currently is not being used (get commented in html file)
#             filename = request.POST["log_name"]
#             print('filename = ', filename)
#             file_dir = os.path.join(event_logs_path, filename)
#             eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

#             log = xes_importer_factory.apply(file_dir)
#             no_traces = len(log)
#             no_events = sum([len(trace) for trace in log])
#             log_attributes['no_traces'] = no_traces
#             log_attributes['no_events'] = no_events
#             print(log_attributes)
#             json_respone = {'log_attributes': log_attributes, 'eventlog_list': eventlogs}
#             return HttpResponse(json.dumps(json_respone), content_type='application/json')
#             # return render(request, 'upload.html', {'log_attributes': log_attributes, 'eventlog_list':eventlogs})
#         else:
#             if "uploadButton" in request.POST:
#                 if "event_log" not in request.FILES:
#                     return HttpResponseRedirect(request.path_info)

#                 log = request.FILES["event_log"]
#                 fs = FileSystemStorage(event_logs_path)
#                 filename = fs.save(log.name, log)
#                 uploaded_file_url = fs.url(filename)

#                 eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
#                 # eventlogs.append(filename)

#                 file_dir = os.path.join(event_logs_path, filename)

#                 # xes_log = xes_importer_factory.apply(file_dir)
#                 # no_traces = len(xes_log)
#                 # no_events = sum([len(trace) for trace in xes_log])
#                 # log_attributes['no_traces'] = no_traces
#                 # log_attributes['no_events'] = no_events

#                 return render(request, 'upload.html', {'eventlog_list': eventlogs})

#             elif "deleteButton" in request.POST:  # for event logs
#                 if "log_list" not in request.POST:
#                     return HttpResponseRedirect(request.path_info)

#                 filename = request.POST["log_list"]
#                 if settings.EVENT_LOG_NAME == filename:
#                     settings.EVENT_LOG_NAME = ":notset:"

#                 eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
#                 n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

#                 eventlogs.remove(filename)
#                 file_dir = os.path.join(event_logs_path, filename)
#                 os.remove(file_dir)
#                 return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})


#             elif "n_deleteButton" in request.POST:  # for none event logs
#                 if "n_log_list" not in request.POST:
#                     return HttpResponseRedirect(request.path_info)

#                 filename = request.POST["n_log_list"]

#                 n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]
#                 eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

#                 n_eventlogs.remove(filename)
#                 file_dir = os.path.join(n_event_logs_path, filename)
#                 os.remove(file_dir)
#                 return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})

#             elif "setButton" in request.POST:
#                 if "log_list" not in request.POST:
#                     return HttpResponseRedirect(request.path_info)

#                 filename = request.POST["log_list"]
#                 settings.EVENT_LOG_NAME = filename

#                 file_dir = os.path.join(event_logs_path, filename)

#                 log = convert_eventfile_to_log(file_dir)

#                 # Apply Filters on log
#                 # filters = {
#                 #     'concept:name': ['Test Repair']
#                 # }
#                 # log = filter_log(log, filters, True)


#                 dfg = log_to_dfg(log, 1, 'Frequency')

#                 g6, temp_file = dfg_to_g6(dfg)
#                 dfg_g6_json = json.dumps(g6)

#                 log_attributes['dfg'] = dfg_g6_json

#                 # Get all the column names and respective values
#                 log_attributes['ColumnNamesValues'] = convert_eventlog_to_json(log)

#                 eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]


#                 #Get all the log statistics
#                 no_cases, no_events, no_variants, total_case_duration, avg_case_duration, median_case_duration = get_Log_Statistics(log)
#                 log_attributes['no_cases'] = no_cases
#                 log_attributes['no_events'] = no_events
#                 log_attributes['no_variants'] = no_variants
#                 log_attributes['total_case_duration'] = total_case_duration
#                 log_attributes['avg_case_duration'] = avg_case_duration
#                 log_attributes['median_case_duration'] = median_case_duration


#                 return render(request, 'upload.html',
#                               {'eventlog_list': eventlogs, 'log_name': filename, 'log_attributes': log_attributes})

#             elif "downloadButton" in request.POST:  # for event logs
#                 if "log_list" not in request.POST:
#                     return HttpResponseRedirect(request.path_info)

#                 filename = request.POST["log_list"]
#                 file_dir = os.path.join(event_logs_path, filename)

#                 try:
#                     wrapper = FileWrapper(open(file_dir, 'rb'))
#                     response = HttpResponse(wrapper, content_type='application/force-download')
#                     response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
#                     return response
#                 except Exception as e:
#                     return None

#             elif "n_downloadButton" in request.POST:  # for none event logs
#                 if "n_log_list" not in request.POST:
#                     return HttpResponseRedirect(request.path_info)

#                 filename = request.POST["n_log_list"]
#                 file_dir = os.path.join(n_event_logs_path, filename)

#                 try:
#                     wrapper = FileWrapper(open(file_dir, 'rb'))
#                     response = HttpResponse(wrapper, content_type='application/force-download')
#                     response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
#                     return response
#                 except Exception as e:
#                     return None

#     else:

#         # file_dir = os.path.join(settings.MEDIA_ROOT, "Privacy_P6uRPEd.xes")
#         # xes_log = xes_importer_factory.apply(file_dir)
#         # no_traces = len(xes_log)
#         # no_events = sum([len(trace) for trace in xes_log])
#         # log_attributes['no_traces'] = no_traces
#         # log_attributes['no_events'] = no_events
#         eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
#         n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

#         return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})

#         # return render(request, 'upload.html')




