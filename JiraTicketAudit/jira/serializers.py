from rest_framework import serializers

from .models import AssignedUser, JiraTicket, JiraTicketHistory, JiraProject ,ConfigurationData,Coefficient


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
            'id',
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
    project= ProjectSerializer()
    class Meta:
        model=Coefficient
        fields=['project','summary_coefficient','description_coefficient','priority_check_coefficient','estimated_time_check_coeffichient']




class ConfiguratinSerializer(serializers.ModelSerializer):
    coefficient=CoefficientSerializer()
    class Meta:
        model=ConfigurationData
        fields=[
            'coefficient',
            'configuration_json'
        ]
    def create (self , validatedData):
        coefficient=validatedData.pop('coefficient')
        projectData=coefficient.pop('project')

        created_project , _=JiraProject.objects.get_or_create( project_name=projectData['project_name'],defaults={'project_manager': projectData['project_manager']})
        createdCoefficient=Coefficient.objects.create(project=created_project, **coefficient)
        
        createdConfiguration=ConfigurationData.objects.create(
            coefficient=createdCoefficient,
            **validatedData
        )
        return createdConfiguration


