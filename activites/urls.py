from django.urls import path
from . import views

app_name = 'activites'

urlpatterns = [
    path('', views.ActiviteListView.as_view(), name='list'),
    path('dashboard/', views.activites_dashboard, name='dashboard'),
    path('nouveau/', views.ActiviteCreateView.as_view(), name='create'),
    path('map/', views.ActiviteMapView.as_view(), name='map'),
    path('export/excel/', views.ExportActiviteExcelListView.as_view(), name='export_excel'),
    path('export/csv/', views.ExportActiviteCSVView.as_view(), name='export_csv'),
    path('<slug:numero>/', views.ActiviteDetailView.as_view(), name='detail'),
    path('<slug:numero>/pdf/', views.ExportActivitePDFView.as_view(), name='pdf'),
    path('<slug:numero>/modifier/', views.ActiviteUpdateView.as_view(), name='update'),
]
