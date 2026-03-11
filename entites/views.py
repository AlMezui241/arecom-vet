from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from .models import Entite, TypeEntite, EntiteDocument


class EntiteListView(LoginRequiredMixin, ListView):
    """Liste toutes les entités avec filtrage"""
    model = Entite
    template_name = 'entites/entite_list.html'
    context_object_name = 'entites'
    paginate_by = 25

    def get_queryset(self):
        queryset = Entite.objects.select_related('type_entite').all()

        # Filtrer par type si spécifié
        type_slug = self.request.GET.get('type')
        if type_slug:
            queryset = queryset.filter(type_entite__slug=type_slug)

        # Filtrer par province
        province = self.request.GET.get('province')
        if province:
            queryset = queryset.filter(province=province)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = TypeEntite.objects.filter(actif=True)
        context['provinces'] = Entite.objects.values_list('province', flat=True).distinct()
        return context


class EntiteDetailView(LoginRequiredMixin, DetailView):
    """Détail d'une entité"""
    model = Entite
    template_name = 'entites/entite_detail.html'
    context_object_name = 'entite'
    slug_field = 'numero'
    slug_url_kwarg = 'numero'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entite = self.get_object()
        context['documents'] = entite.documents.all()
        return context


class EntiteCreateView(LoginRequiredMixin, CreateView):
    """Créer une nouvelle entité"""
    model = Entite
    template_name = 'entites/entite_form.html'
    fields = ['type_entite', 'numero', 'nom_entite', 'province',
              'localite', 'quartier_zone', 'telephone', 'email', 'latitude',
              'longitude', 'precision_gps', 'frais_instruction_dossier',
              'frais_exploitation_annuel', 'contribution_fonds_universel',
              'statut_autorisation', 'date_attribution', 'date_renouvellement',
              'date_expiration', 'observation']
    success_url = reverse_lazy('entites:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EntiteUpdateView(LoginRequiredMixin, UpdateView):
    """Modifier une entité"""
    model = Entite
    template_name = 'entites/entite_form.html'
    fields = ['type_entite', 'numero', 'nom_entite', 'province',
              'localite', 'quartier_zone', 'telephone', 'email', 'latitude',
              'longitude', 'precision_gps', 'frais_instruction_dossier',
              'frais_exploitation_annuel', 'contribution_fonds_universel',
              'statut_autorisation', 'date_attribution', 'date_renouvellement',
              'date_expiration', 'observation']
    slug_field = 'numero'
    slug_url_kwarg = 'numero'
    success_url = reverse_lazy('entites:list')


def entites_dashboard(request):
    """Dashboard global des entités"""
    if not request.user.is_authenticated:
        return redirect('admin:login')

    stats = {
        'total_entites': Entite.objects.count(),
        'par_type': {},
        'par_province': {},
        'total_redevances': Decimal('0.00'),
    }

    # Stats par type
    for type_entite in TypeEntite.objects.filter(actif=True):
        entites_type = Entite.objects.filter(type_entite=type_entite)
        stats['par_type'][type_entite.nom] = {
            'count': entites_type.count(),
            'redevances': entites_type.aggregate(
                Sum('frais_exploitation_annuel'))['frais_exploitation_annuel__sum'] or Decimal('0.00')
        }

    # Stats par province
    for province in Entite.objects.values_list('province', flat=True).distinct():
        entites_province = Entite.objects.filter(province=province)
        stats['par_province'][province] = entites_province.count()

    # Total redevances
    stats['total_redevances'] = Entite.objects.aggregate(
        total=Sum('frais_exploitation_annuel'))['total'] or Decimal('0.00')

    return render(request, 'entites/dashboard.html', {'stats': stats})

