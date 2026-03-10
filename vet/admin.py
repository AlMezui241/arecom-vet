from django.contrib import admin
from .models import VET, VETVignette, AuditLog, VETDocument

class VETVignetteInline(admin.TabularInline):
    model = VETVignette
    extra = 1

class VETDocumentInline(admin.TabularInline):
    model = VETDocument
    extra = 1

@admin.register(VET)
class VETAdmin(admin.ModelAdmin):
    list_display = (
        'numero', 'numero_ordre_de_recette', 'identification_de_l_exploitant_ou_raison_sociale',
        'region', 'zone', 'quartier', 'numero_de_telephone',
        'frais_de_dossier_payes', 'redevance_payee', 'montant_de_la_redevance_annuelle', 'get_montant_total',
        'dossier_suivi_par',
        'date_d_emission_de_la_redevance_annuelle', 'date_d_expiration_de_la_redevance_annuelle',
        'statut'
    )
    search_fields = ('identification_de_l_exploitant_ou_raison_sociale', 'numero_ordre_de_recette', 'dossier_suivi_par')
    list_filter = ('region', 'zone', 'statut', 'frais_de_dossier_payes', 'redevance_payee', 'dossier_suivi_par')
    inlines = [VETVignetteInline, VETDocumentInline]

    def get_montant_total(self, obj):
        """Affiche le montant total calculé (property) en read-only"""
        return f"{obj.montant_total_a_recouvrer:.2f} FCFA"
    get_montant_total.short_description = "Montant Total à Recouvrer"

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'vet', 'action')
    list_filter = ('action', 'user')
    readonly_fields = ('timestamp', 'user', 'vet', 'action', 'details')
