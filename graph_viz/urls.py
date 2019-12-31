from django.urls import path

from . import views

app_name = 'graph_viz'
urlpatterns = [
    path('', views.index, name='index'),
]