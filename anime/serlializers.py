from rest_framework import serializers
from .models import *


class ProjectSerializer(serializers.Serializer):
    projectName = serializers.CharField(max_length=100)
    image = serializers.ListField(child=serializers.FileField(allow_empty_file=False))
    audio = serializers.ListField(child=serializers.FileField(allow_empty_file=False))