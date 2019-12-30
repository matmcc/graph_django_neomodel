from neomodel import DoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Paper, Author, FieldOfStudy
from .serializers import PaperSerializer, AuthorSerializer, FieldOfStudySerializer, AuthorWithPapersSerializer, \
    FieldOfStudyWithPapersSerializer


class PaperList(mixins.ListModelMixin, generics.GenericAPIView):
    """
    List all papers
    """
    queryset = Paper.nodes.all()
    serializer_class = PaperSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PaperOne(APIView):
    """
    Return one paper
    """
    def get_object(self, pk):
        try:
            return Paper.nodes.get(Id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        paper = self.get_object(pk)
        serializer = PaperSerializer(paper)
        return Response(serializer.data)


class PaperRelated(APIView):
    """
    Return papers referenced or cited by the initial paper
    """
    def get_object(self, pk):
        try:
            return Paper.nodes.get(Id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        paper = self.get_object(pk)
        related_papers = paper.references.all() + paper.cited_by.all()
        serializer = PaperSerializer(related_papers, many=True)
        return Response(serializer.data)


class AuthorWithPapers(APIView):
    """
    Return author with list of papers
    """
    def get_object(self, pk):
        try:
            return Author.nodes.get(Id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        author = self.get_object(pk)
        serializer = AuthorWithPapersSerializer(author)
        return Response(serializer.data)


class FieldWithPapers(APIView):
    """
    Return author with list of papers
    """
    def get_object(self, pk):
        try:
            return FieldOfStudy.nodes.get(Id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        field = self.get_object(pk)
        serializer = FieldOfStudyWithPapersSerializer(field)
        return Response(serializer.data)
