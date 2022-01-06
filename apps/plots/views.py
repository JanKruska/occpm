import os
import tempfile

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
from pm4pymdl.visualization.mvp.gen_framework3 import visualizer as dfg_visualizer
from pm4pymdl.algo.mvp.get_logs_and_replay import algorithm as petri_disc_factory
from pm4pymdl.visualization.mvp.gen_framework import visualizer as mdfg_vis_factory
from pm4pymdl.visualization.petrinet import visualizer as pn_vis_factory


import modules.plots as plots
from apps.index import models
import modules.utils as utils


class HistogramView(View):
    """View used to render the Histograms displayed on the webpages of the application. Allows for plots
    of different object and event type attributes from the log that it extracts from the chosen log file 
    stored in the database. 

    Args:
        View ([type]): [description]
    """
    def get(self, request, column=None):
        event_log, df, obj_df = utils.get_event_log(request)
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
        else:
            raise Http404("No such column in event log")

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
    """Helps construct and display the directly-follows graphs for the discovered process model from the log. 
    Also has options for frequency adjustments (minimum edge and activity frequency). 

    Args:
        View ([type]): [description]
    """
    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        name = request.GET.get("name", "get")
        model = discovery.apply(df, parameters={"epsilon": 0, "noise_threshold": 0})

        activties = list(model.dictio["activities"].keys())
        activties = sorted(
            activties,
            key=lambda x: model.dictio["activities"][x]["events"],
            reverse=True,
        )
        num_activities = max(
            0,
            min(
                round(int(request.GET.get("act_freq", 100)) * len(activties) / 100),
                len(activties) - 1,
            ),
        )

        edges = {}
        for type, type_edges in model.dictio["types_view"].items():
            for key, value in type_edges["edges"].items():
                edges[(type, key)] = value
        edge_keys_sorted = sorted(
            list(edges.keys()), key=lambda x: edges[x]["events"], reverse=True
        )
        num_edges = max(
            0,
            min(
                round(
                    int(request.GET.get("edge_freq", 100)) * len(edge_keys_sorted) / 100
                ),
                len(edge_keys_sorted) - 1,
            ),
        )

        gviz = dfg_visualizer.apply(
            model,
            measure=request.GET.get("measure", "frequency"),
            parameters={
                "min_act_freq": model.dictio["activities"][
                    activties[int(num_activities)]
                ]["events"],
                "min_edge_freq": edges[edge_keys_sorted[num_edges]]["events"],
            },
        )

        dfg_visualizer.save(gviz, os.path.join(settings.MEDIA_ROOT, name))
        return render(
            request,
            "plots/image.html",
            context={"image": settings.MEDIA_URL + name},
        )


class PetriNetView(View):
    """Used to create and display petri nets from the discovered process model. Contains adjustable parameters 
    (minimum node and edge frequency)

    Args:
        View ([type]): [description]
    """
    def get(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        name = request.GET.get("name", "get")
        
        df = succint_mdl_to_exploded_mdl.apply(df)
        activ = dict(df.groupby("event_id").first()["event_activity"].value_counts())
        activ_sorted = sorted(activ.keys(),key=lambda x:activ[x],reverse=True)
        num_activities = max(
            0,
            min(
                round(int(request.GET.get("act_freq", 100)) * len(activ) / 100),
                len(activ) - 1,
            ),
        )

        # num_edges = max(
        #     0,
        #     min(
        #         round(
        #             int(request.GET.get("edge_freq", 100)) * len(edge_keys_sorted) / 100
        #         ),
        #         len(edge_keys_sorted) - 1,
        #     ),
        # )
        model = petri_disc_factory.apply(
            df,
            parameters={
                "min_node_freq": activ[activ_sorted[num_activities]],
                "min_edge_freq": int(request.GET.get("edge_freq", 100)),
            },
        )
        gviz = pn_vis_factory.apply(model, parameters={"format": "svg"})
        mdfg_vis_factory.save(gviz, os.path.join(settings.MEDIA_ROOT, name))
        return render(
            request,
            "plots/image.html",
            context={"image": settings.MEDIA_URL + name},
        )
