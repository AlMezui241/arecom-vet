from django.contrib import admin
from .models import VET, VETVignette, AuditLog

class VETVignetteInline(admin.TabularInline):
    model = VETVignette
    extra = 1

@admin.register(VET)
class VETAdmin(admin.ModelAdmin):
    list_display = (
        'numero', 'numero_ordre_de_recette', 'identification_de_l_exploitant_ou_raison_sociale',
        'region', 'zone', 'quartier', 'numero_de_telephone',
        'frais_de_dossier_payes', 'redevance_payee', 'montant_de_la_redevance_annuelle', 'montant_total_a_recouvrer',
        'dossier_suivi_par',
        'date_d_emission_de_la_redevance_annuelle', 'date_d_expiration_de_la_redevance_annuelle',
        'statut'
    )
    search_fields = ('identification_de_l_exploitant_ou_raison_sociale', 'numero_ordre_de_recette', 'dossier_suivi_par')
    list_filter = ('region', 'zone', 'statut', 'frais_de_dossier_payes', 'redevance_payee', 'dossier_suivi_par')
    inlines = [VETVignetteInline]

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'vet', 'action')
    list_filter = ('action', 'user')
    readonly_fields = ('timestamp', 'user', 'vet', 'action', 'details')
