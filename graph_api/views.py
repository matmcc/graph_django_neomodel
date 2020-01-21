import random

from neomodel import DoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Paper, Author, FieldOfStudy
from .papers_to_cypher import update_papers
from .serializers import (PaperSerializer, AuthorSerializer, FieldOfStudySerializer, AuthorWithPapersSerializer,
                          FieldOfStudyWithPapersSerializer, SigmaPaperSerializer)
from .utils import count_nodes, fetch_nodes, fetch_node_details, get_related_edges_unfiltered
from . import node_layout


# class PaperList(mixins.ListModelMixin, generics.GenericAPIView):
#     """
#     List all papers
#     """
#     queryset = Paper.nodes.all()
#     serializer_class = PaperSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)


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

    def get_object(self, pk):
        try:
            return Paper.nodes.get(PaperId=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            SENT_TO_VIZ = request.session['node_ids_sent_to_viz']
        except KeyError:
            request.session['node_ids_sent_to_viz'] = set()
            SENT_TO_VIZ = request.session['node_ids_sent_to_viz']
        # print(f'0: {len(SENT_TO_VIZ)}')

        paper = self.get_object(pk)

        references = paper.references.all()
        cited_by = paper.cited_by.all()
        related_papers = references + cited_by

        to_update = [p.PaperId for p in related_papers if not p.UpdatedAt]
        if len(to_update) > 0:
            update_papers(to_update)

            references = paper.references.all()
            cited_by = paper.cited_by.all()
            related_papers = references + cited_by

        serializer = SigmaPaperSerializer(related_papers, many=True)
        nodes = serializer.data

        # Add random (x, y) positions - todo: Build function
        for n in nodes:
            SENT_TO_VIZ.add(n['id'])
            # n['x'] = random.randrange(0, 100)
            try:
                x_coord = node_layout.coord_year(n['year'])
                n['x'] = x_coord
            except TypeError as e:
                print(f'Error: {x_coord}, {type(x_coord)}')    # todo: year=2020 giving type(None) - fix
                n['x'] = 0
            y_coord = node_layout.coord_rank(n['rank'])
            n['y'] = y_coord

        # build better edges
        # print(f'1: {len(SENT_TO_VIZ)}')
        SENT_TO_VIZ.add(paper.PaperId)
        edges = []
        all_edges = get_related_edges_unfiltered(paper.PaperId, weight='Rank')
        for e in all_edges:
            if e[1] in SENT_TO_VIZ and e[2] in SENT_TO_VIZ:
                edges.append({
                    'id': e[0],
                    's': e[1],
                    't': e[2],
                    'w': e[3]})

        # for p in nodes:
        #     for r in p['references']:
        #         if r in SENT_TO_VIZ:
        #             edges.append({
        #                 'id': f'{p["id"]}_{r}',
        #                 's': p["id"],
        #                 't': r,
        #                 'w': p['cc']})
        #     for c in p['citations']:
        #         if c in SENT_TO_VIZ:
        #             edges.append({
        #                 'id': f'{c}_{p["id"]}',
        #                 's': c,
        #                 't': p["id"],
        #                 'w': p['cc']})

        json_for_sigma = {
            'nodes': nodes,
            'edges': edges
        }
        # print(f'2: {len(SENT_TO_VIZ)}')
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
