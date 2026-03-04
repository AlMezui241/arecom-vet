from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from vet.models import VET

class VignetteCategory(models.Model):
    niveau = models.IntegerField(unique=True, verbose_name="Niveau")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (FCFA)")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description / Équipement")
    stock_actuel = models.PositiveIntegerField(default=0, verbose_name="Stock Actuel")
    seuil_alerte = models.PositiveIntegerField(default=10, verbose_name="Seuil d'Alerte")

    def __str__(self):
        return f"Niveau {self.niveau} ({self.prix} F)"

    class Meta:
        verbose_name = "Catégorie de Vignette"
        verbose_name_plural = "Catégories de Vignettes"
        ordering = ['niveau']

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée (Achat/Approvisionnement)'),
        ('sortie', 'Sortie (Utilisation VET)'),
        ('ajustement', 'Ajustement (Inventaire/Correction)'),
    ]

    category = models.ForeignKey(VignetteCategory, on_delete=models.CASCADE, related_name='mouvements', verbose_name="Catégorie")
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de Mouvement")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    vet_reference = models.ForeignKey(VET, on_delete=models.SET_NULL, null=True, blank=True, related_name='mouvements_vignettes', verbose_name="Référence VET")
    commentaire = models.TextField(blank=True, verbose_name="Commentaires")

    def __str__(self):
        return f"{self.type_mouvement.capitalize()} - {self.category.niveau} - {self.quantite}"

    class Meta:
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        ordering = ['-date_mouvement']
