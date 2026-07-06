from rest_framework.views import APIView
from .serializer import UserSerializer
from .models import JiraUser

class UserView(APIView):
    queryset=JiraUser.objects.all()
    serializer_class=UserSerializer
    

