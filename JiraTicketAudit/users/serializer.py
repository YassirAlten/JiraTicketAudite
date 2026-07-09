from rest_framework import serializers
from .models import JiraUser
from django.conf import settings
from django.contrib.auth import get_user_model

User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['username','email','password']
        extra_kwargs = {'password': {'write_only': True}}

class JiraUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = JiraUser
        fields = ['id', 'user', 'jira_key']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        django_user = User.objects.create_user(**user_data)
        
        jira_user = JiraUser.objects.create(user=django_user, **validated_data)
        return jira_user
         