#%%
from pm4pymdl.objects.ocel.importer import importer as ocel_importer
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)
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
def filter_object(exp, filter):
    for object, values in filter.items():
        exp = exp[exp[object].isin(values)]
    return exp


filter = {"customers": ["Marco Pegoraro"]}
exp = succint_mdl_to_exploded_mdl.apply(df)
filtered_exp = filter_object(exp, filter)
filtered_df = exploded_mdl_to_succint_mdl.apply(filtered_exp)
histo_boxplot(filtered_df, "event_price")
# %%
filter = {"event_price": lambda x: x < 1000}


def filter_numerical(df, filter):
    for object, eval in filter.items():
        df = df[eval(df[object])]
    return df


filtered2 = filter_numerical(df, filter)
histogram(filtered2, "event_activity")
# %%
object_list = ["items", "orders", "customers", "packages"]


def get_object_attributes(obj_df, object_types):
    """Determines which attributes are valid for a list of object_types

    Args:
        obj_df (pd.DataFrame): A pm4py-mdl object dataframe
        object_types (list): The object types to determine attributes for

    Returns:
        dict: dict containing a pairs of object_type and a list of associated attributes
    """
    attributes = {}
    for column in object_types:
        valid = obj_df[obj_df["object_type"] == column].isnull().all()
        attr = [
            column
            for column in obj_df.columns
            if not valid[column] and column != "object_id" and column != "object_type"
        ]
        if attr:
            attributes[column] = attr
    return attributes


attributes = get_object_attributes(obj_df, object_list)
# %%
