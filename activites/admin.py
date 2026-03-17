from django.contrib import admin
from .models import TypeActivite, Activite, ActiviteDocument, ActiviteAuditLog


@admin.register(TypeActivite)
class TypeActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'a_frais_instruction', 'a_frais_exploitation', 'a_contribution_fonds', 'ordre', 'actif')
    list_editable = ('ordre', 'actif')
    prepopulated_fields = {'slug': ('nom',)}


# ✅ Inline formset pour documents (comme VETDocumentFormSet)
class ActiviteDocumentInline(admin.TabularInline):
    model = ActiviteDocument
    extra = 1
    fields = ['type_document', 'fichier', 'description', 'uploaded_by']
    readonly_fields = ['uploaded_by']


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nom_activite', 'type_activite', 'province', 'localite', 'statut', 'created_at')
    list_filter = ('type_activite', 'province', 'statut', 'frais_de_dossier_payes', 'redevance_payee')
    search_fields = ('numero', 'nom_activite', 'localite', 'quartier_zone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'created_by')

    fieldsets = (
        ('Identité', {
            'fields': ('type_activite', 'numero', 'nom_activite', 'statut')
        }),
        ('Localisation & Contact', {
            'fields': ('province', 'localite', 'quartier_zone', 'telephone', 'email')
        }),
        ('GPS', {
            'fields': ('latitude', 'longitude', 'precision_gps')
        }),
        ('Finances', {
            'fields': ('frais_instruction_dossier', 'frais_exploitation_annuel', 'contribution_fonds_universel',
                       'frais_de_dossier_payes', 'redevance_payee')
        }),
        ('Conformité', {
            'fields': ('presence_facture', 'presence_autorisation', 'presence_homologation')
        }),
        ('Autorisation', {
            'fields': ('statut_autorisation', 'contrepartie_financiere')
        }),
        ('Suivi & Audit', {
            'fields': ('dossier_suivi_par', 'observation', 'created_at', 'updated_at', 'created_by')
        }),
    )


@admin.register(ActiviteDocument)
class ActiviteDocumentAdmin(admin.ModelAdmin):
    list_display = ['activite', 'type_document', 'description', 'date_upload', 'uploaded_by']
    list_filter = ['type_document', 'date_upload', 'activite__type_activite']
    search_fields = ['activite__numero', 'activite__nom_activite', 'description']
    readonly_fields = ['date_upload']


@admin.register(ActiviteAuditLog)
class ActiviteAuditLogAdmin(admin.ModelAdmin):
    """✅ Journalisation des actions - inspiré de VET.AuditLog"""
    list_display = ['timestamp', 'activite', 'action', 'user']
    list_filter = ['action', 'timestamp', 'activite__type_activite']
    search_fields = ['activite__numero', 'activite__nom_activite', 'user__username', 'details']
    readonly_fields = ['timestamp', 'activite', 'user', 'action', 'details']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        """Empêcher l'ajout manuel - les logs sont créés par signaux"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Logs immuables"""
        return False