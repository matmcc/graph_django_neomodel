from graph_api.models import Paper, Author, FieldOfStudy
from mag.Mag import Mag_Api, build_abstract
from decorators import timing
from neomodel import config, db


# config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


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


# Build db
# @timing
def add_mag_paper_to_graph_db(paper_from_Mag):
    """Adds a MAG paper to db via neomodel ogm.
        Adds refs only if paper exists in graph"""

    # Todo: Too Slow! Try cypher instead

    # if paper already exists, skip
    if Paper.nodes.get_or_none(Ti=paper_from_Mag['Ti']):
        # print(paper_from_Mag)
        return

    # fix abstract and get first source link
    if paper_from_Mag.get('IA', None):
        paper_from_Mag['Ab'] = build_abstract(paper_from_Mag.pop('IA'))
    if paper_from_Mag.get('S', None):
        paper_from_Mag['S'] = paper_from_Mag.pop('S')[0]['U']
    paper_from_Mag.pop('prob', None)

    fields = paper_from_Mag.pop('F', None)
    authors = paper_from_Mag.pop('AA', None)
    references = paper_from_Mag.pop('RId', None)

    paper = Paper(**paper_from_Mag).save()

    for f in fields:
        field = FieldOfStudy(**f)
        field_already_exists = field.nodes.get_or_none(FN=field.FN)
        if field_already_exists:
            paper.fields.connect(field_already_exists)
        else:
            field.save()
            paper.fields.connect(field)
    for a in authors:
        author = Author(**a)
        author_already_exists = author.nodes.get_or_none(AuN=author.AuN)
        if author_already_exists:
            paper.authors.connect(author_already_exists)
        else:
            author.save()
            paper.authors.connect(author)
    if references:
        for ref in references:
            reference_exists = paper.nodes.get_or_none(Id=ref)
            if reference_exists:
                paper.references.connect(reference_exists)

    paper.save()


query = """
     MERGE (paper:Paper { id: {Id} }) ON CREATE
           SET paper += { cc: {CC}, year: {Y}, abstract: {Ab}, label: {DN},
                         source: {S}, title: {Ti}, doi: {DOI}, prob: {logprob} } 
       WITH paper
       UNWIND {F} AS field
           MERGE (f:FieldOfStudy { name: field.FN }) ON CREATE
               SET f.id = field.FId, f.label = field.DFN
           MERGE (paper)-[:HAS_FIELD]->(f)
       WITH paper
       UNWIND {AA} AS author
           MERGE (a:Author { name: author.AuN }) ON CREATE
               SET a.id = author.AuId, a.label = author.DAuN
           MERGE (paper)-[:HAS_AUTHOR]->(a)
"""
query2 = """
     CREATE (paper:Paper)
     WITH paper
       UNWIND paper.F AS field
           MERGE (f:FieldOfStudy { name: field.FN }) ON CREATE
               SET f.id = field.FId, f.label = field.DFN
           MERGE (paper)-[:HAS_FIELD]->(f)
       WITH paper
       UNWIND paper.AA AS author
           MERGE (a:Author { name: author.AuN }) ON CREATE
               SET a.id = author.AuId, a.label = author.DAuN
           MERGE (paper)-[:HAS_AUTHOR]->(a)
    RETURN paper
"""
queryApoc = """
         CALL apoc.create.node(['Paper'], {params}) YIELD node AS paper
         UNWIND paper.F AS field
         MERGE (f:FieldOfStudy { name: field.FN }) ON CREATE
         SET f.id = field.FId, f.label = field.DFN
         MERGE (paper)-[:HAS_FIELD]->(f)
         WITH paper
         UNWIND paper.AA AS author
         MERGE (a:Author { name: author.AuN }) ON CREATE
         SET a.id = author.AuId, a.label = author.DAuN
         MERGE (paper)-[:HAS_AUTHOR]->(a)
         """


def clean_paper_from_mag(paper_from_Mag):
    if paper_from_Mag.get('IA', None):
        paper_from_Mag['Ab'] = build_abstract(paper_from_Mag.pop('IA'))
    if paper_from_Mag.get('S', None):
        paper_from_Mag['S'] = paper_from_Mag.pop('S')[0]['U']
    paper_from_Mag.pop('Pr', None)
    return paper_from_Mag


@timing
def add_paper_by_cypher(query, params):
    results, meta = db.cypher_query(query, {'batch': params})
    return results, meta


add_papers = """
UNWIND {batch} as row
MERGE (p:Paper {name:row.Ti}) ON CREATE
SET p += {CC:row.CC, year:row.Y, abstract:row.Ab, label:row.DN, Id:row.Id, DOI:row.DOI, prob:row.logprob}
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


on_click()
