from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty, AliasProperty)


class Author(StructuredNode):
    """Represents an Author node in Neo4j"""
    Id = IntegerProperty(index=True)
    label = StringProperty()
    name = StringProperty(index=True)

    papers = RelationshipFrom('.paper.Paper', 'HAS_AUTHOR')
    # AuId = IntegerProperty(index=True)
    # id = AliasProperty(to='AuId')
    # DAuN = StringProperty()
    # label = AliasProperty(to='DAuN')
    # AuN = StringProperty(index=True)
    # name = AliasProperty(to='AuN')
