from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets
from .models import JiraProject, JiraTicket ,JiraTicketHistory,AssignedUser ,ConfigurationData,Coefficient
from .serializers import JiraTicketHistorySerializer, TicketSerializer, AssignedUserSerializer ,ProjectSerializer,ConfiguratinSerializer
import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema,OpenApiParameter
from users.models import JiraUser
from users.serializer import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import pandas as pd 
import joblib
from ml_engine.test_pipeline import preprocess_data_model1,preprocess_data_model3,preprocess_data_model5,preprocess_data_model6

requested_fields = ["webhookEvent", "issue.fields.customfield_10016","issue.fields.customfield_10015","issue.fields.issuetype.name","issue.key","issue.fields.summary","issue.fields.creator.displayName","issue.fields.created", "issue.fields.priority.name","issue.fields.duedate", "issue.fields.assignee.displayName","issue.fields.updated","issue.fields.description","issue.fields.status.name","issue.fields.project.name","changelog.items"]

class JiraTicketViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JiraTicket.objects.filter(project__project_manager=JiraUser.objects.get(user=self.request.user))
    serializer_class = TicketSerializer

class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ConfigurationData.objects.all()
    serializer_class = ConfiguratinSerializer


class HistoryViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return JiraTicketHistory.objects.filter(ticket__project__project_manager=JiraUser.objects.get(user=self.request.user))
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
            defaults={'project_manager': None }
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

@extend_schema(
    request=dict,
    responses={200: float},
    
)
@api_view(['POST'])
def predict_ticket_quality(request ):
    ticket=JiraTicket.objects.get(id=request.data.get('ticketId'))
    config = ConfigurationData.objects.get(coefficient__project=ticket.project)
    description_coefficent=Coefficient.objects.get(project=ticket.project).description_coefficient
    summary_coefficent=Coefficient.objects.get(project=ticket.project).summary_coefficient
    data={
        'description':ticket.description,
        'summary':ticket.summary,
        'ticket_type':ticket.ticket_type,
        'configuration_json':config.configuration_json
    }
    df1 = pd.DataFrame([data])
    df_model1=preprocess_data_model5(df1)
    print(df_model1)
    df_model2=preprocess_data_model3(df1)
    df_model3=preprocess_data_model1(df1)
    df_model4=preprocess_data_model6(df1)

    models_dir = os.path.join(settings.BASE_DIR, 'ml_engine', 'saved_models')

    # 2. Charger les modèles en utilisant le chemin absolu complet
    path1 = os.path.join(models_dir, 'text_quality_model6.joblib')
    model1 = joblib.load(path1)
    
    path2 = os.path.join(models_dir, 'text_quality_model7.joblib')
    model2 = joblib.load(path2)
    
    path3 = os.path.join(models_dir, 'text_quality_model8.joblib')
    model3 = joblib.load(path3)
    
    path4 = os.path.join(models_dir, 'text_quality_model9.joblib')
    model4 = joblib.load(path4)
    
    path5 = os.path.join(models_dir, 'vectorisor_model7.joblib')
    vectorisor1 = joblib.load(path5)
    
    path6 = os.path.join(models_dir, 'vectorisor_model9.joblib')
    vectorisor2 = joblib.load(path6)

    description_structural_prediction=float(model1.predict(df_model1)[0])
    print(description_structural_prediction)
    vectorised_df2=vectorisor1.transform(df_model2)
    description_content_prediction=float(model2.predict(vectorised_df2)[0])
    print(description_content_prediction)
    summary_structural_prediction= float(model3.predict(df_model3)[0])
    print(summary_structural_prediction)
    vectorised_df4=vectorisor2.transform(df_model4)
    summary_content_prediction= float(model4.predict(vectorised_df4)[0])
    print(summary_content_prediction)

    description_total_prediction= float(description_structural_prediction*0.5 + description_content_prediction*2.5)
    print(description_total_prediction)
    summary_total_prediction = float(summary_structural_prediction*0.5 +summary_content_prediction*2.5)
    print(summary_total_prediction)
    ticket_final_prediction =float((description_total_prediction*description_coefficent+summary_total_prediction*summary_coefficent)/(description_coefficent+summary_coefficent))
    print(ticket_final_prediction)
    return Response(ticket_final_prediction)
    