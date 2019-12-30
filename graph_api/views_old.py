from neomodel import DoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Paper, Author, FieldOfStudy
from .serializers import PaperSerializer, AuthorSerializer, FieldOfStudySerializer


# class PaperList(APIView):
#     """
#     List all papers
#     """
#     def get(self, request, format=None):
#         if request.method == 'GET':
#             papers = Paper.nodes.all()
#             serializer = PaperSerializer(papers, many=True)
#             return Response(serializer.data)
class PaperList(generics.ListAPIView):
    queryset = Paper.nodes.all()
    serializer_class = PaperSerializer

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)


class PaperOne(APIView):
    def get_object(self, pk):
        try:
            return Paper.nodes.get(id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        paper = self.get_object(pk)
        serializer = PaperSerializer(paper)
        return JsonResponse(serializer.data)

# class PaperOne(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Paper.nodes.all()
#     serializer_class = PaperSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)


# class PaperViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint returning view of papers
#     """
#     queryset = Paper.nodes.first_or_none()
#     serializer_class = PaperSerializer
#
#
# class AuthorViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint returning view of papers
#     """
#     queryset = Author.nodes.first_or_none()
#     serializer_class = AuthorSerializer
#
#
# class FieldOfStudyViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint returning view of papers
#     """
#     queryset = FieldOfStudy.nodes.first_or_none()
#     serializer_class = FieldOfStudySerializer
