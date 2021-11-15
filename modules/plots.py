import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def histogram(df, column):
    fig = px.histogram(df, x=column)
    fig.update_layout(title_text=f"Distribution of column {column}")
    return fig


def histogram_boxplot(df, column):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    fig.add_trace(go.Histogram(x=df[column]), row=1, col=1)
    fig.add_trace(go.Box(x=df[column]), row=2, col=1)
    fig.update_layout(title_text=f"Histogram and boxplot of column {column}")
    return fig
