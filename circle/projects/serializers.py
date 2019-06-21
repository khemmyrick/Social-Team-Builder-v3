from rest_framework import serializers
from .models import Project, Skill, Position, Applicant


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'url',
            'description',
            'creator',
            'requirements',
            'time',
            'active'
        )
        model = Project


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('name',)


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'description',
            'filled',
            'project',
            'user',
            'skills',
            'time',
            'active'
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
