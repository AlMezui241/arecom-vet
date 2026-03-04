from django.urls import path
from .views import (
    VETListView,
    VETDetailView,
    VETCreateView,
    VETUpdateView,
    VETDeleteView,
    VETMapView,
    ExportVETCSVView,
    ExportVETPDFView,
    ExportVETPDFListView,
    ExportVETExcelListView,
    ExportVETExcelDetailView,
)

app_name = "vet"

urlpatterns = [
    path("", VETListView.as_view(), name="vet_list"),
    path("new/", VETCreateView.as_view(), name="vet_create"),
    path("<int:pk>/", VETDetailView.as_view(), name="vet_detail"),
    path("<int:pk>/edit/", VETUpdateView.as_view(), name="vet_update"),
    path("<int:pk>/delete/", VETDeleteView.as_view(), name="vet_delete"),
    path("<int:pk>/pdf/", ExportVETPDFView.as_view(), name="vet_pdf"),
    path("<int:pk>/excel/", ExportVETExcelDetailView.as_view(), name="vet_excel_detail"),
    path("map/", VETMapView.as_view(), name="vet_map"),
    path("export/csv/", ExportVETCSVView.as_view(), name="vet_export_csv"),
    path("export/pdf/", ExportVETPDFListView.as_view(), name="vet_export_pdf"),
    path("export/excel/", ExportVETExcelListView.as_view(), name="vet_export_excel"),
]
