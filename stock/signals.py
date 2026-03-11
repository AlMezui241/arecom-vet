from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F
from django.contrib.auth.models import User
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
    # ✅ FIX #4: Nettoyer avec le champ booléen au lieu du commentaire (robuste)
    MouvementStock.objects.filter(
        vet_reference=instance.vet,
        category=instance.categorie,
        est_automatique=True  # ← Plus fiable que commentaire__icontains
    ).delete()

    if instance.quantite > 0:
        # ✅ FIX #3: Créer utilisateur "system" pour les mouvements automatiques
        sys_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@arecom.local',
                'first_name': 'Système',
                'last_name': 'Automatique',
                'is_staff': False,
                'is_active': True
            }
        )

        MouvementStock.objects.create(
            category=instance.categorie,
            type_mouvement='sortie',
            quantite=instance.quantite,
            vet_reference=instance.vet,
            utilisateur=sys_user,  # ✅ FIX #3: Traçabilité via utilisateur système
            est_automatique=True,  # ✅ FIX #4: Marquer comme automatique
            commentaire=f"Sortie automatique (VET {instance.vet.numero_ordre_de_recette})"
        )

@receiver(post_delete, sender=VETVignette)
def update_stock_on_vetvignette_delete(sender, instance, **kwargs):
    """Nettoie les mouvements si l'assignation est supprimée."""
    # ✅ FIX #4: Nettoyer avec le champ booléen (robuste)
    MouvementStock.objects.filter(
        vet_reference=instance.vet,
        category=instance.categorie,
        est_automatique=True  # ← Plus fiable
    ).delete()

# --- Signaux pour VET (Nettoyage lors de la suppression) ---

@receiver(post_delete, sender=VET)
def restore_stock_on_vet_delete(sender, instance, **kwargs):
    """Les mouvements liés seront supprimés par CASCADE ou on les nettoie."""
    # ✅ FIX #4: Nettoyer avec le champ booléen (robuste)
    MouvementStock.objects.filter(
        vet_reference=instance,
        est_automatique=True  # ← Plus fiable
    ).delete()
