from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F
from vet.models import VET, VETVignette
from .models import VignetteCategory, MouvementStock

# --- Signaux pour MouvementStock (Mise à jour automatique de VignetteCategory) ---

@receiver(post_save, sender=MouvementStock)
def update_category_stock_on_save(sender, instance, created, **kwargs):
    """Met à jour le stock actuel de la catégorie lors de la création d'un mouvement."""
    if created:
        if instance.type_mouvement == 'entree':
            VignetteCategory.objects.filter(pk=instance.category.pk).update(stock_actuel=F('stock_actuel') + instance.quantite)
        else:
            VignetteCategory.objects.filter(pk=instance.category.pk).update(stock_actuel=F('stock_actuel') - instance.quantite)

@receiver(post_delete, sender=MouvementStock)
def update_category_stock_on_delete(sender, instance, **kwargs):
    """Rétablit le stock lors de la suppression d'un mouvement."""
    if instance.type_mouvement == 'entree':
        VignetteCategory.objects.filter(pk=instance.category.pk).update(stock_actuel=F('stock_actuel') - instance.quantite)
    else:
        VignetteCategory.objects.filter(pk=instance.category.pk).update(stock_actuel=F('stock_actuel') + instance.quantite)

# --- Signaux pour VETVignette (Automatisation des mouvements de stock) ---

@receiver(post_save, sender=VETVignette)
def update_stock_on_vetvignette_save(sender, instance, created, **kwargs):
    """
    Lorsqu'une vignette est assignée ou modifiée sur un VET, on ajuste le stock.
    """
    # On nettoie les anciens mouvements automatiques pour ce VET et cette catégorie
    MouvementStock.objects.filter(
        vet_reference=instance.vet, 
        category=instance.categorie,
        commentaire__icontains="automatique"
    ).delete()
    
    if instance.quantite > 0:
        MouvementStock.objects.create(
            category=instance.categorie,
            type_mouvement='sortie',
            quantite=instance.quantite,
            vet_reference=instance.vet,
            commentaire=f"Sortie automatique (VET {instance.vet.numero_ordre_de_recette})"
        )

@receiver(post_delete, sender=VETVignette)
def update_stock_on_vetvignette_delete(sender, instance, **kwargs):
    """Nettoie les mouvements si l'assignation est supprimée."""
    MouvementStock.objects.filter(
        vet_reference=instance.vet, 
        category=instance.categorie,
        commentaire__icontains="automatique"
    ).delete()

# --- Signaux pour VET (Nettoyage lors de la suppression) ---

@receiver(post_delete, sender=VET)
def restore_stock_on_vet_delete(sender, instance, **kwargs):
    """Les mouvements liés seront supprimés par CASCADE ou on les nettoie."""
    MouvementStock.objects.filter(vet_reference=instance, commentaire__icontains="automatique").delete()
