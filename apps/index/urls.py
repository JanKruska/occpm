from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("tips", views.PlotsView.as_view(), name="tips"),
    path("iris", views.PlotsView.as_view(), name="iris"),
   # path("upload", views.uplaodfile.as_view(), name="upload")

]
