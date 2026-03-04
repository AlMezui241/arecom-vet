from django.test import TestCase
from django.contrib.auth.models import User
from .models import VET, VETVignette, FRAIS_DOSSIER
from stock.models import VignetteCategory, MouvementStock
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class VETModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testagent', password='password')
        self.category = VignetteCategory.objects.create(
            niveau=1,
            prix=Decimal("250.00"),
            stock_actuel=100
        )
        self.vet = VET.objects.create(
            numero_ordre_de_recette="VET-001",
            identification_de_l_exploitant_ou_raison_sociale="Boutique Test",
            region="Estuaire",
            zone="Libreville",
            quartier="Akanda",
            montant_de_la_redevance_annuelle=Decimal("100000.00"),
            date_d_emission_de_la_redevance_annuelle=timezone.now().date(),
            date_d_expiration_de_la_redevance_annuelle=timezone.now().date() + timedelta(days=365)
        )

    def test_vet_creation_and_calculation(self):
        """Vérifie le calcul du montant total à recouvrer (redevance + frais dossier)."""
        # Par défaut, frais de dossier non payés
        self.assertEqual(self.vet.montant_total_a_recouvrer, Decimal("100000.00") + FRAIS_DOSSIER)

    def test_vet_with_vignettes_calculation(self):
        """Vérifie le calcul avec vignettes assignées."""
        VETVignette.objects.create(vet=self.vet, categorie=self.category, quantite=10)
        # On force le save du VET car le signal VETVignette.post_save ne met pas à jour le montant du VET automatiquement
        # dans les tests sans save explicite ou signal retour
        self.vet.save()
        
        expected_total = Decimal("100000.00") + FRAIS_DOSSIER + (Decimal("250.00") * 10)
        self.assertEqual(self.vet.montant_total_a_recouvrer, expected_total)

    def test_vetvignette_updates_stock_signal(self):
        """Vérifie que l'assignation d'une vignette à un VET réduit le stock."""
        initial_stock = self.category.stock_actuel
        VETVignette.objects.create(vet=self.vet, categorie=self.category, quantite=5)
        
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, initial_stock - 5)
        
        # Vérifie qu'un mouvement automatique a été créé
        self.assertTrue(MouvementStock.objects.filter(vet_reference=self.vet, category=self.category).exists())

    def test_vetvignette_delete_cleans_stock_signal(self):
        """Vérifie que la suppression d'une assignation nettoie les mouvements."""
        vv = VETVignette.objects.create(vet=self.vet, categorie=self.category, quantite=5)
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 95)
        
        vv.delete()
        # Le signal de suppression de VETVignette supprime le mouvement de sortie
        # Le signal de suppression de MouvementStock rétablit le stock
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 100)

from django.urls import reverse

class VETViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')
        self.category = VignetteCategory.objects.create(niveau=1, prix=Decimal("250.00"), stock_actuel=100)
        self.vet = VET.objects.create(
            numero_ordre_de_recette="VET-002",
            identification_de_l_exploitant_ou_raison_sociale="Boutique View Test",
            region="Estuaire", zone="Libreville", quartier="Centre",
            montant_de_la_redevance_annuelle=Decimal("50000.00"),
            date_d_emission_de_la_redevance_annuelle=timezone.now().date(),
            date_d_expiration_de_la_redevance_annuelle=timezone.now().date() + timedelta(days=365)
        )

    def test_home_view(self):
        """Vérifie que la page d'accueil s'affiche et contient les KPIs."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de bord")
        self.assertIn('total_vet', response.context)

    def test_vet_list_view(self):
        """Vérifie l'affichage de la liste des VET."""
        response = self.client.get(reverse('vet:vet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Boutique View Test")

    def test_vet_detail_view(self):
        """Vérifie l'affichage du détail d'un VET."""
        response = self.client.get(reverse('vet:vet_detail', args=[self.vet.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VET-002")

    def test_export_pdf_view(self):
        """Vérifie la génération du PDF (Reçu)."""
        response = self.client.get(reverse('vet:vet_pdf', args=[self.vet.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_excel_view(self):
        """Vérifie la génération de l'Excel."""
        response = self.client.get(reverse('vet:vet_excel_detail', args=[self.vet.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
