import pickle
import logging

from graph_api.models import Paper, Author, FieldOfStudy
from mag.Mag import Mag_Api, build_abstract
from decorators import timing

from neomodel import config, db


config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'
logger = logging.getLogger(__name__)



#  Mag util functions
@timing
def get_one_paper(mag_instance, q):
    return mag_instance.get_paper(q)


@timing
def expand_from_mag_paper(mag_instance, mag_paper):
    refs = mag_instance.get_refs(mag_paper)
    cits = mag_instance.get_cits(mag_paper)
    return {'refs': refs, 'cits': cits}


m = Mag_Api()
seed = 2157025439


def clean_paper_from_mag(paper_from_Mag):
    if paper_from_Mag.get('IA', None):
        paper_from_Mag['Ab'] = build_abstract(paper_from_Mag.pop('IA'))
    if paper_from_Mag.get('S', None):
        # if len(paper_from_Mag['S']) > 1:
        try:
            paper_from_Mag['S'] = paper_from_Mag['S'][0]['U']
        except (TypeError, IndexError, KeyError) as e:
            print(paper_from_Mag)
            print(e)
    paper_from_Mag.pop('Pr', None)
    paper_from_Mag['RC'] = len(paper_from_Mag.get('RId', ''))
    return paper_from_Mag


@timing
def add_paper_by_cypher(query, params):
    params = [clean_paper_from_mag(p) for p in params]
    results, meta = db.cypher_query(query, {'batch': params})
    return results, meta


add_papers = """
UNWIND {batch} as row
MERGE (p:Paper {name:row.Ti}) ON CREATE
SET p += {CC:row.CC, RC:row.RC, year:row.Y, abstract:row.Ab, source:row.S, label:row.DN, Id:row.Id, DOI:row.DOI, prob:row.logprob}
WITH p, row
UNWIND row.F AS field
MERGE (f:FieldOfStudy { name: field.FN }) ON CREATE
SET f.Id = field.FId, f.label = field.DFN
MERGE (p)-[:HAS_FIELD]->(f)
WITH p, row
UNWIND row.AA AS author
MERGE (a:Author { name: author.AuN }) ON CREATE
SET a.Id = author.AuId, a.label = author.DAuN
MERGE (p)-[:HAS_AUTHOR]->(a)
"""
# Todo: add Source
# Todo: add Abstract
# Todo: add RR count for refs?
# Todo: build adapter?? to do above
# Note: cypher has limited types - will error if json includes lists that are not dealt with correctly.

add_refs = """
MATCH (s:Paper {Id:{source}})
WITH s
UNWIND {target} AS tId
MATCH (t:Paper {Id:tId})
MERGE (s)-[:CITES]->(t)
"""

add_cits = """
MATCH (t:Paper {Id:{target}})
WITH t
UNWIND {source} AS sId
MATCH (s:Paper {Id:sId})
MERGE (s)-[:CITES]->(t)
"""

add_refs_batch = """
UNWIND {batch} AS row
MATCH (s:Paper {Id:row.source})
WITH s, row
UNWIND row.target AS tId
MATCH (t:Paper {Id:tId})
MERGE (s)-[:CITES]->(t)
"""

add_cits_batch = """
UNWIND {batch} as row
MATCH (t:Paper {Id:row.target})
WITH t, row
UNWIND row.source AS sId
MATCH (s:Paper {Id:sId})
MERGE (s)-[:CITES]->(t)
"""


@timing
def on_click():
    print('get one paper')
    p = get_one_paper(m, seed)
    print('add to db')
    # add_mag_paper_to_graph_db(p)
    add_paper_by_cypher(add_papers, [p])
    print('hop')
    hop = expand_from_mag_paper(m, p)
    print('refs')
    ref_nodes, _ = add_paper_by_cypher(add_papers, hop['refs'])
    # for ref in hop['refs']:
    #     add_mag_paper_to_graph_db(ref)
    # print('cits')
    # for cit in hop['cits']:
    #     p = clean_paper_from_mag(cit)
    cit_nodes, meta = add_paper_by_cypher(add_papers, hop['cits'])
    print('adding citation relations')
    ref_ids = p['RId']
    db.cypher_query(add_refs, {'source': p['Id'], 'target': ref_ids})
    cit_ids = [n['Id'] for n in hop['cits']]
    db.cypher_query(add_cits, {'source': cit_ids, 'target': p['Id']})

    papers = hop['refs'] + hop['cits']
    new_papers = expand(papers)
    return new_papers


