from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from django.contrib.auth.models import User
from django.utils import timezone


class TypeActivite(models.Model):
    """Catalogue des types d'activités - extensible sans code!"""
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
    a_frais_instruction = models.BooleanField(default=False,
        help_text="Ce type a-t-il des frais d'instruction de dossier?")

    ordre = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Type d'activité"
        verbose_name_plural = "Types d'activités"

    def __str__(self):
        return self.nom


class Activite(models.Model):
    """Modèle générique pour TOUS les types d'activités - data-driven!"""

    # Identité
    type_activite = models.ForeignKey(TypeActivite, on_delete=models.PROTECT,
                                     related_name='activites')
    numero = models.CharField(max_length=50, unique=True, db_index=True)
    nom_activite = models.CharField(max_length=255, verbose_name="Nom / Raison Sociale")

    # Localisation
    province = models.CharField(max_length=100, db_index=True)
    localite = models.CharField(max_length=100, db_index=True)
    quartier_zone = models.CharField(max_length=255, db_index=True)

    # Coordonnées
    telephone = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(
            regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
            message="Format de numéro invalide"
        )],
        help_text="Format: +243123456789 ou (243) 123-456789"
    )
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

    # Champs financiers OPTIONNELS (selon TypeActivite)
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

    # Paiements (comme VET)
    frais_de_dossier_payes = models.BooleanField(default=False,
        verbose_name="Frais de dossier payés")
    redevance_payee = models.BooleanField(default=False,
        verbose_name="Redevance annuelle payée")

    # Suivi du dossier
    dossier_suivi_par = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Dossier suivi par"
    )

    # Nouveaux champs de conformité (Identiques à VET)
    presence_facture = models.BooleanField(default=False, verbose_name="Facture présente ?")
    presence_autorisation = models.BooleanField(default=False, verbose_name="Autorisation présente ?")
    presence_homologation = models.BooleanField(default=False, verbose_name="Homologation présente ?")

    # Statut global
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
        ('termine', 'Terminé'),
    ]
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='actif',
        db_index=True
    )

    # Dates d'émission/expiration (pour calcul redevances)
    date_emission_redevance = models.DateField(null=True, blank=True,
        verbose_name="Date d'émission de la redevance", db_index=True,
        help_text="Date à laquelle la redevance annuelle a été facturée.")
    date_expiration_redevance = models.DateField(null=True, blank=True,
        verbose_name="Date d'expiration de la redevance", db_index=True,
        help_text="Date à laquelle la redevance annuelle expire.")

    # Autorisation
    STATUT_AUTORISATION_CHOICES = [
        ('attribution', 'Attribution'),
        ('renouvellement', 'Renouvellement'),
        ('suspendue', 'Suspendue'),
        ('terminee', 'Terminée'),
    ]
    statut_autorisation = models.CharField(
        max_length=20,
        choices=STATUT_AUTORISATION_CHOICES,
        default='attribution',
    )
    contrepartie_financiere = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Contrepartie financière associée à l'autorisation (valeur constante définie par le régulateur).",
    )

    # Notes
    observation = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='activites_creees')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type_activite', 'numero']),
            models.Index(fields=['province', 'localite']),
        ]
        verbose_name = "Activité"
        verbose_name_plural = "Activités"

    def __str__(self):
        return f"{self.type_activite.nom} - {self.numero}: {self.nom_activite}"

    def clean(self):
        """Validation DYNAMIQUE basée sur TypeActivite + validations métier comme VET"""
        from django.core.exceptions import ValidationError
        errors = {}

        # Validation GPS
        if (self.latitude is not None) != (self.longitude is not None):
            errors['longitude'] = "Latitude et longitude doivent être fournies ensemble"

        # Validation dates (expiration >= emission)
        if self.date_emission_redevance and self.date_expiration_redevance:
            if self.date_expiration_redevance < self.date_emission_redevance:
                errors['date_expiration_redevance'] = "La date d'expiration de la redevance doit être postérieure ou égale à la date d'émission."

        # Validations conditionnelles par type
        if self.type_activite.a_frais_exploitation and not self.frais_exploitation_annuel:
            errors['frais_exploitation_annuel'] = "Requis pour ce type"

        if self.type_activite.a_contribution_fonds and not self.contribution_fonds_universel:
            errors['contribution_fonds_universel'] = "Requis pour ce type"



        if self.type_activite.a_frais_instruction and not self.frais_instruction_dossier:
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
        if self.frais_instruction_dossier:
            total += self.frais_instruction_dossier
        if self.frais_exploitation_annuel:
            total += self.frais_exploitation_annuel
        if self.contribution_fonds_universel:
            total += self.contribution_fonds_universel
        return total

    @property
    def est_en_cours(self):
        """Vérifier si l'autorisation est valide en se basant sur sa date de fin."""
        from django.utils import timezone
        if self.date_fin_autorisation:
            return self.date_fin_autorisation >= timezone.now().date()
        return True


class ActiviteDocument(models.Model):
    """Documents attachés aux activités"""
    TYPES_DOCUMENT = [
        ('autorisation', 'Autorisation'),
        ('renouvellement', 'Renouvellement'),
        ('rapport', 'Rapport'),
        ('autre', 'Autre'),
    ]

    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=20, choices=TYPES_DOCUMENT)
    fichier = models.FileField(
        upload_to='activites/documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'])]
    )
    description = models.CharField(max_length=255, blank=True)
    date_upload = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date_upload']
        verbose_name = "Document d'activité"
        verbose_name_plural = "Documents d'activité"

    def __str__(self):
        return f"{self.activite.numero} - {self.type_document}"


class ActiviteAuditLog(models.Model):
    """Journalisation des actions sur les activités (CREATE/UPDATE/DELETE)"""
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('payment', 'Paiement'),
    ]

    activite = models.ForeignKey(Activite, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    details = models.TextField(verbose_name="Détails des changements", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Date/Heure")

    class Meta:
        verbose_name = "Journal d'audit (Activité)"
        verbose_name_plural = "Journaux d'audit (Activité)"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['activite', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.action} par {self.user}"
