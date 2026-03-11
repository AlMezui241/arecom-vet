from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from django.contrib.auth.models import User


class TypeEntite(models.Model):
    """Catalogue des types d'entités - extensible sans code!"""
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)

    # Configuration des champs (ce type a-t-il ces champs?)
    a_frais_exploitation = models.BooleanField(default=False,
        help_text="Ce type a-t-il les frais annuels d'exploitation?")
    a_contribution_fonds = models.BooleanField(default=False,
        help_text="Ce type a-t-il la contribution annuelle au fonds universel?")
    a_renouvellement = models.BooleanField(default=False,
        help_text="Ce type a-t-il un renouvellement d'autorisation?")
    a_frais_instruction = models.BooleanField(default=True,
        help_text="Ce type a-t-il des frais d'instruction de dossier?")

    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Type d'entité"
        verbose_name_plural = "Types d'entités"

    def __str__(self):
        return self.nom


class Entite(models.Model):
    """Modèle générique pour TOUS les types d'entités - data-driven!"""

    # Identité
    type_entite = models.ForeignKey(TypeEntite, on_delete=models.PROTECT,
                                     related_name='entites')
    numero = models.CharField(max_length=50, unique=True, db_index=True)
    nom_entite = models.CharField(max_length=255, verbose_name="Nom / Raison Sociale")

    # Localisation
    province = models.CharField(max_length=100, db_index=True)
    localite = models.CharField(max_length=100, db_index=True)
    quartier_zone = models.CharField(max_length=255, db_index=True)

    # Coordonnées
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # GPS
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))]
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))]
    )
    precision_gps = models.CharField(max_length=50, default='Précision inconnue')

    # Champs financiers OPTIONNELS (selon TypeEntite)
    frais_instruction_dossier = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Frais d'instruction de dossier"
    )
    frais_exploitation_annuel = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Frais annuel d'exploitation (redevance annuelle)"
    )
    contribution_fonds_universel = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Contribution annuelle au fonds du service universel"
    )

    # Autorisation
    STATUT_CHOICES = [
        ('attribution', 'Attribution'),
        ('renouvellement', 'Renouvellement'),
        ('suspendue', 'Suspendue'),
        ('terminee', 'Terminée'),
    ]
    statut_autorisation = models.CharField(max_length=20, choices=STATUT_CHOICES,
                                            default='attribution')
    date_attribution = models.DateField(null=True, blank=True)
    date_renouvellement = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)

    # Notes
    observation = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='entites_creees')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type_entite', 'numero']),
            models.Index(fields=['province', 'localite']),
        ]
        verbose_name = "Entité"
        verbose_name_plural = "Entités"

    def __str__(self):
        return f"{self.type_entite.nom} - {self.numero}: {self.nom_entite}"

    def clean(self):
        """Validation DYNAMIQUE basée sur TypeEntite"""
        from django.core.exceptions import ValidationError
        errors = {}

        # Validation GPS
        if (self.latitude is not None) != (self.longitude is not None):
            errors['longitude'] = "Latitude et longitude doivent être fournies ensemble"

        # Validations conditionnelles
        if self.type_entite.a_frais_exploitation and not self.frais_exploitation_annuel:
            errors['frais_exploitation_annuel'] = "Requis pour ce type"

        if self.type_entite.a_contribution_fonds and not self.contribution_fonds_universel:
            errors['contribution_fonds_universel'] = "Requis pour ce type"

        if self.type_entite.a_renouvellement and not self.date_renouvellement:
            errors['date_renouvellement'] = "Requis pour ce type"

        if self.type_entite.a_frais_instruction and not self.frais_instruction_dossier:
            errors['frais_instruction_dossier'] = "Requis pour ce type"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def montant_total_redevance(self):
        """Total redevances annuelles"""
        total = Decimal('0.00')
        if self.frais_exploitation_annuel:
            total += self.frais_exploitation_annuel
        if self.contribution_fonds_universel:
            total += self.contribution_fonds_universel
        return total

    @property
    def est_en_cours(self):
        """Vérifier si l'autorisation est valide"""
        from django.utils import timezone
        if self.date_expiration:
            return self.date_expiration >= timezone.now().date()
        return True


class EntiteDocument(models.Model):
    """Documents attachés aux entités"""
    TYPES_DOCUMENT = [
        ('autorisation', 'Autorisation'),
        ('renouvellement', 'Renouvellement'),
        ('rapport', 'Rapport'),
        ('autre', 'Autre'),
    ]

    entite = models.ForeignKey(Entite, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=20, choices=TYPES_DOCUMENT)
    fichier = models.FileField(
        upload_to='entites/documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'])]
    )
    description = models.CharField(max_length=255, blank=True)
    date_upload = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date_upload']
        verbose_name = "Document d'entité"
        verbose_name_plural = "Documents d'entité"

    def __str__(self):
        return f"{self.entite.numero} - {self.type_document}"
