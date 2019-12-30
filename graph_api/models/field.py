from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty,
    AliasProperty)


class FieldOfStudy(StructuredNode):
    """Represents an Author node in Neo4j"""
    Id = IntegerProperty(index=True)
    label = StringProperty()
    name = StringProperty(index=True)
    # FId = IntegerProperty(index=True)
    # id = AliasProperty(to='FId')
    # DFN = StringProperty()
    # label = AliasProperty(to='DFN')
    # FN = StringProperty(index=True)
    # name = AliasProperty(to='FN')

    papers = RelationshipFrom('.paper.Paper', 'HAS_FIELD')
    child = RelationshipTo('.field.FieldOfStudy', 'HAS_CHILD')
    parent = RelationshipFrom('.field.FieldOfStudy', 'HAS_CHILD')
