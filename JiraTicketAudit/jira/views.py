from django.shortcuts import render
from rest_framework import viewsets
from .models import JiraProject, JiraTicket ,JiraTicketHistory,AssignedUser
from .serializers import JiraTicketHistorySerializer, TicketSerializer, AssignedUserSerializer, ProjectSerializer

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