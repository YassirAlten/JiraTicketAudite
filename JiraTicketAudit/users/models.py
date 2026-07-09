from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


class JiraUser (models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, null = False , blank = False )
    jira_Key = models.TextField(max_length=100 , null = False , blank = False )

    def create(self, username, password, email=None, **kwargs):
        User = get_user_model()
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password
        )
        
        kwargs['user'] = user
        
        return super().create(**kwargs)



