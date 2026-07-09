from django.db import models
from users.models import JiraUser

class AssignedUser (models.Model):
    fullName = models.CharField(max_length=100, null=False, blank=False , unique=True)
    email = models.EmailField(max_length=100, null=True, blank=True)


class JiraTicket(models.Model):
    ticket_key = models.CharField(max_length=100, unique=True , null=False, blank=False) #the key is a mixed of sprint number and ticket number ex: SPRINT-1-SCRUM-1
    ticket_type = models.CharField(max_length=50, null=False, blank=False)
    summary = models.TextField(null=True, blank=True)
    estimated_time = models.CharField(max_length=100, null=True, blank=True)
    story_point=models.IntegerField(null=True , blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=False, blank=False)
    priority = models.CharField(max_length=50, null=False, blank=False)
    assigned_user = models.ForeignKey('AssignedUser', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=False, blank=False)
    start_date = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey('JiraProject', on_delete=models.CASCADE, null=False, blank=False)
    startingDate_priority_logical_relation_score = models.IntegerField(null=True, blank=True)
    description_quality_score = models.IntegerField(null=True, blank=True)
    summary_quality_score = models.IntegerField(null=True, blank=True)
    storyPoint_estimatedTime_logical_relation_score=models.IntegerField(null=True, blank=True)
    

class JiraProject(models.Model):
    project_name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    project_manager = models.ForeignKey(JiraUser, on_delete=models.CASCADE, null=True, blank=True)

class JiraTicketHistory(models.Model):
    ticket = models.ForeignKey(JiraTicket, on_delete=models.CASCADE, null=False, blank=False)
    managerScore = models.FloatField(null=True, blank=True)
    # modelScore = models.FloatField(null=False, blank=False)


class Coefficient(models.Model):
    project=models.ForeignKey('JiraProject',on_delete=models.CASCADE,null=False,blank=False)
    summary_coefficient=models.IntegerField(null=False,blank=False)
    description_coefficient=models.IntegerField(null=False,blank=False)
    priority_check_coefficient=models.IntegerField(null=False,blank=False)
    estimated_time_check_coeffichient=models.IntegerField(null=False,blank=False)



   



