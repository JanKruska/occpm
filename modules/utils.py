import json
import numpy as np
import pandas as pd
from pm4pymdl.objects.ocel.exporter.exporter import json_serial, get_python_obj
from pm4pymdl.algo.mvp.utils import (
    succint_mdl_to_exploded_mdl,
    exploded_mdl_to_succint_mdl,
)
from pm4pymdl.objects.ocel.importer import importer as ocel_importer

from apps.index import models

"""
Helper modules containing various useful utility functions.
"""
ESSENTIAL_LOG_ATTRIBUTES = (
    "event_id",
    "object_id",
    "object_type",
    "event_timestamp",
    "event_activity",
)


def first_valid_entry(series):
    idx = series.first_valid_index()
    if idx == None:
        return None
    else:
        return series.loc[idx]


def series_is_type(series, type):
    """Checks whether the given column is of the provided python type

    Args:
        series (pd.Series):
        type: A python type

    Returns:
        bool
    """
    idx = series.first_valid_index()
    if idx == None:
        return False
    else:
        return isinstance(series.loc[idx], type)


def get_column_types(df):
    """Given a dataframe of an OCEL log, separates columns into numerical, categorical and object type columns

    Args:
        df: A df as it is prodeuced by pm4pymdl

    Returns:
        list,list,list: lists of column identifiers of numerical,categorical and object columns
    """
    valid_columns = [
        column
        for column in df.columns
        if column != "event_id" and not df.isnull().all()[column]
    ]
    numerical = df.select_dtypes("number").columns.to_list()

    object = [column for column in valid_columns if series_is_type(df[column], list)]

    categorical = [
        column
        for column in valid_columns
        if column not in numerical
        and column not in object
        and column not in ESSENTIAL_LOG_ATTRIBUTES
    ]
    return numerical, categorical, object


def filter_object(exp, filter):
    """Filters an event log using categorical columns, can be used on exploded event logs to filter object, since they become categorical through the explosion.
    Note that this filters in CNF, i.e. a logical and on `filter` and logical or on the list contained in each item

    Args:
        exp (pd.DataFrame): (exploded) event log
        filter (dict): a dictionary containing (str,list) pairs where str is a df-column name and list is a list of values

    Returns:
        exp: A filtered dataframe
    """
    for object, values in filter.items():
        exp = exp[exp[object].isin(values)]
    return exp


def filter_numerical(df, filter):
    """Filters an event log on numerical columns

    Args:
        df (pd.DataFrame): The dataframe to be filtered
        filter (dict): dict containing (str,Callable) pairs where str is a df-column name and Callable is function that returns a truth value

    Returns:
        pd.DataFrame: [description]
    """
    for object, eval in filter.items():
        df = df[eval(df[object])]
    return df


def filter(df, obj_df, columns, filters):
    _, _, object_types = get_column_types(df)
    object_attributes = get_object_attributes(obj_df, object_types)

    idx_or = df["event_id"] != df["event_id"]
    # obj_idx_or = obj_df["object_id"] != obj_df["object_id"]
    for filter in filters:
        idx_and = df["event_id"] == df["event_id"]
        for column, value in zip(columns, filter):
            if column in df.columns:
                idx_and = idx_and & (df[column] == value)
            elif column in obj_df.columns:
                valid = obj_df[column] == value
                obj_idx = obj_df[valid]["object_id"]
                temp_df = succint_mdl_to_exploded_mdl.apply(df)
                obj_type = [
                    key for key, value in object_attributes.items() if column in value
                ]
                idx_and = idx_and & (
                    df["event_id"].isin(
                        temp_df[temp_df[obj_type[0]].isin(obj_idx)]["event_id"]
                    )
                )
                # obj_idx_or |= valid
        idx_or = idx_or | idx_and
    df = df[idx_or]
    temp_df = succint_mdl_to_exploded_mdl.apply(df)
    valid_objects = temp_df[
        [type for type in object_types if type in temp_df.columns]
    ].values.ravel()
    valid_objects = valid_objects[~pd.isnull(valid_objects)]
    obj_df = obj_df[obj_df["object_id"].isin(valid_objects)]
    return df, obj_df  # ,obj_df[obj_idx_or]


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


def apply_json(df, obj_df=None, parameters=None):
    """Should not be here, string printing is just missing form pm4pymdl

    Args:
        df ([type]): [description]
        file_path ([type]): [description]
        obj_df ([type], optional): [description]. Defaults to None.
        parameters ([type], optional): [description]. Defaults to None.
    """
    ret = get_python_obj(df, obj_df=obj_df, parameters=parameters)
    return json.dumps(ret, default=json_serial, indent=2)


def serialize_sets(set_obj):
    ## Raises error that object of type set is not json serializable:
    ## soln:
    # json_str = json.dumps(set([1,2,3]), default=serialize_sets)
    # print(json_str)

    if isinstance(set_obj, set):
        return list(set_obj)
    return set_obj


def get_event_log(request):
    if request.method == "GET":
        id = request.GET.get("id")
    elif request.method == "POST":
        id = request.POST.get("id")
    event_log = models.EventLog.objects.get(id=id)
    df, obj_df = ocel_importer.apply(event_log.file.path)
    return event_log, df, obj_df
