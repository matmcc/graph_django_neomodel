from .models import Author, FieldOfStudy, Paper
from rest_framework import serializers


class PaperSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    cc = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    abstract = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    doi = serializers.CharField(read_only=True)

    # ModelSerializer did not work - _meta class on neomodel did not seem to work
    # These are here as required, but API intended as read_only
    def create(self, validated_data):
        return NotImplementedError

    def update(self, instance, validated_data):
        return NotImplementedError
# class PaperSerializer(serializers.ModelSerializer):
#
#
#     class Meta:
#         model = Paper
#         fields = ['id', 'cc', 'year', 'abstract', 'source', 'title', 'doi']


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return NotImplementedError

    def update(self, instance, validated_data):
        return NotImplementedError


class FieldOfStudySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return NotImplementedError

    def update(self, instance, validated_data):
        return NotImplementedError
