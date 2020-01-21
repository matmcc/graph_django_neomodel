from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty, AliasProperty, DateProperty)


class Author(StructuredNode):
    """Represents an Author node in Neo4j"""
    __name__ = 'Author'
    AuthorId = IntegerProperty(index=True)
    Rank = IntegerProperty()
    name = StringProperty(index=True)
    label = StringProperty()
    PaperCount = IntegerProperty()
    CitationCount = IntegerProperty()
    UpdatedAt = DateProperty()

    Id = AliasProperty(to='AuthorId')

    papers = RelationshipFrom('.paper.Paper', 'HAS_AUTHOR')
