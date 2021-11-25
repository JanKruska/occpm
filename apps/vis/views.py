import json

from django.shortcuts import render
from django.core.files.base import ContentFile
from django.views import View

from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import filter_act_attr_val, filter_act_ot
from pm4pymdl.algo.mvp.utils import succint_mdl_to_exploded_mdl

from apps.index import models
import modules.utils as utils

EVENT_LOG_URL = "media/running-example.jsonocel"


class VisualizeView(View):
    def post(self, request):
        event_log, df, obj_df = utils.get_event_log(request)
        row = request.POST.get("row")
        column = request.POST.get("column")
        filters = []
        for key in request.POST.keys():
            if request.POST.get(key) == "on":
                filters.append([attr.strip("'") for attr in key.split("_")])
        df, obj_df = ocel_importer.apply(EVENT_LOG_URL)

        filtered_log = utils.filter(df, obj_df, [row, column], filters)
        attr_filtered_log = models.AttributeFilteredLog(
            parent=models.FilteredLog.objects.get(id=request.POST.get("id"))
        )
        attr_filtered_log.name = request.POST.get("name")
        attr_filtered_log.filter = json.dumps(filters)
        attr_filtered_log.file.save(
            attr_filtered_log.name + ".jsonocel",
            ContentFile(utils.apply_json(filtered_log, obj_df)),
        )
        attr_filtered_log.save()

        context = {
            "num_events": len(df),
            "num_events_filtered": len(filtered_log),
            "filters": filters,
        }
        return render(request, "vis/vis.html", context=context)
