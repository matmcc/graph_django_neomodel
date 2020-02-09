import pickle
from neomodel import config, db

from decorators import timing
from mag.Mag import Mag_Api, build_abstract

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'
m = Mag_Api()


@timing
def get_paper_via_interpret(query):
    interpret_results = m.interpret(query)
    if not interpret_results:
        return []
    evaluate_interpret = m.evaluate(interpret_results[0], count=50)
    papers = [p["Id"] for p in evaluate_interpret]
    update_papers(papers)
    return papers


@timing
def update_papers(paper_ids):
    # Call MAG for papers
    papers_from_mag = m.get_papers(paper_ids)
    # Clean source nad inverted abstract fields for Neo4J
    papers_from_mag_cleaned = [clean_paper_from_mag(p) for p in papers_from_mag]
    # add papers, authors, paper->author edges, fields, paper->field edges
    # separate transactions faster and easier to debug
    db.cypher_query(add_papersPAPERS, {'batch': papers_from_mag_cleaned})
    db.cypher_query(add_papersAUTHORS, {'batch': papers_from_mag_cleaned})
    db.cypher_query(add_papersAu_RELATIONS, {'batch': papers_from_mag_cleaned})
    db.cypher_query(add_papersFIELDS, {'batch': papers_from_mag_cleaned})
    db.cypher_query(add_papersFoS_RELATIONS, {'batch': papers_from_mag_cleaned})
    # todo: should check if CitationCount matches in-degree - otherwise check for new citation


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


# Cypher statements
# add_papers would add a batch in one statement.
# DB performs faster using simpler queries, with relations separated - better execution planning
# Also easier to debug or refactor
add_papersPAPERS = """
UNWIND {batch} AS row
MERGE (p:Paper {PaperId:row.Id}) 
ON CREATE SET p += {CitationCount:row.CC, ReferenceCount:row.RC, Year:row.Y, abstract:row.Ab, source:row.S, label:row.DN, name:row.Ti, DOI:row.DOI, prob:row.logprob, UpdatedAt:date()}
ON MATCH SET p += {CitationCount:row.CC, ReferenceCount:row.RC, Year:row.Y, abstract:row.Ab, source:row.S, label:row.DN, name:row.Ti, DOI:row.DOI, prob:row.logprob, UpdatedAt:date()}
"""

add_papersFIELDS = """
UNWIND {batch} AS row
UNWIND row.F AS field
MERGE (f:FieldOfStudy { FieldOfStudyId: field.FId })
ON CREATE SET f.name = field.FN, f.label = field.DFN, f.UpdatedAt = date()
ON MATCH SET f.name = field.FN, f.label = field.DFN, f.UpdatedAt = date()
"""

add_papersAUTHORS = """
UNWIND {batch} AS row
UNWIND row.AA AS author
MERGE (a:Author { AuthorId: author.AuId }) 
ON CREATE SET a.name = author.AuN, a.label = author.DAuN, a.UpdatedAt = date()
ON MATCH SET a.name = author.AuN, a.label = author.DAuN, a.UpdatedAt = date()
"""

add_papersFoS_RELATIONS = """
UNWIND {batch} AS row
MATCH (p:Paper {PaperId:row.Id})
WITH p, row
UNWIND row.F AS field
MATCH (f:FieldOfStudy { FieldOfStudyId: field.FId })
MERGE (p)-[:HAS_FIELD]->(f) 
"""

add_papersAu_RELATIONS = """
UNWIND {batch} AS row
MATCH (p:Paper {PaperId:row.Id})
WITH p, row
UNWIND row.AA AS author
MATCH (a:Author { AuthorId: author.AuId })
MERGE (p)-[:HAS_AUTHOR]->(a) 
"""

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
MATCH (t:Paper {Id:row.target})
MERGE (s)-[:CITES]->(t)
"""
# WITH s, row (between MATCH statements)

# d = pickle.load(open('mag.pickle', 'rb'))
# _PAPERS = d['_PAPERS']
# _REFS = d['_REFS']
# _CITS = d['_CITS']
# _EXPANDED = d['_EXPANDED']
#
#
# @timing
# def add_papers_():
#     print('papers')
#     _p = list(_PAPERS.values())
#     i = 0
#     for _batch in batch(_p, 1000):
#         print(i)
#         i += 1
#         add_paper_by_cypher(add_papers, _batch)
#
#
# @timing
# def add_citing_relations():
#     print('refs')
#     relations = set()
#
#     for paper, list_of_refs in _REFS.items():
#         for referenced_paper in list_of_refs:
#             relations.add((paper, referenced_paper))
#
#     for paper, list_of_cits in _CITS.items():
#         for citing_paper in list_of_cits:
#             relations.add((citing_paper, paper))
#
#     l_relations = [{'source': source, 'target': target} for source, target in relations]
#
#     db.cypher_query(add_cites_relations_batch, {'batch': l_relations})
#
#
# add_papers_()
# add_citing_relations()
# print('done')
