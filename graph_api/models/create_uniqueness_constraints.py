from neomodel import db


def create_uniqueness_constraint(label, property):
    query = f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    db.cypher_query(query)


constraints = [("Paper", "Id"), ("Paper", "Ti"),
               ("Author", "AuId"), ("Author", "AuN"),
               ("FieldOfStudy", "FId"), ("FieldOfStudy", "FN")]

for (l, n) in constraints:
    create_uniqueness_constraint(l, n)
