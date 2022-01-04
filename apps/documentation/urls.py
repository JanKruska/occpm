from django.urls import path

from . import views

urlpatterns = [
    path("", views.PlotsView.as_view(), name="index"),
]
