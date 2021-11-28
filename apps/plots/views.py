from django.http.response import Http404

from django.shortcuts import render
from django.views import View
from django.conf import settings

import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px


from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)

import modules.plots as plots
from apps.index import models
import modules.utils as utils


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
        numerical, categorical, objects = utils.get_column_types(df)
        obj_numerical, obj_categorical, _ = utils.get_column_types(obj_df)

        if column == None:
            return render(
                request,
                "index/plots.html",
                context={"list": [*numerical, *categorical]},
            )
        if column in numerical or column in obj_numerical:
            plotf = plots.histogram_boxplot
        elif column in categorical or column in obj_categorical or column in objects:
            plotf = plots.histogram

        if column in [*categorical, *numerical]:
            target = df
        elif column in obj_df.columns:
            target = obj_df
        elif column in objects:
            target = succint_mdl_to_exploded_mdl.apply(df)

        plot_div = plot(
            plotf(target, column),
            output_type="div",
            include_plotlyjs=False,
            link_text="",
        )
        return render(request, "plots/raw.html", context={"object": plot_div})
