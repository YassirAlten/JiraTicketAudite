from django.shortcuts import render
from rest_framework import viewsets
from .models import JiraProject, JiraTicket ,JiraTicketHistory,AssignedUser,Coefficient
from .serializers import JiraTicketHistorySerializer, TicketSerializer, AssignedUserSerializer, ProjectSerializer,CoefficientSerializer
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

requested_fields = ["webhookEvent", "issue.fields.customfield_10016","issue.fields.customfield_10015","issue.fields.issuetype.name","issue.key","issue.fields.summary","issue.fields.creator.displayName","issue.fields.created", "issue.fields.priority.name","issue.fields.duedate", "issue.fields.assignee.displayName","issue.fields.updated","issue.fields.description","issue.fields.status.name","issue.fields.project.name","changelog.items"]

class JiraTicketViewSet(viewsets.ModelViewSet):
    queryset = JiraTicket.objects.all()
    serializer_class = TicketSerializer

class CoefficientViewSet(viewsets.ModelViewSet):
    queryset = Coefficient.objects.all()
    serializer_class = CoefficientSerializer

class HistoryViewSet(viewsets.ModelViewSet):
    queryset = JiraTicketHistory.objects.all()
    serializer_class = JiraTicketHistorySerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = JiraProject.objects.all()
    serializer_class = ProjectSerializer

class AssignedUserViewSet(viewsets.ModelViewSet):
    queryset = AssignedUser.objects.all()
    serializer_class = AssignedUserSerializer



def get_nested_value(dictionqry , path_string):
    key=path_string.split('.')
    current= dictionqry

    for k in key:
        if isinstance(current, dict) :
            current = current.get(k)
        else :
            return None
    return current

@extend_schema(
    request=dict,
    responses={200: dict}
)

@api_view(['POST'])
def extractDataFromJson(request):
    data = request.data
    if not isinstance(data, dict):
        return Response({"error": "Expected a JSON object"}, status=400)
    
    result = {field: get_nested_value(data, field) for field in requested_fields}

    project_name = result.get('issue.fields.project.name')
    project_instance = None
    if project_name:
        project_instance, created = JiraProject.objects.get_or_create(
            project_name=project_name,
            defaults={'project_manager': None}
        )

    assignee_name = result.get('issue.fields.assignee.displayName')
    user_instance = None
    if assignee_name:
        user_instance, created = AssignedUser.objects.get_or_create(
            fullName=assignee_name,
            defaults={'email': None}
        )

    ticket_data = {
        'ticket_key': result.get('issue.key'),
        'ticket_type': result.get('issue.fields.issuetype.name'),
        'summary': result.get('issue.fields.summary'),
        'estimated_time': result.get('issue.fields.duedate'),
        'status': result.get('issue.fields.status.name'),
        'priority': result.get('issue.fields.priority.name'),
        'created_at': result.get('issue.fields.created'),
        'updated_at': result.get('issue.fields.updated'),
        'start_date': result.get('issue.fields.customfield_10015'),
        'story_point':result.get('issue.fields.customfield_10016'),
        'description': result.get('issue.fields.description'),
        '_project': project_instance.pk if project_instance else None,
        'assignedUser': user_instance.pk if user_instance else None
    }
    
    ticket_key = result.get('issue.key')

    try:
        ticket_instance = JiraTicket.objects.get(ticket_key=ticket_key)
        ticket_serializer = TicketSerializer(ticket_instance, data=ticket_data)
    except JiraTicket.DoesNotExist:
        ticket_serializer = TicketSerializer(data=ticket_data)

    ticket_serializer.is_valid(raise_exception=True)
    ticket_serializer.save()

    return Response(result, status=200)

    