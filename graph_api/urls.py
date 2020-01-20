from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'graph_api'
urlpatterns = [
    # path('papers/', views.PaperList.as_view()),
    path('paper/<int:pk>/', views.PaperOne.as_view()),
    path('paper/<int:pk>/related', views.PaperRelated.as_view()),
    path('author/<int:pk>/', views.AuthorWithPapers.as_view()),
    path('field/<int:pk>/', views.FieldWithPapers.as_view()),
    path('sigma/paper/related/<int:pk>/', views.SigmaPaperRelated.as_view()),
    path('sigma/nodes', views.GetNodesData.as_view()),
    path('sigma/node', views.GetNodeData.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
