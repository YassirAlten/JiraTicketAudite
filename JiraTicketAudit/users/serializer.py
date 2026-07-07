from rest_framework import serializers
from .models import JiraUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraUser
        fields='__all__'
         