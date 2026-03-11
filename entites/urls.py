from django.urls import path
from . import views

app_name = 'entites'

urlpatterns = [
    path('', views.EntiteListView.as_view(), name='list'),
    path('dashboard/', views.entites_dashboard, name='dashboard'),
    path('nouveau/', views.EntiteCreateView.as_view(), name='create'),
    path('<slug:numero>/', views.EntiteDetailView.as_view(), name='detail'),
    path('<slug:numero>/modifier/', views.EntiteUpdateView.as_view(), name='update'),
]
