from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.models import F
from .models import MouvementStock, VignetteCategory
from .forms import StockEntryForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Vous n'avez pas les droits d'administration nécessaires.")

class StockStatusListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = VignetteCategory
    template_name = "stock/stock_status.html"
    context_object_name = "categories"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # On ajoute les alertes de stock bas
        context['low_stock_alerts'] = VignetteCategory.objects.filter(stock_actuel__lte=F('seuil_alerte'))
        return context

class StockMovementListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = MouvementStock
    template_name = "stock/stock_movement_list.html"
    context_object_name = "movements"
    paginate_by = 50

    def get_queryset(self):
        return MouvementStock.objects.all().select_related('category', 'utilisateur', 'vet_reference')

class StockEntryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = MouvementStock
    form_class = StockEntryForm
    template_name = "stock/stock_entry_form.html"
    success_url = reverse_lazy('stock:movement_list')

    def form_valid(self, form):
        form.instance.type_mouvement = 'entree'
        form.instance.utilisateur = self.request.user
        return super().form_valid(form)
