import json

from django.shortcuts import render
from django.core.files.base import ContentFile
from django.views import View

from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import filter_act_attr_val,filter_act_ot
from pm4pymdl.algo.mvp.utils import succint_mdl_to_exploded_mdl

from apps.index import models
import modules.utils as utils

EVENT_LOG_URL = "media/running-example.jsonocel"


class VisualizeView(View):
    def post(self, request):
        row = request.POST.get("row")
        column = request.POST.get("column")
        filters = []
        for key in request.POST.keys():
            if request.POST.get(key) == "on":
                filters.append([attr.strip("'") for attr in key.split("_")])
        df, obj_df = ocel_importer.apply(EVENT_LOG_URL)
        numerical, categorical, object_types = utils.get_column_types(df)
        object_attributes = utils.get_object_attributes(obj_df,object_types)
        
        for filter in filters:
            if row in df.columns:
                id1 = df[row]==filter[0]
            elif row in obj_df.columns:
                obj_idx = obj_df[obj_df[row] == filter[0]]["object_id"]
                temp_df = succint_mdl_to_exploded_mdl.apply(df)
                obj_type = [key for key,value in object_attributes.items() if row in value]
                id1 = df["event_id"].isin(temp_df[temp_df[obj_type[0]].isin(obj_idx)]["event_id"])
                
            if column in df.columns:
                id2 = df[column]==filter[1]
            elif column in obj_df.columns:
                obj_idx = obj_df[obj_df[column] == filter[1]]["object_id"]
                temp_df = succint_mdl_to_exploded_mdl.apply(df)
                obj_type = [key for key,value in object_attributes.items() if column in value]
                id2 = df["event_id"].isin(temp_df[temp_df[obj_type[0]].isin(obj_idx)]["event_id"])
                
            filtered_log = df[id1 & id2]
                
        # breakpoint()

        context = {
            "num_events": len(df),
            "num_events_filtered": len(filtered_log),
            "filters": filters,
        }
        return render(request, "vis/vis.html", context=context)
