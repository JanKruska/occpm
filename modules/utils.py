"""
Helper modules containing various useful utility functions.
"""


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
        if column not in numerical and column not in object
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
