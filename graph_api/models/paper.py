from django_neomodel import DjangoNode
from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty, AliasProperty, FloatProperty, DateProperty)


class Paper(StructuredNode):
    """Represents a Paper node in Neo4j"""
    __name__ = 'Paper'
    PaperId = IntegerProperty(unique_index=True)
    Rank = IntegerProperty()
    DOI = StringProperty()
    Doctype = StringProperty()
    name = StringProperty(index=True)
    label = StringProperty()
    Year = IntegerProperty()
    Date = DateProperty()
    Publisher = StringProperty()
    Volume = StringProperty()
    Issue = StringProperty()
    FirstPage = StringProperty()
    LastPage = StringProperty()
    ReferenceCount = IntegerProperty()
    CitationCount = IntegerProperty()
    abstract = StringProperty()
    source = StringProperty()
    prob = FloatProperty()
    community = IntegerProperty()
    UpdatedAt = DateProperty()

    Id = AliasProperty(to='PaperId')
    CC = AliasProperty(to='CitationCount')
    RC = AliasProperty(to='ReferenceCount')

    authors = RelationshipTo('.author.Author', 'HAS_AUTHOR')
    fields = RelationshipTo('.field.FieldOfStudy', 'HAS_FIELD')
    references = RelationshipTo('.paper.Paper', 'CITES')
    cited_by = RelationshipFrom('.paper.Paper', 'CITES')

    # Todo: add methods to test now - updated_at > some_value => update
