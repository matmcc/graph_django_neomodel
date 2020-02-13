import pickle

from decorators import timing
from graph_api.models import FieldOfStudy
from mag.Mag import Mag_Api
from neomodel import config, db

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'

# m = Mag_Api()
# FoS = FieldOfStudy.nodes.all()
# Field_ids = [f.Id for f in FoS]
#
# fields = []
# for i in range(0, len(Field_ids), 100):
#     fields += m.evaluate(m._make_or(Field_ids[i:i+100]), attribs='Id,FC.FId,FP.FId', count=1000)
#
# with open('fields.pickle', 'wb') as f:
#     pickle.dump(fields, f, protocol=pickle.HIGHEST_PROTOCOL)
fields = pickle.load(open('fields.pickle', 'rb'))

field_rels_child = set()
for f in fields:
    if 'FC' in f:
        for fc in f['FC']:
            field_rels_child.add((f['Id'], fc['FId']))

field_rels_parent = set()
for f in fields:
    if 'FP' in f:
        for fp in f['FP']:
            field_rels_parent.add((fp['FId'], f['Id']))

field_rels = field_rels_child | field_rels_parent

l_relations = [{'source': source, 'target': target} for source, target in field_rels]

add_field_relationships = """
UNWIND {batch} as row
MATCH (s:FieldOfStudy {Id:row.source})
WITH s, row
MATCH (t:FieldOfStudy {Id:row.target})
MERGE (s)-[:HAS_CHILD]->(t)
"""


@timing
def add_rels():
    db.cypher_query(add_field_relationships, {'batch': l_relations})


add_rels()
print('done')
