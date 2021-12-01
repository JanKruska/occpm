from django.urls import path

from . import views

urlpatterns = [
    path("", views.HistogramView.as_view(), name="index"),
    path("histogram/<str:column>", views.HistogramView.as_view(), name="histogram"),
    path("dfg", views.DFGView.as_view(), name="dfg"),
]
