import random

from neomodel import DoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from decorators import timing
from .models import Paper, Author, FieldOfStudy
from .papers_to_cypher import update_papers, get_paper_via_interpret
from .serializers import (PaperSerializer, AuthorSerializer, FieldOfStudySerializer, AuthorWithPapersSerializer,
                          FieldOfStudyWithPapersSerializer, SigmaPaperSerializer)
from .utils import count_nodes, fetch_nodes, fetch_node_details, get_related_edges_unfiltered, fetch_co_citations, \
    get_related_edges_filtered, get_related_edges_two_layers
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
def flush_session(request):
    request.session.flush()
    return HttpResponse("<h3>Session Data cleared</h3>")

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
def get_session_key_for_nodes_sent_to_viz(request, key):
    try:
        ret = request.session[key]
    except KeyError:
        request.session[key] = set()
        ret = request.session[key]
    return ret


@timing
def get_node_coords(nodes):
    for n in nodes:
        try:
            x_coord = node_layout.coord_year(n.get('year', 0))
            n['x'] = x_coord
        except TypeError as e:
            print(e)  # print(f'Error: {x_coord}, {type(x_coord)}')
            n['x'] = 0
        y_coord = node_layout.coord_rank(n.get('rank', 0))
        # y_coord = node_layout.coord_citation(n.get('cc', 0))
        n['y'] = y_coord
    return nodes


@timing
def get_edges(node_id, session_key, method="unfiltered", weight="Rank"):
    edges = []
    if method == "filtered":
        all_edges = get_related_edges_filtered(node_id, weight)
    elif method == "unfiltered":
        all_edges = get_related_edges_unfiltered(node_id, weight)
    elif method == "two_layers":
        all_edges = get_related_edges_two_layers(node_id, weight)
        print(len(all_edges))
    else:
        raise NotImplementedError
    for e in all_edges:
        if e[1] in session_key and e[2] in session_key:
            edges.append({
                'id': e[0],
                's': e[1],
                't': e[2],
                'w': e[3]})
    print(len(edges))
    return edges


class SigmaPaperRelated(APIView):
    """Return json object for sigma of papers referenced or cited by the initial paper"""
    renderer_classes = [JSONRenderer]   # return json by default (i.e. if suffix not included)

    def get_object(self, pk):
        try:
            return Paper.nodes.get(PaperId=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        SENT_TO_VIZ = get_session_key_for_nodes_sent_to_viz(request, 'node_ids_sent_to_viz')
        paper = self.get_object(pk)
        SENT_TO_VIZ.add(paper.PaperId)

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

        for n in nodes:
            SENT_TO_VIZ.add(n['id'])

        nodes = get_node_coords(nodes)
        edges = get_edges(paper.PaperId, SENT_TO_VIZ)

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


class GetPaperFromMag(APIView):
    """Return result from MAG via interpret, then evaluate"""
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        SENT_TO_VIZ = get_session_key_for_nodes_sent_to_viz(request, 'node_ids_sent_to_viz')
        query = request.GET.get("query", None)
        if not query:
            raise Http404("Request must include a search query")

        paperIds = get_paper_via_interpret(query)
        if not paperIds:
            return Response()

        papers = [Paper.nodes.get(Id=pId) for pId in paperIds]
        serializer = SigmaPaperSerializer(papers, many=True)
        nodes = serializer.data

        for n in nodes:
            SENT_TO_VIZ.add(n['id'])

        nodes = get_node_coords(nodes)
        # edges = get_edges(paper.PaperId, SENT_TO_VIZ)

        json_for_sigma = {
            'nodes': nodes,
            'edges': []
        }
        return Response(json_for_sigma)


class SigmaPaperCoCited(APIView):
    renderer_classes = [JSONRenderer]  # return json by default (i.e. if suffix not included)

    def get_object(self, pk):
        try:
            return Paper.nodes.get(PaperId=pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        SENT_TO_VIZ = get_session_key_for_nodes_sent_to_viz(request, 'node_ids_sent_to_viz')
        paper = self.get_object(pk)
        # print(paper)
        SENT_TO_VIZ.add(paper.PaperId)

        references = paper.references.all()
        cocite_req = {
            'node_id': pk,
            'count': 50
        }
        cocites = fetch_co_citations(cocite_req)
        related_papers = references + cocites
        paperIds = [p.PaperId for p in related_papers]

        to_update = [p.PaperId for p in related_papers if not p.UpdatedAt]
        if len(to_update) > 0:
            update_papers(to_update)

        related_papers = [Paper.nodes.get(PaperId=Id) for Id in paperIds]

        serializer = SigmaPaperSerializer(related_papers, many=True)
        nodes = serializer.data

        for n in nodes:
            SENT_TO_VIZ.add(n['id'])

        nodes = get_node_coords(nodes)
        edges = get_edges(paper.PaperId, SENT_TO_VIZ, method="two_layers")

        print(request.session)
        json_for_sigma = {
            'nodes': nodes,
            'edges': edges
        }
        return Response(json_for_sigma)
