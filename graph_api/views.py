import random

from neomodel import DoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Paper, Author, FieldOfStudy
from .serializers import (PaperSerializer, AuthorSerializer, FieldOfStudySerializer, AuthorWithPapersSerializer,
                          FieldOfStudyWithPapersSerializer, SigmaPaperSerializer)
from .utils import count_nodes, fetch_nodes, fetch_node_details
from . import year_percentiles


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
            raise Http404()

    def get(self, request, pk, format=None):
        field = self.get_object(pk)
        serializer = FieldOfStudyWithPapersSerializer(field)
        return Response(serializer.data)


# Views for sigma
class SigmaPaperRelated(APIView):
    """
    Return json object for sigma of papers referenced or cited by the initial paper
    """
    # return json by default (i.e. if suffix not included)
    renderer_classes = [JSONRenderer]

    # node_ids_sent = set()

    def get_object(self, pk):
        try:
            return Paper.nodes.get(Id=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            SENT_TO_VIZ = request.session['node_ids_sent_to_viz']
        except KeyError:
            request.session['node_ids_sent_to_viz'] = set()
            SENT_TO_VIZ = request.session['node_ids_sent_to_viz']

        paper = self.get_object(pk)

        references = paper.references.all()
        cited_by = paper.cited_by.all()
        related_papers = references + cited_by

        to_update = []
        for p in related_papers:
            if p.CC != len(p.cited_by) or p.RC != len(p.references):
                to_update.append(p)

        serializer = SigmaPaperSerializer(related_papers, many=True)
        nodes = serializer.data

        # remove duplicates (e.g. if a paper is referenced and cited)
        # nodes = [i for n, i in enumerate(nodes) if i not in nodes[n + 1:]]

        # Add random (x, y) positions - todo: Build function
        for n in nodes:
            SENT_TO_VIZ.add(n['id'])
            try:
                n['x'] = int(year_percentiles.coord_year(n['year']))
            except TypeError as e:
                print(n)    # todo: year=2020 giving type(None) - fix
                n['x'] = 0
            n['y'] = year_percentiles.coord_community(n['community'])

        # build better edges
        SENT_TO_VIZ.add(paper.Id)
        edges = []
        for p in nodes:
            for r in p['references']:
                if r in SENT_TO_VIZ:
                    edges.append({
                        'id': f'e_{p["id"]}_{r}',
                        'source': p["id"],
                        'target': r,
                        'weight': p['prob']})
            for c in p['citations']:
                if c in SENT_TO_VIZ:
                    edges.append({
                        'id': f'e_{c}->{p["id"]}',
                        'source': c,
                        'target': p["id"],
                        'weight': p['prob']})

        # edges = [{
        #     'id': f'e{paper.Id}->{ref.Id}',
        #     'source': paper.Id,
        #     'target': ref.Id
        # } for ref in references]
        # edges += [{
        #     'id': f'e{cit.Id}->{paper.Id}',
        #     'source': cit.Id,
        #     'target': paper.Id
        # } for cit in cited_by]

        json_for_sigma = {
            'nodes': nodes,
            'edges': edges
        }
        return Response(json_for_sigma)


class GetNodesData(APIView):
    """Return data for set of nodes"""
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        fetch_nodes_req = {
            'node_type': request.GET.get('t', 'paper'),
            'node_id': request.GET.get('id', None),
            'query': request.GET.get('q', None),
            'order': request.GET.get('o', None),    # Todo: Needs validation
            'count': int(request.GET.get('c', 10)),
            'page': int(request.GET.get('p', 1)),
        }
        nodes = fetch_nodes(fetch_nodes_req)

        return Response(nodes)


class GetNodeData(APIView):
    """Return data for a single node"""
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        # Todo: try except would not raise 404 - don't understand - so this instead
        node_id = request.GET.get('id', None)
        if not node_id:
            raise Http404('request must include id')

        fetch_node_details_req = {
            'node_type': request.GET.get('t', 'paper'),
            'node_id': node_id,
        }
        node = fetch_node_details(fetch_node_details_req)

        return Response(node)
