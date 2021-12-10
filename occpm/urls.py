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
from apps.index.views import ComparativeView, FilterView, SelectFilterView, UploadView

from django.conf import settings
from django.conf.urls.static import static
from apps.index import views
from apps.vis.views import VisualizeView

from markdown_view.views import MarkdownView

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include("apps.index.urls")),
    path("filter", FilterView.as_view(), name="filter"),
    path("filtering", SelectFilterView.as_view(), name="filtering"),
    path("plots/", include("apps.plots.urls")),
    path("table/", include("apps.dataframe_table.urls")),
    path("", UploadView.as_view(), name="upload"),
    path("visualize", VisualizeView.as_view(), name="visualize"),
    path("comparative", ComparativeView.as_view(), name="comparative"),
    # path("documentation/", include("apps.documentation.urls"))
    path(
        "documentation/",
        MarkdownView.as_view(file_name="/user-manual/User_Manual.md"),
        name="documentation",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
