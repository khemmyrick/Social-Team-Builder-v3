from django.contrib.auth import get_user_model

from rest_framework import serializers
from .models import Project, Position, Applicant


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'description',
            'creator',
            'requirements'
        )
        model = Project


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'description',
            'filled',
            'project',
            'user',
            'skills',
            'time'
        )
        model = Position


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user',
            'position',
            'status'
        )
        model = Applicant