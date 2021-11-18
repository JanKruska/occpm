"""occpm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.index.views import FilterView, PlotsView, uploadfile

from django.conf import settings
from django.conf.urls.static import static
from apps.index import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include("apps.index.urls")),
    path("filter", FilterView.as_view(), name="filter"),
    path("filtering", views.select_filter, name="filtering"),
    path("plots/", include("apps.index.urls")),
    path("table/", include("apps.dataframe_table.urls")),
    path("", views.uploadfile, name="upload"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
