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
from pm4pymdl.algo.mvp.utils import succint_mdl_to_exploded_mdl, exploded_mdl_to_succint_mdl

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
    

class PlotsView(View):
    def post(self, request, column=None):
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

    def get(self, request,column=None):
        df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
        numerical, categorical, _ = utils.get_column_types(df)
        if column==None:
            return render(request, "index/plots.html", context={'list':[*numerical, *categorical]})
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
        return render(request, "index/raw.html", context={"object": plot_div}) 

class FilterView(View):

    

    def get(self, request):
        #! TODO: determine filtering from request
        filter = {"customers": ["Marco Pegoraro"]}

        df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
        exp=succint_mdl_to_exploded_mdl.apply(df)
        filtered_exp = utils.filter_object(exp,filter)
        filtered_df = exploded_mdl_to_succint_mdl.apply(filtered_exp)
        return render(request, "index/filter.html", context={"num_events":len(df),"filtered_events":len(filtered_df)})
