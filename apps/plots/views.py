import os

from django.http.response import Http404, HttpResponse
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
from pm4pymdl.algo.mvp.gen_framework3 import discovery
from pm4pymdl.visualization.mvp.gen_framework3 import visualizer as visualizer


import modules.plots as plots
from apps.index import models
import modules.utils as utils


class HistogramView(View):
    def get(self, request, column=None):
        event_log = models.EventLog.objects.get(id=request.GET.get("id"))
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


class DFGView(View):
    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)

        model = discovery.apply(df, parameters={"epsilon": 0, "noise_threshold": 0})
        gviz = visualizer.apply(
            model,
            parameters={
                "min_act_freq": request.GET.get("act_freq", 100),
                "min_edge_freq": request.GET.get("edge_freq", 100),
            },
        )

        visualizer.save(gviz, os.path.join(settings.MEDIA_ROOT, "test.png"))
        return render(
            request,
            "plots/image.html",
            context={"image": settings.MEDIA_URL + "test.png"},
        )


# def dfg_to_g6(dfg):
#     unique_nodes = []
#     # print(dfg)
#     for i in dfg:
#         unique_nodes.extend(i)
#     unique_nodes = list(set(unique_nodes))

#     unique_nodes_dict = {}

#     for index, node in enumerate(unique_nodes):
#         unique_nodes_dict[node] = "node_" + str(index)

#     nodes = [{'id': unique_nodes_dict[i], 'name': i, 'isUnique':False, 'conf': [
#         {
#             'label': 'Name',
#             'value': i
#         }
#     ]} for i in unique_nodes_dict]
#     freqList = [int(dfg[i]) for i in dfg]
#     maxVal = max(freqList) if len(freqList) != 0 else 0
#     minVal = min(freqList) if len(freqList) != 0 else 0

#     edges = [{'source': unique_nodes_dict[i[0]], 'target': unique_nodes_dict[i[1]], 'label': round(dfg[i], 2),
#               "style": {"lineWidth": ((int(dfg[i]) - minVal) / (maxVal - minVal) * (20 - 2) + 2), "endArrow": True}} for
#              i in
#              dfg]
#     data = {
#         "nodes": nodes,
#         "edges": edges,
#     }
