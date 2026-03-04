from django.urls import path
from .views import StockStatusListView, StockMovementListView, StockEntryCreateView

app_name = 'stock'

urlpatterns = [
    path('', StockStatusListView.as_view(), name='status'),
    path('movements/', StockMovementListView.as_view(), name='movement_list'),
    path('entry/', StockEntryCreateView.as_view(), name='stock_entry'),
]
