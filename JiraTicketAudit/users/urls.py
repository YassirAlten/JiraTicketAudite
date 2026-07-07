from django.urls import path
from .views import UserView

urlpatterns = [
    
    path('', UserView.as_view({'get': 'list', 'post': 'create'}), name='user'),
    path('<int:pk>/', UserView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='user-detail'),
]
