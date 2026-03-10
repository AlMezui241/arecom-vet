from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, F

FRAIS_DOSSIER = Decimal("50000.00")

# Modèles de données
class VET(models.Model):
    """
    Représente un établissement assujetti à la redevance annuelle.
    Les montants sont stockés avec 2 décimales. Le champ
    `montant_total_a_recouvrer` est dérivé et maintenu à jour à chaque sauvegarde.
    """

    # Identifiants
    numero = models.AutoField(primary_key=True, verbose_name="N°")  # Clé primaire auto-incrémentée
    numero_ordre_de_recette = models.CharField(max_length=100, verbose_name="N° ORDRE DE RECETTE", unique=True)
    identification_de_l_exploitant_ou_raison_sociale = models.CharField(max_length=255, verbose_name="IDENTIFICATION DE L'EXPLOITANT OU RAISON SOCIALE")

    # Localisation
    region = models.CharField(max_length=100, verbose_name="REGION", db_index=True)  # Région administrative
    zone = models.CharField(max_length=100, verbose_name="ZONE", db_index=True)  # Zone/sous-division
    quartier = models.CharField(max_length=100, verbose_name="QUARTIER", db_index=True)  # Quartier/localité
    longitude = models.FloatField(verbose_name="Longitude", blank=True, null=True, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])  # Optionnel
    latitude = models.FloatField(verbose_name="Latitude", blank=True, null=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])  # Optionnel

    # Contact
    numero_de_telephone = models.CharField(
        max_length=20,
        verbose_name="NUMERO DE TELEPHONE",
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r"^\+?[0-9\s\-\(\)]{7,20}$", message="Format de numéro invalide")],
    )
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="EMAIL")

    # Redevance et recouvrement
    # Indique si les frais de dossier (fixés à 50 000) ont été payés
    frais_de_dossier_payes = models.BooleanField(default=False, verbose_name="FRAIS DE DOSSIER PAYÉS")
    
    # Indique si la redevance annuelle a été payée
    redevance_payee = models.BooleanField(default=False, verbose_name="REDEVANCE ANNUELLE PAYÉE")
    
    # Suivi du dossier
    dossier_suivi_par = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="DOSSIER SUIVI PAR"
    )
    
    # Les quantités de vignettes sont désormais gérées dynamiquement via VETVignette

    montant_de_la_redevance_annuelle = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="MONTANT DE LA REDEVANCE ANUELLE",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    date_d_emission_de_la_redevance_annuelle = models.DateField(verbose_name="DATE D'EMISSION DE LA REDEVANCE ANNUELLE", db_index=True)
    date_d_expiration_de_la_redevance_annuelle = models.DateField(verbose_name="DATE D'EXPIRATION DE LA REDEVANCE ANNUELLE", db_index=True)
    
    # Statut et journalisation
    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('inactif', 'Inactif')], default='actif', verbose_name="STATUT", db_index=True)
    notes = models.TextField(blank=True, null=True, verbose_name="NOTES")  # Remarques internes
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="DATE DE CRÉATION")  # Horodatage création
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="DATE DE MISE À JOUR")  # Horodatage MAJ
    
    class Meta:
        indexes = [
            models.Index(fields=["region", "zone", "quartier"]),
            models.Index(fields=["statut", "date_d_expiration_de_la_redevance_annuelle"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(date_d_expiration_de_la_redevance_annuelle__gte=F("date_d_emission_de_la_redevance_annuelle")),
                name="vet_expiration_gte_emission",
            ),
            models.CheckConstraint(
                condition=Q(montant_de_la_redevance_annuelle__gte=0),
                name="vet_montant_nonneg",
            ),
        ]
        ordering = ["-date_mise_a_jour"]
    
    def __str__(self):
        # Représentation courte et lisible dans l’admin et les logs
        return f"{self.numero} - {self.identification_de_l_exploitant_ou_raison_sociale}"
    
    @property
    def montant_total_a_recouvrer(self):
        """
        Calcul à la volée du montant total à recouvrer.
        Automatiquement mis à jour, pas de synchronisation nécessaire.

        Formule:
        montant_total = redevance_annuelle
                      + frais_dossier (50,000 si non payés)
                      + sum(vignettes assignées)
        """
        from django.db.models import F, Sum, DecimalField

        frais_dossier = (
            FRAIS_DOSSIER
            if not self.frais_de_dossier_payes
            else Decimal("0.00")
        )

        # Coût des vignettes via agrégation (pas de N+1 queries)
        total_vignettes = Decimal("0.00")
        if self.pk:
            agg_result = self.vignettes_assignees.aggregate(
                total=Sum(
                    F('quantite') * F('categorie__prix'),
                    output_field=DecimalField()
                )
            )
            total_vignettes = agg_result.get('total') or Decimal("0.00")

        return self.montant_de_la_redevance_annuelle + frais_dossier + total_vignettes

    def clean(self):
        super().clean()
        if (
            self.date_d_emission_de_la_redevance_annuelle
            and self.date_d_expiration_de_la_redevance_annuelle
            and self.date_d_expiration_de_la_redevance_annuelle < self.date_d_emission_de_la_redevance_annuelle
        ):
            raise ValidationError(
                {"date_d_expiration_de_la_redevance_annuelle": "La date d'expiration doit être postérieure ou égale à la date d'émission."}
            )

    def save(self, *args, **kwargs):
        # ✅ CORRECTION #1: Valider les données avant sauvegarde
        # Cela exécute le clean() et lève ValidationError si données invalides
        self.full_clean()
        super().save(*args, **kwargs)

class VETVignette(models.Model):
    vet = models.ForeignKey(VET, on_delete=models.CASCADE, related_name='vignettes_assignees')
    categorie = models.ForeignKey('stock.VignetteCategory', on_delete=models.CASCADE, verbose_name="Catégorie de Vignette")
    quantite = models.PositiveIntegerField(default=0, verbose_name="Quantité")

    class Meta:
        verbose_name = "Vignette assignée"
        verbose_name_plural = "Vignettes assignées"
        unique_together = ('vet', 'categorie')

    def __str__(self):
        return f"{self.vet.numero_ordre_de_recette} - {self.categorie} (x{self.quantite})"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
    ]
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    vet = models.ForeignKey(VET, on_delete=models.SET_NULL, null=True, verbose_name="VET")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    details = models.TextField(verbose_name="Détails des changements", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date/Heure")

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.action} par {self.user}"

class VETDocument(models.Model):
    DOCUMENT_TYPES = [
        ('photo', 'Photo / Image'),
        ('scan', 'Scan Document (PDF)'),
        ('other', 'Autre'),
    ]
    vet = models.ForeignKey(VET, on_delete=models.CASCADE, related_name='documents', verbose_name="Dossier VET")
    fichier = models.FileField(upload_to='vet_documents/%Y/%m/', verbose_name="Fichier")
    type_document = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='photo', verbose_name="Type")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")

    class Meta:
        verbose_name = "Document VET"
        verbose_name_plural = "Documents VET"
        ordering = ['-date_upload']

    def __str__(self):
        return f"Doc {self.type_document} pour {self.vet.numero}"
