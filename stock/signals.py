from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import F
from .models import MouvementStock, VignetteCategory

@receiver(post_save, sender=MouvementStock)
def update_stock_on_save(sender, instance, created, **kwargs):
    """Met à jour le stock actuel de la catégorie lors de la création d'un mouvement."""
    if created:
        category = instance.category
        if instance.type_mouvement == 'entree':
            category.stock_actuel = F('stock_actuel') + instance.quantite
        elif instance.type_mouvement == 'sortie':
            category.stock_actuel = F('stock_actuel') - instance.quantite
        elif instance.type_mouvement == 'ajustement':
            # Pour l'ajustement, on peut supposer que quantite est la nouvelle valeur
            # ou une différence. Ici, on va supposer une différence (positive ou négative).
            category.stock_actuel = F('stock_actuel') + instance.quantite
        category.save(update_fields=['stock_actuel'])

@receiver(post_delete, sender=MouvementStock)
def update_stock_on_delete(sender, instance, **kwargs):
    """Rétablit le stock lors de la suppression d'un mouvement."""
    category = instance.category
    if instance.type_mouvement == 'entree':
        category.stock_actuel = F('stock_actuel') - instance.quantite
    elif instance.type_mouvement == 'sortie':
        category.stock_actuel = F('stock_actuel') + instance.quantite
    elif instance.type_mouvement == 'ajustement':
        category.stock_actuel = F('stock_actuel') - instance.quantite
    category.save(update_fields=['stock_actuel'])

@receiver(post_save, sender=MouvementStock)
def check_stock_level(sender, instance, **kwargs):
    """Envoie une alerte email si le stock tombe sous le seuil."""
    category = instance.category
    category.refresh_from_db() # Nécessaire car on a utilisé F()
    if category.stock_actuel <= category.seuil_alerte:
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            if admin.email:
                send_mail(
                    'Alerte de stock bas',
                    f'Le stock pour la catégorie "{category.description}" est bas : {category.stock_actuel} unités restantes.',
                    'noreply@arecom.com',
                    [admin.email],
                    fail_silently=False,
                )
