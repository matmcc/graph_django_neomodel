from .models import Author, FieldOfStudy, Paper
from rest_framework import serializers


class PaperSerializer(serializers.BaseSerializer):
    """
    Read-only serializer for Paper neomodel node
    """
    def to_representation(self, instance):
        # Todo: refs and cits will not return correct numbers when called from another serializer
        return {
            'id': instance.Id,
            'cc': instance.CC,
            'year': instance.year,
            'abstract': instance.abstract,
            # 'source': instance.source,
            'title': instance.name,
            'label': instance.label,
            'doi': instance.DOI,
            'authors': [AuthorSerializer(author).data for author in instance.authors.all()],
            'fields': [FieldOfStudySerializer(field).data for field in instance.fields.all()],
            'references': [paper.id for paper in instance.references.all()],
            'citations': [paper.id for paper in instance.cited_by.all()],
        }


class AuthorSerializer(serializers.BaseSerializer):
    """
    Read-only serializer for Author neomodel node
    """
    def to_representation(self, instance):
        return {
            'id': instance.Id,
            'label': instance.label,
            'name': instance.name,
        }


class AuthorWithPapersSerializer(serializers.BaseSerializer):
    """
    Read-only serializer for Author neomodel node
    """
    def to_representation(self, instance):
        return {
            'id': instance.Id,
            'label': instance.label,
            'name': instance.name,
            'papers': [PaperSerializer(paper).data for paper in instance.papers.all()]
        }


class FieldOfStudySerializer(serializers.BaseSerializer):
    """
    Read-only serializer for FieldOdStudy neomodel node
    """
    def to_representation(self, instance):
        return {
            'id': instance.Id,
            'label': instance.label,
            'name': instance.name,
            # parent and child fields go here
        }


class FieldOfStudyWithPapersSerializer(serializers.BaseSerializer):
    """
    Read-only serializer for FieldOdStudy neomodel node
    """
    def to_representation(self, instance):
        return {
            'id': instance.Id,
            'label': instance.label,
            'name': instance.name,
            'papers': [PaperSerializer(paper).data for paper in instance.papers.all()]
            # parent and child fields go here
        }


class ObjectSerializer(serializers.BaseSerializer):
    """
    A read-only serializer that coerces arbitrary complex objects
    into primitive representations.
    """
    def to_representation(self, instance):
        output = {}
        for attribute_name in dir(instance):
            attribute = getattr(instance, attribute_name)
            if attribute_name.startswith('_'):
                # Ignore private attributes.
                pass
            elif hasattr(attribute, '__call__'):
                # Ignore methods and other callables.
                pass
            elif isinstance(attribute, (str, int, bool, float, type(None))):
                # Primitive types can be passed through unmodified.
                output[attribute_name] = attribute
            elif isinstance(attribute, list):
                # Recursively deal with items in lists.
                output[attribute_name] = [
                    self.to_representation(item) for item in attribute
                ]
            elif isinstance(attribute, dict):
                # Recursively deal with items in dictionaries.
                output[attribute_name] = {
                    str(key): self.to_representation(value)
                    for key, value in attribute.items()
                }
            else:
                # Force anything else to its string representation.
                output[attribute_name] = str(attribute)
        return output