@timing
def expand(set_of_papers):
    l_refs = []
    l_cits = []
    papers = []
    for p in set_of_papers:
        # print(p)
        # print('getting refs')
        refs = m.get_refs(p)
        # print('getting cits')
        cits = m.get_cits(p)
        try:
            cits_ids = [c['Id'] for c in cits]
        except TypeError as e:
            try:
                cits_ids = cits['Id']
            except (TypeError, IndexError) as e:
                cits_ids = None
                print(e)
                print(cits)
            # for c in cits:
            #     if type(c) == type(''):
            #         print(c)
        papers += refs
        papers += cits
        if 'RId' in p:
            l_refs.append({'source': p['Id'], 'target': p['RId']})
        if p['CC'] > 0:
            try:
                l_cits.append({'source': cits_ids, 'target': p['Id']})
            except TypeError as e:
                print(e)
                print(p)

    print('add papers')
    add_paper_by_cypher(add_papers, papers)
    print('add refs')
    db.cypher_query(add_refs_batch, {'batch': l_refs})
    print('adding cits')
    db.cypher_query(add_cits_batch, {'batch': l_cits})
    return papers

# papers = on_click()

# p = get_one_paper(m, seed)
# print('add to db')
# # add_mag_paper_to_graph_db(p)
# add_paper_by_cypher(add_papers, [p])
# p2 = expand([p])
# p3 = expand(p2)


def expand_mag(papers):
    d = {}
    # d['errors'] = []
    ps = []
    for p in papers:
        try:
            i = p['Id']
            refs = m.get_refs(p)
            cits = m.get_cits(p)
            if isinstance(refs, dict):
                refs = [refs]
            if isinstance(cits, dict):
                cits = [cits]
            t = {'refs': refs, 'cits': cits}
            d[i] = t
            ps += refs
            ps += cits
        except TypeError:
            d['errors'] += p
    return d, ps


_PAPERS = {}
_REFS = {}
_CITS = {}
_EXPANDED = {}


@timing
def expand_2(papers, tuple_papers_refs_cits=(_PAPERS, _REFS, _CITS, _EXPANDED)):
    _p = _PAPERS
    _r = _REFS
    _c = _CITS
    _done = _EXPANDED
    for paper in papers:
        # If already called, skip
        if _done.get(paper['Id'], False):
            continue
        # if not in paper dict add to paper dict
        if paper['Id'] not in _p:
            _p[paper['Id']] = paper
        # if Refs...
        if 'RId' in paper and isinstance(paper['RId'], list):
            refs = m.get_refs(paper)  # get refs
            # ensure refs is a list
            if isinstance(refs, dict):
                refs = [refs]

            _r[paper['Id']] = paper['RId']  # add ref list
            # add referenced papers
            for r in refs:
                _p[r['Id']] = r

        # if citations ...
        if 'CC' in paper and paper['CC'] > 0:
            cits = m.get_cits(paper)
            if isinstance(cits, dict):
                cits = [cits]
            cit_ids = []

            # add citing papers
            for c in cits:
                _p[c['Id']] = c
                cit_ids.append(c['Id'])
            # add cit list
            _c[paper['Id']] = cit_ids

        # add to _done
        _done[paper['Id']] = True



# p1 = get_one_paper(m, seed)
# p2, ps = expand_mag([p1])
# p3, ps = expand_mag(ps)

# shells = {'1': p1, '2': p2, '3': p3}
# with open('mag_dict_123.pickle', 'wb') as f:
#     pickle.dump(shells, f, protocol=pickle.HIGHEST_PROTOCOL)
# print('done')

# p1 = get_one_paper(m, seed)
# expand_2([p1])
# expand_2(list(_PAPERS.values()))
#
# with open('mag.pickle', 'wb') as f:
#     pickle.dump({'_PAPERS': _PAPERS, '_REFS': _REFS, '_CITS': _CITS, '_EXPANDED': _EXPANDED}, f, protocol=pickle.HIGHEST_PROTOCOL)
# print('done')

d = pickle.load(open('mag.pickle', 'rb'))
_P = d['_PAPERS']
_R = d['_REFS']
_C = d['_CITS']
_E = d['_EXPANDED']

for p in _E:
    if _E[p]:
        _P.pop(p, None)

expand_2(list(_P.values()))

with open('mag_hop4.pickle', 'wb') as f:
    pickle.dump({'_PAPERS': _PAPERS, '_REFS': _REFS, '_CITS': _CITS, '_EXPANDED': _EXPANDED}, f, protocol=pickle.HIGHEST_PROTOCOL)
print('done')

