from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from .models import TypeActivite, Activite

class ActiviteModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.type_activite = TypeActivite.objects.create(nom='Test Type', slug='test-type')

    def test_creer_activite(self):
        activite = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-001',
            nom_activite='Test Activite',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            created_by=self.user
        )
        self.assertEqual(activite.nom_activite, 'Test Activite')

    def test_validation_dates_redevance(self):
        with self.assertRaises(ValidationError):
            Activite.objects.create(
                type_activite=self.type_activite,
                numero='TEST-002',
                nom_activite='Test Activite 2',
                province='Test Province',
                localite='Test Localite',
                quartier_zone='Test Zone',
                date_emission_redevance=date.today(),
                date_expiration_redevance=date.today() - timedelta(days=1),
                created_by=self.user
            )

    def test_validation_dates_autorisation(self):
        # Les dates d'autorisation ont été supprimées, ce test doit être mis à jour ou supprimé
        # On teste ici la validation globale de clean()
        activite = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-003',
            nom_activite='Test Activite 3',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            created_by=self.user
        )
        activite.clean() # Ne devrait pas lever d'erreur

    def test_montant_total_redevance(self):
        activite = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-004',
            nom_activite='Test Activite 4',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            frais_instruction_dossier=Decimal('1000'),
            frais_exploitation_annuel=Decimal('2000'),
            contribution_fonds_universel=Decimal('3000'),
            created_by=self.user
        )
        self.assertEqual(activite.montant_total_redevance, Decimal('6000'))

    def test_est_en_cours(self):
        # Les dates d'autorisation ont été supprimées, on s'appuie sur les statuts.
        activite_en_cours = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-005',
            nom_activite='Test Activite 5',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            statut='actif',
            created_by=self.user
        )
        self.assertTrue(activite_en_cours.est_en_cours)

        activite_expiree = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-006',
            nom_activite='Test Activite 6',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            statut='termine',
            created_by=self.user
        )
        self.assertFalse(activite_expiree.est_en_cours)

        activite_suspendue = Activite.objects.create(
            type_activite=self.type_activite,
            numero='TEST-007',
            nom_activite='Test Activite 7',
            province='Test Province',
            localite='Test Localite',
            quartier_zone='Test Zone',
            statut='actif',
            statut_autorisation='suspendue',
            created_by=self.user
        )
        self.assertFalse(activite_suspendue.est_en_cours)
