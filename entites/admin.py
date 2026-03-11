from django.contrib import admin
from .models import TypeEntite, Entite, EntiteDocument


@admin.register(TypeEntite)
class TypeEntiteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'a_frais_exploitation', 'a_contribution_fonds',
                    'a_renouvellement', 'actif']
    list_filter = ['actif', 'created_at']
    search_fields = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Entite)
class EntiteAdmin(admin.ModelAdmin):
    list_display = ['numero', 'type_entite', 'nom_entite', 'province', 'localite',
                    'montant_total_redevance', 'est_en_cours']
    list_filter = ['type_entite', 'province', 'localite', 'created_at', 'statut_autorisation']
    search_fields = ['numero', 'nom_entite', 'province', 'localite']
    readonly_fields = ['created_at', 'updated_at', 'montant_total_redevance']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identité', {
            'fields': ('type_entite', 'numero', 'nom_entite')
        }),
        ('Localisation', {
            'fields': ('province', 'localite', 'quartier_zone')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'email'),
            'classes': ('collapse',)
        }),
        ('GPS', {
            'fields': ('latitude', 'longitude', 'precision_gps'),
            'classes': ('collapse',)
        }),
        ('Autorisation', {
            'fields': ('statut_autorisation', 'date_attribution', 'date_renouvellement',
                      'date_expiration')
        }),
        ('Champs Financiers Optionnels', {
            'fields': ('frais_instruction_dossier', 'frais_exploitation_annuel',
                      'contribution_fonds_universel', 'montant_total_redevance'),
            'description': 'Certains champs peuvent être vides selon le type d\'entité'
        }),
        ('Notes', {
            'fields': ('observation',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        """Adaptation dynamique des onglets selon le type"""
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.type_entite:
            # Tous les champs financiers optionnels sont affichés
            # Voir les données pour savoir lesquels sont pertinents
            pass
        return fieldsets


@admin.register(EntiteDocument)
class EntiteDocumentAdmin(admin.ModelAdmin):
    list_display = ['entite', 'type_document', 'description', 'date_upload', 'uploaded_by']
    list_filter = ['type_document', 'date_upload', 'entite__type_entite']
    search_fields = ['entite__numero', 'entite__nom_entite', 'description']
    readonly_fields = ['date_upload']

