from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VETVignette
from stock.models import MouvementStock

@receiver(post_save, sender=VETVignette)
def create_stock_movement_on_save(sender, instance, created, **kwargs):
    """Crée automatiquement un mouvement de sortie de stock lors de l'assignation d'une vignette."""
    # ✅ FIX: On ne déduit du stock QUE si l'établissement ne possède pas déjà les vignettes (possede_vignettes=False)
    if created and instance.quantite > 0 and not instance.vet.possede_vignettes:
        MouvementStock.objects.create(
            category=instance.categorie,
            type_mouvement='sortie',
            quantite=instance.quantite,
            vet_reference=instance.vet,
            commentaire=f"Sortie automatique pour VET {instance.vet.numero_ordre_de_recette} (Besoin généré sur site)",
            est_automatique=True
        )

@receiver(post_delete, sender=VETVignette)
def delete_stock_movement_on_delete(sender, instance, **kwargs):
    """Supprime le mouvement de stock associé lors de la suppression d'une assignation de vignette."""
    MouvementStock.objects.filter(
        category=instance.categorie,
        type_mouvement='sortie',
        quantite=instance.quantite,
        vet_reference=instance.vet,
        est_automatique=True
    ).delete()
