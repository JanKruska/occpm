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
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)

import modules.utils as utils


def uploadfile(request):
    if request.method == "POST" and request.FILES["myfile"]:
        myfile = request.FILES["myfile"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        settings.EVENT_LOG_URL = uploaded_file_url
        return render(
            request, "index/upload.html", {"uploaded_file_url": uploaded_file_url}
        )
    return render(request, "index/upload.html")

def select_filter(request):
    df, obj_df = ocel_importer.apply(os.path.abspath("media/running-example.jsonocel"))
    attribute_list = df.columns.tolist()
    ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
    numerical, categorical, object_attribute_list = utils.get_column_types(df)
    event_attribute_list = [*numerical,*categorical]
    
    #Extract valid attributes associated with each object type
    object_attributes = utils.get_object_attributes(obj_df,object_attribute_list)
    event_dict = {}
    for attribute in event_attribute_list:
        event_dict[attribute] = utils.first_valid_entry(df[attribute])

    object_attributes_examples = {}
    for key, values in object_attributes.items():
        # object_attributes_examples[key] = [" : ".join(x) for x in zip(values,[str(utils.first_valid_entry(obj_df[value])) for value in values])]
        object_attributes_examples[key] = []
        for value in values:
            object_attributes_examples[key].append((value,utils.first_valid_entry(obj_df[value])))
    print(object_attributes_examples)
    column_width=1/(len(object_attributes)+1)*100
    return render(request, "index/filtering.html", context={'event_attributes':event_dict, 'column_width': column_width, 'object_attributes': object_attributes_examples.items()})


class PlotsView(View):
    def post(self, request, column=None):
        df, obj_df = ocel_importer.apply(
            os.path.abspath("media/running-example.jsonocel")
        )
        numerical, categorical, _ = utils.get_column_types(df)
        if column == None or column not in df.columns:
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
        return render(
            request,
            "index/plots.html",
            context={"plot_div": plot_div, "list": [*numerical, *categorical]},
        )

    def get(self, request, column=None):
        df, obj_df = ocel_importer.apply(
            os.path.abspath("media/running-example.jsonocel")
        )
        numerical, categorical, _ = utils.get_column_types(df)
        if column == None:
            return render(
                request,
                "index/plots.html",
                context={"list": [*numerical, *categorical]},
            )
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

        df, obj_df = ocel_importer.apply(
            os.path.abspath("media/running-example.jsonocel")
        )
        numerical, categorical, _ = utils.get_column_types(df)

        exp = succint_mdl_to_exploded_mdl.apply(df)
        filtered_exp = utils.filter_object(exp, filter)
        filtered_df = exploded_mdl_to_succint_mdl.apply(filtered_exp)
        context = {
            "num_events": len(df),
            "filtered_events": len(filtered_df),
            "list": [*numerical, *categorical],
        }
        return render(request, "index/filter.html", context=context)
