from django.contrib import admin
from .models import VignetteCategory, MouvementStock

@admin.register(VignetteCategory)
class VignetteCategoryAdmin(admin.ModelAdmin):
    list_display = ('niveau', 'prix', 'stock_actuel', 'seuil_alerte', 'description')
    list_editable = ('seuil_alerte',)

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('date_mouvement', 'category', 'type_mouvement', 'quantite', 'utilisateur', 'vet_reference')
    list_filter = ('type_mouvement', 'category', 'date_mouvement')
    search_fields = ('commentaire', 'vet_reference__identification_de_l_exploitant_ou_raison_sociale')
