from rest_framework import serializers

from .models import AssignedUser, JiraTicket, JiraTicketHistory, JiraProject

class AssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedUser
        fields='__all__'
        
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraProject
        fields='__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraTicket
        assigned_user = AssignedUserSerializer()
        project = ProjectSerializer()
        fields='__all__'



class JiraTicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraTicketHistory
        fields='__all__'