from neomodel import db

from .models import Author, FieldOfStudy, Paper
from .serializers import AuthorSerializer, FieldOfStudySerializer, PaperSerializer

MODELS = {
    'author': Author,
    'field': FieldOfStudy,
    'paper': Paper
}

SERIALIZERS = {
    'author': AuthorSerializer,
    'field': FieldOfStudySerializer,
    'paper': PaperSerializer
}

# Todo: fetch_node returns list, others return dict - use wrapper method to return dict (json) with status and count?


def filter_nodes(node_type, node_id=None, query=None, order=None):
    """Filter nodes by request args"""
    node_set = node_type.nodes

    if node_id:
        node_set.filter(Id=node_id)
    if query:
        node_set.filter(name__icontains=query)
    if node_type.__name__ == 'Paper':
        if order:
            # if cc or rc ensure uppercase, greatest value first
            order = '-' + order.upper() if order != 'prob' else '-' + order
        else:
            order = '-prob'
        node_set.order_by(order)

    return node_set


def serialize_nodes(node_type, node_set):
    if not node_set:
        return None
    many = True if hasattr(node_set, '__iter__') else False     # True if iterable
    serializer = SERIALIZERS[node_type](node_set, many=many)

    return serializer.data


def count_nodes(req):
    count = {}
    node_type = req.get('node_type', 'paper')
    node_id = req.get('node_id', None)
    query = req.get('query', None)

    node_set = filter_nodes(MODELS[node_type], node_id, query)
    count['count'] = len(node_set)

    return count


def fetch_nodes(req):
    node_type = req.get('node_type', 'paper')
    node_id = req.get('node_id', None)
    query = req.get('query', None)
    count = req.get('count', 10)
    page = req.get('page', 1)
    order = req.get('order', None)
    start = (page - 1) * count
    end = start + count

    node_set = filter_nodes(MODELS[node_type], node_id, query, order)
    fetched_nodes = node_set[start:end]
    serialized_data = serialize_nodes(node_type, fetched_nodes)

    return serialized_data


def fetch_node_details(req):
    node_type = req.get('node_type', 'paper')
    node_id = req.get('node_id')

    node = filter_nodes(MODELS[node_type], node_id).get_or_none()   # Todo: 404 here? if so, use get() and DoesNotExist
    serialized_data = serialize_nodes(node_type, node)

    return serialized_data


def fetch_papers_by_algo(req, cypher_q):
    """Util function, runs cypher query with node_id and count from request, returns serialized data"""
    node_id = req.get('node_id')    # todo: 404 here?
    count = req.get('count', 10)

    results, meta = db.cypher_query(cypher_q, {'node_id': node_id, 'count': count})
    nodes = [Paper.inflate(row[0]) for row in results]

    serialized_data = serialize_nodes('paper', nodes)

    return serialized_data


def fetch_co_citations(req):
    """Return list of papers with 1 or more shared references, ordered by number shared references"""
    get_co_citations = """
    Match (p:Paper {Id:{node_id}})-[:CITES]->(r:Paper)<-[c:CITES]-(q:Paper) 
    RETURN q, count(c) as rc  
    ORDER BY rc DESC LIMIT {count}
    """
    data = fetch_papers_by_algo(req, get_co_citations)

    return data


def personalised_page_rank(req):
    """Return list of papers in order of personalised page rank"""
    # Could write to nodes, but in this case stream results (since will likely update as more nodes added)
    get_ppr = """
    MATCH (n:Paper {Id:{node_id}})
    CALL algo.pageRank.stream('Paper', 'CITES',
    {direction:'OUTGOING', iterations:20, dampingFactor:0.85, sourceNodes: [n]})
    YIELD nodeId, score
    RETURN algo.asNode(nodeId).name AS page,score
    ORDER BY score DESC
    """
    data = fetch_papers_by_algo(req, get_ppr)

    return data


def personalised_article_rank(req):
    """Return list of papers in order of personalised page rank"""
    # Could write to nodes, but in this case stream results (since will likely update as more nodes added)
    get_par = """
    MATCH (n:Paper {Id:{node_id}})
    CALL algo.articleRank.stream('Paper', 'CITES',
    {direction:'OUTGOING', iterations:20, dampingFactor:0.85, sourceNodes: [n]})
    YIELD nodeId, score
    RETURN algo.asNode(nodeId).name AS page,score
    ORDER BY score DESC
    """
    data = fetch_papers_by_algo(req, get_par)

    return data
