from django.shortcuts import render
from django.views import View
import numpy as np
from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
)

from modules import utils

EVENT_LOG_URL = "media/running-example.jsonocel"

# Create your views here.
class TableView(View):
    def get(self, request, row=None, column=None):
        df, obj_df = ocel_importer.apply(EVENT_LOG_URL)
        attribute_list = df.columns.tolist()
        ## returns 3 lists, 1st two are written and need to be merged to get event attributes. 3rd list is for object attributes.
        _, categorical, _ = utils.get_column_types(df)
        _, obj_categorical, _ = utils.get_column_types(obj_df)
        # breakpoint()
        if column in df.columns:
            column_labels = df[column].dropna().unique()
        elif column in obj_df.columns:
            column_labels = obj_df[column].dropna().unique()

        if row in df.columns:
            row_labels = df[row].dropna().unique()
        elif row in obj_df.columns:
            row_labels = obj_df[row].dropna().unique()

        exp = succint_mdl_to_exploded_mdl.apply(df)
        rows = {}
        for row_label in row_labels:
            rows[row_label] = []
            for column_label in column_labels:
                rows[row_label].append(column_label)
                # rows[row_label].append(len(exp[exp[row] == row_label]))

        return render(
            request,
            "dataframe_table/table.html",
            {"column_labels": column_labels, "rows": rows.items()},
        )
