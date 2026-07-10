from rest_framework import viewsets
from .serializer import JiraUserSerializer
from .models import JiraUser

class UserView(viewsets.ModelViewSet):
    queryset=JiraUser.objects.all()
    serializer_class=JiraUserSerializer
    

