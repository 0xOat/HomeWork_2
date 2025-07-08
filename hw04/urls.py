from django.urls import path

from . import views

urlpatterns = [
    path("", views.laion_list, name="hw04_home"),
]