from django.urls import path

from . import views

app_name = "chart"

urlpatterns = [
    path("", views.zfactor_chart, name="zfactor_chart"),
    path("data/", views.zfactor_data_list, name="zfactor_data_list"),
]
