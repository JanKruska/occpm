from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px

import modules.plots as plots

class ImportView(View):
    def get(self, request):
        return render(request, "index/main.html")

class PlotsView(View):
    def get(self, request):
        if "btn_iris" in request.GET:
            df = px.data.iris()
            plot_div = plot(plots.histogram(df,"sepal_length"),
                    output_type='div',include_plotlyjs=False, link_text="")
            return render(request, "index/plots.html", context={'plot_div': plot_div})
        else:
            df = px.data.tips()
            plot_div = plot(plots.histogram(df,"total_bill"),
                    output_type='div',include_plotlyjs=False, link_text="")
            return render(request, "index/plots.html", context={'plot_div': plot_div})

    # def post(self, request):
    #     if "btn_iris" in request.GET:
    #         df = px.data.iris()
    #         plot_div = plot(plots.histogram(df,"sepal_length"),
    #                 output_type='div',include_plotlyjs=False, link_text="")
    #         return render(request, "index/plots.html", context={'plot_div': plot_div})
    #     else:
    #         df = px.data.tips()
    #         plot_div = plot(plots.histogram(df,"total_bill"),
    #                 output_type='div',include_plotlyjs=False, link_text="")
    #         return render(request, "index/plots.html", context={'plot_div': plot_div})