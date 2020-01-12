from django.urls import path

from . import views

app_name = 'graph_viz'
urlpatterns = [
    path('', views.index, name='index'),
    path('vue/', views.vue, name='vue'),
    path('buefy/', views.buefy, name='vue'),
    path('vuetify/', views.vuetify, name='vue'),
]