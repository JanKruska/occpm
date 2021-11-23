import json

from django.shortcuts import render
from django.core.files.base import ContentFile
from django.views import View

from pm4pymdl.objects.ocel.importer import importer as ocel_importer

from apps.index import models
import modules.utils as utils

EVENT_LOG_URL = "media/running-example.jsonocel"


class VisualizeView(View):
    def post(self, request):
        filters = []
        for key in request.POST.keys():
            if request.POST.get(key) == "on":
                filters.append([attr.strip("'") for attr in key.split("_")])
        breakpoint()
        df, obj_df = ocel_importer.apply(EVENT_LOG_URL)
        numerical, categorical, object_types = utils.get_column_types(df)

        df = df[[col for col in df.columns if col in checked]]
        obj_df = obj_df[[col for col in obj_df.columns if col in checked]]

        context = {
            "num_events": len(df),
            "num_ojects": len(obj_df),
            "filters": filters,
        }
        return render(request, "index/filter.html", context=context)
