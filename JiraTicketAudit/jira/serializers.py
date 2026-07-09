from rest_framework import serializers

from .models import AssignedUser, JiraTicket, JiraTicketHistory, JiraProject , Coefficient

class AssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedUser
        fields='__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraProject
        fields='__all__'



class TicketSerializer(serializers.ModelSerializer):
    assignedUser = serializers.PrimaryKeyRelatedField(
        source='assigned_user', 
        queryset=AssignedUser.objects.all(),
        allow_null=True,
        required=False
    )
    
    _project = serializers.PrimaryKeyRelatedField(
        source='project', 
        queryset=JiraProject.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = JiraTicket
        fields = [
            'ticket_key', 
            'ticket_type', 
            'summary', 
            'estimated_time', 
            'description', 
            'status', 
            'priority', 
            'assignedUser', 
            'created_at', 
            'updated_at', 
            'story_point',
            'start_date',
            '_project'      
        ]




class JiraTicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraTicketHistory
        fields='__all__'

class CoefficientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Coefficient
        fields='__all__'