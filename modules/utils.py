"""
Helper modules containing various useful utility functions.
"""


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
    numerical = df.select_dtypes("number")

    object = [column for column in valid_columns if series_is_type(df[column], list)]

    categorical = [
        column
        for column in valid_columns
        if column not in numerical and column not in object
    ]
    return numerical, categorical, object
