from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty,
    AliasProperty, DateProperty)


class FieldOfStudy(StructuredNode):
    """Represents an Author node in Neo4j"""
    __name__ = "FieldOfStudy"

    FieldOfStudyId = IntegerProperty(index=True)
    Rank = IntegerProperty()
    name = StringProperty(index=True)
    label = StringProperty()
    MainType = StringProperty()
    Level = IntegerProperty()
    PaperCount = IntegerProperty()
    CitationCount = IntegerProperty()
    UpdatedAt = DateProperty()

    Id = AliasProperty(to='FieldOfStudyId')

    papers = RelationshipFrom('.paper.Paper', 'HAS_FIELD')
    child = RelationshipTo('.field.FieldOfStudy', 'HAS_CHILD')
    parent = RelationshipFrom('.field.FieldOfStudy', 'HAS_CHILD')
