from neomodel import (
    StringProperty,
    StructuredNode,
    RelationshipTo,
    RelationshipFrom,
    IntegerProperty,
    FloatProperty)


class PaperSimple(StructuredNode):
    """Represents a Paper node in Neo4j"""
    id = IntegerProperty(unique_index=True)
    cc = IntegerProperty()
    year = IntegerProperty()
    abstract = StringProperty()
    label = StringProperty()
    source = StringProperty()
    title = StringProperty(index=True)
    doi = StringProperty()
    prob = FloatProperty()

    # authors = RelationshipTo('.author.Author', 'WRITTEN_BY')
    # fields = RelationshipTo('.field.FieldOfStudy', 'FIELD')
    # references = RelationshipTo('.paper.Paper', 'CITES')
    # cited_by = RelationshipFrom('.paper.Paper', 'CITES')
