from django.db import models
from users.models import JiraUser

class AssignedUser (models.Model):
    fullName = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)


class JiraTicket(models.Model):
    ticket_key = models.CharField(max_length=100, unique=True , null=False, blank=False) #the key is a mixed of sprint number and ticket number ex: SPRINT-1-SCRUM-1
    ticket_type = models.CharField(max_length=50, null=False, blank=False)
    summary = models.TextField(null=True, blank=True)
    estimated_time = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=False, blank=False)
    priority = models.CharField(max_length=50, null=False, blank=False)
    assigned_user = models.OneToOneField(AssignedUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=False, blank=False)
    project = models.ForeignKey('JiraProject', on_delete=models.CASCADE, null=False, blank=False)

class JiraProject(models.Model):
    project_name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    project_manager = models.ForeignKey(JiraUser, on_delete=models.CASCADE, null=True, blank=True)

class JiraTicketHistory(models.Model):
    ticket = models.ForeignKey(JiraTicket, on_delete=models.CASCADE, null=False, blank=False)
    managerScore = models.FloatField(null=True, blank=True)
    # modelScore = models.FloatField(null=False, blank=False)



