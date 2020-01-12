from neomodel import config, db

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


def create_uniqueness_constraint(label, property):
    # Also creates index in DB
    query = f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    db.cypher_query(query)


def create_index(label, property):
    query = f"CREATE INDEX ON :{label}({property})"
    db.cypher_query(query)


constraints = [("Paper", "Id"), ("Author", "Id"), ("FieldOfStudy", "Id")]
indexes = [("Paper", "name"), ("Author", "name"), ("FieldOfStudy", "name")]

for (l, p) in constraints:
    create_uniqueness_constraint(l, p)

for (l, p) in indexes:
    create_index(l, p)
