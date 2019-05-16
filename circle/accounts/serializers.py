from django.contrib.auth import get_user_model

from rest_framework import serializers
from .models import Skill


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    #
    # def create(self, validated_data):
    #    user = get_user_model().objects.create(
    #        username=validated_data['username'],
    #        email=validated_data['email'],
    #        display_name=validated_data['display_name'],
    #        bio=validated_data['bio'],
    #        is_active=validated_data['is_active'],
    #        is_staff=validated_data['is_staff']
    #    )
    #    user.set_password(validated_data['password'])
    #    user.save()
    #    return user

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'username',
            'password',
            'display_name',
            'bio',
            'avatar',
            'is_active',
            'is_staff'
        )

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('name', 'users')
