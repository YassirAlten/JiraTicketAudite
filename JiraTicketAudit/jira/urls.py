from django.urls import path
from .views import JiraTicketViewSet , HistoryViewSet , ProjectViewSet , AssignedUserViewSet , extractDataFromJson,ConfigurationViewSet
from jira import views

urlpatterns = [
    path('', JiraTicketViewSet.as_view({'get': 'list', 'post': 'create'}), name='ticket'),
    path('<int:pk>/', JiraTicketViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='ticket-detail'),
    path('history/', HistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='history'),
    path('history/<int:pk>/', HistoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='history-detail'),
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-detail'),
    path('assigned_users/', AssignedUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user'),
    path('Configuration/', ConfigurationViewSet.as_view({'get': 'list','post': 'create'}), name='configuration'),
    path('Configuration/<int:pk>/', ConfigurationViewSet.as_view({'get': 'retrieve','put': 'update', 'delete': 'destroy'}), name='configuration-details'),
    path('assigned_users/<int:pk>/', AssignedUserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='user-detail'),
    path('extract/', views.extractDataFromJson, name='extract-data'),

]