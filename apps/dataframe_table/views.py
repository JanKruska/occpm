from django.shortcuts import render
from django.views import View
from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
)

from modules import utils

# Create your views here.
class TableView(View):
    """View used to generate the cross-table with values of the selected 'row' and 'column' attribute
    with checkboxes enabled for user selection in the second-level of filtering of the log. 

    Args:
        View ([type]): [description]
    """
    def get(self, request, row=None, column=None):
        """Takes in the HTTP request containing information about the log, with row and column parameters as default=None
        and returns the cross-table of attribute values 

        Args:
            request (Django HttpRequest object): contains al information passed on as the webpage is requested. 
            row ([type], optional): Refers to the row of the . Defaults to None.
            column ([type], optional): . Defaults to None.

        Returns:
            [type]: [description]
        """
        event_log, df, obj_df = utils.get_event_log(request)
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
        context = {
            "column_labels": column_labels,
            "rows": rows.items(),
            "row": row,
            "column": column,
            "event_log": event_log,
        }
        return render(request, "dataframe_table/table.html", context=context)
