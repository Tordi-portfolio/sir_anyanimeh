from django.urls import path

from .views import home
from .views import theory

urlpatterns = [
    path(
        "",
        home,
        name="home",
    ),
    path(
        "theory/",
        theory,
        name="theory",
    ),
]