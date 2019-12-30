from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty, AliasProperty, FloatProperty)


# Todo: changed from StructuredNode to DjangoNode to support ModelSerializer - but unsuccessful - change back?
class Paper(StructuredNode):
    """Represents a Paper node in Neo4j"""
    Id = IntegerProperty(unique_index=True)
    CC = IntegerProperty()
    year = IntegerProperty()
    abstract = StringProperty()
    label = StringProperty()
    source = StringProperty()
    name = StringProperty(index=True)
    DOI = StringProperty()
    prob = FloatProperty()

    authors = RelationshipTo('.author.Author', 'HAS_AUTHOR')
    fields = RelationshipTo('.field.FieldOfStudy', 'HAS_FIELD')
    references = RelationshipTo('.paper.Paper', 'CITES')
    cited_by = RelationshipFrom('.paper.Paper', 'CITES')
