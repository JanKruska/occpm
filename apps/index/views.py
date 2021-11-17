import os
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px

import modules.plots as plots

## file upload code
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from pm4pymdl.objects.ocel.importer import importer as ocel_importer

import modules.utils as utils


def uploadfile(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        settings.EVENT_LOG_URL = uploaded_file_url
        return render(request, 'index/upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'index/upload.html')

def select_filter(request):
    df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
    attribute_list = df.columns.tolist()
    ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
    numerical, categorical, object_attribute_list = utils.get_column_types(df)
    event_attribute_list = [*numerical,*categorical]
    
    ## writing code for extracting the object columns sub-attributes 
    #object_types = obj_df[object_type].unique() # extracts all types of objects from the obj df as a list
    object_types = object_attribute_list    #extra step because i'm not sure it's correct. 
    attributes = {}
    for column in object_types:
        valid = obj_df[obj_df["object_type"]==column].isnull().all()    # checks that if column has all null values then it is not considered as a valid attribute
        attr = [column for column in obj_df.columns if not valid[column] and column!="object_id" and column!="object_type"]
        if attr:
            attributes[column] = attr

    return render(request, "index/filtering.html", context={'event_attributes':event_attribute_list, 'object_types': object_attribute_list, 'object_attributes': attributes})


class PlotsView(View):
    def post(self, request, column=None):
        # if "btn_iris" in request.GET:
        df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
        numerical, categorical, _ = utils.get_column_types(df)
        if column==None or column not in df.columns:
            return self.get(request)
        elif column in numerical:
            plot_div = plot(
                plots.histogram_boxplot(df, column),
                output_type="div",
                include_plotlyjs=False,
                link_text="",
            )
        elif column in categorical:
            plot_div = plot(
                plots.histogram(df, column),
                output_type="div",
                include_plotlyjs=False,
                link_text="",
            )
        return render(request, "index/plots.html", context={"plot_div": plot_div, 'list':[*numerical, *categorical]})

    def get(self, request):
        df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
        numerical, categorical, _ = utils.get_column_types(df)
        return render(request, "index/plots.html", context={'list':[*numerical, *categorical]})
        
