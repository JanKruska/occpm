from django.shortcuts import render
from django.http import HttpResponse
from django.views import View


# def index(request):
#     return render(request, "index/base.html")


class ImportView(View):
    def get(self, request):
        return render(request, "index/base.html")
