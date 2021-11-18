from django.urls import path

from . import views

urlpatterns = [
    # path("", views.PlotsView.as_view(), name="index"),
    path("<str:row>/<str:column>/", views.TableView.as_view(), name="histogram"),
]
