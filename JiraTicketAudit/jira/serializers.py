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
    # Correction pour l'utilisateur assigné : accepte l'ID en entrée et le convertit en instance AssignedUser
    assignedUser = serializers.PrimaryKeyRelatedField(
        source='assigned_user', 
        queryset=AssignedUser.objects.all(),
        allow_null=True,
        required=False
    )
    
    # Correction pour le projet : accepte l'ID en entrée et le convertit en instance JiraProject
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
            'assignedUser', # Ce nom correspond à la clé de votre dictionnaire ticket_data
            'created_at', 
            'updated_at', 
            'start_date',
            '_project'      # Ce nom correspond à la clé de votre dictionnaire ticket_data
        ]




class JiraTicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraTicketHistory
        fields='__all__'