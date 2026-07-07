from django.shortcuts import render
from rest_framework import viewsets
from .models import JiraProject, JiraTicket ,JiraTicketHistory,AssignedUser
from .serializers import JiraTicketHistorySerializer, TicketSerializer, AssignedUserSerializer, ProjectSerializer
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

requested_fields = ["webhookEvent","issue.fields.issuetype.name","issue.key","issue.fields.summary","issue.fields.creator.displayName","issue.fields.created", "issue.fields.priority.name","issue.fields.timeestimate", "issue.fields.assignee.displayName","issue.fields.updated","issue.fields.status.description","issue.fields.status.name","issue.fields.project.name","changelog.items"]

class JiraTicketViewSet(viewsets.ModelViewSet):
    queryset = JiraTicket.objects.all()
    serializer_class = TicketSerializer

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
    
    if isinstance(request.data, (dict, list)):
                  data = request.data
    elif isinstance(request.body, (bytes, str)):
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format"}, status=400)
    else:
        try:
            data = json.loads(request.body or b'{}')
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format"}, status=400)
    if not isinstance(data, dict):
        return Response({"error": "Expected a JSON object"}, status=400)
    
    result = {field: get_nested_value(data, field) for field in requested_fields}

    project = JiraProject.objects.filter(project_name=result.get('issue.fields.project.name')).first()
    assigned_user = AssignedUser.objects.filter(fullName=result.get('issue.fields.assignee.displayName')).first()

    
    ticket_data = {
    'ticket_key': result.get('issue.key'),
    'ticket_type': result.get('issue.fields.issuetype.name'),
    'summary': result.get('issue.fields.summary'),
    'estimated_time': result.get('issue.fields.timeestimate'),
    'status': result.get('issue.fields.status.name'),
    'priority': result.get('issue.fields.priority.name'),
    'created_at': result.get('issue.fields.created'),
    'updated_at': result.get('issue.fields.updated'),
    'description': result.get('issue.fields.description'),
    'project': project,
    'assigned_user': assigned_user
    
}
    if not JiraProject.objects.filter(project_name=result.get('issue.fields.project.name')).exists():
        project = ProjectSerializer.create(project_name=result.get('issue.fields.project.name'), project_manager=None)
        project.save()

    if not AssignedUser.objects.filter(fullName=result.get('issue.fields.assignee.displayName')).exists():
        assigned_user = AssignedUserSerializer.create(fullName=result.get('issue.fields.assignee.displayName'), email=None)
        assigned_user.save()

    if not JiraTicket.objects.filter(ticket_key=result.get('issue.key')).exists():
        ticket = TicketSerializer.create(ticket_key=result.get('issue.key'), defaults=ticket_data)
        ticket.save()
    else:
        ticket = JiraTicket.objects.get(ticket_key=result.get('issue.key'))
        ticket_Serializer = TicketSerializer(ticket, data=ticket_data, partial=True)
        if ticket_Serializer.is_valid():
            ticket_Serializer.save()
        
    return Response(ticket , status=200)

    