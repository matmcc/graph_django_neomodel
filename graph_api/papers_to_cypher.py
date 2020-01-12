import pickle
from neomodel import config, db

from decorators import timing
from mag.Mag import Mag_Api, build_abstract

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


def clean_paper_from_mag(paper_from_Mag):
    if isinstance(paper_from_Mag, dict):
        if paper_from_Mag.get('IA', None):
            paper_from_Mag['Ab'] = build_abstract(paper_from_Mag.pop('IA'))
        if paper_from_Mag.get('S', None):
            # if len(paper_from_Mag['S']) > 1:
            try:
                paper_from_Mag['S'] = paper_from_Mag['S'][0]['U']
            except (TypeError, IndexError, KeyError) as e:
                print(paper_from_Mag['S'])
                print(e)
        paper_from_Mag.pop('Pr', None)
        paper_from_Mag['RC'] = len(paper_from_Mag.get('RId', ''))
        return paper_from_Mag
    else:
        print(paper_from_Mag)
        msg = 'paper_from_mag argument should be type(dict), instead type: {}'.format(type(paper_from_Mag))
        raise TypeError(msg)


@timing
def add_paper_by_cypher(query, params):
    params = [clean_paper_from_mag(p) for p in params]
    results, meta = db.cypher_query(query, {'batch': params})
    return results, meta


def batch(seq, size):
    """ returns generator of slices of seq of len(size) """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


add_papers = """
UNWIND {batch} as row
MERGE (p:Paper {Id:row.Id}) ON CREATE
SET p += {CC:row.CC, RC:row.RC, year:row.Y, abstract:row.Ab, source:row.S, label:row.DN, name:row.Ti, DOI:row.DOI, prob:row.logprob}
WITH p, row
UNWIND row.F AS field
MERGE (f:FieldOfStudy { Id: field.FId }) ON CREATE
SET f.name = field.FN, f.label = field.DFN
MERGE (p)-[:HAS_FIELD]->(f)
WITH p, row
UNWIND row.AA AS author
MERGE (a:Author { Id: author.AuId }) ON CREATE
SET a.name = author.AuN, a.label = author.DAuN
MERGE (p)-[:HAS_AUTHOR]->(a)
"""

add_cites_relations_batch = """
UNWIND {batch} as row
MATCH (s:Paper {Id:row.source})
WITH s, row
MATCH (t:Paper {Id:row.target})
MERGE (s)-[:CITES]->(t)
"""

d = pickle.load(open('mag.pickle', 'rb'))
_PAPERS = d['_PAPERS']
_REFS = d['_REFS']
_CITS = d['_CITS']
_EXPANDED = d['_EXPANDED']


@timing
def add_papers_():
    print('papers')
    _p = list(_PAPERS.values())
    i = 0
    for _batch in batch(_p, 1000):
        print(i)
        i += 1
        add_paper_by_cypher(add_papers, _batch)


@timing
def add_citing_relations():
    print('refs')
    relations = set()

    for paper, list_of_refs in _REFS.items():
        for referenced_paper in list_of_refs:
            relations.add((paper, referenced_paper))

    for paper, list_of_cits in _CITS.items():
        for citing_paper in list_of_cits:
            relations.add((citing_paper, paper))

    l_relations = [{'source': source, 'target': target} for source, target in relations]

    db.cypher_query(add_cites_relations_batch, {'batch': l_relations})


add_papers_()
add_citing_relations()
print('done')
