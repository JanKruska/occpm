#%%
from pm4pymdl.objects.mdl.importer import importer as mdl_importer
from pm4pymdl.objects.ocel.exporter import exporter as ocel_exporter
from pm4pymdl.objects.ocel.importer import importer as ocel_importer
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

df, obj_df = ocel_importer.apply("running-example.jsonocel")

num_events = len(df)

num_objects = len(obj_df)
# %%
def histogram(df, column):
    fig = px.histogram(df, x=column)
    fig.update_layout(title_text=f"Distribution of column {column}")
    fig.show()


def histo_boxplot(df, column):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Histogram(x=df[column]), row=1, col=1)
    fig.add_trace(go.Box(x=df[column]), row=2, col=1)
    fig.update_layout(title_text=f"Histogram and boxplot of column {column}")
    fig.show()


# %%
def column_is_type(df, column, type):
    idx = df[column].first_valid_index()
    if idx == None:
        return False
    else:
        return isinstance(df[column].loc[idx], type)


def get_column_types(df):
    valid_columns = [
        column
        for column in df.columns
        if column != "event_id" and not df.isnull().all()[column]
    ]
    numerical = df.select_dtypes("number")

    object = [column for column in valid_columns if column_is_type(df, column, list)]

    categorical = [
        column
        for column in valid_columns
        if column not in numerical and column not in object
    ]
    return numerical, categorical, object


numerical, categorical, object = get_column_types(df)

for column in numerical:
    histo_boxplot(df, column)

for column in categorical:
    histogram(df, column)

histogram(obj_df, "object_type")

# %%
