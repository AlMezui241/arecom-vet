from django.test import TestCase
from django.contrib.auth.models import User
from .models import VignetteCategory, MouvementStock
from decimal import Decimal

class StockModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = VignetteCategory.objects.create(
            niveau=1,
            prix=Decimal("250.00"),
            description="Niveau 1 test",
            stock_actuel=100
        )

    def test_category_creation(self):
        """Vérifie la création d'une catégorie de vignette."""
        self.assertEqual(self.category.niveau, 1)
        self.assertEqual(self.category.stock_actuel, 100)
        self.assertEqual(str(self.category), "Niveau 1 (250.00 F)")

    def test_mouvement_entree_updates_stock(self):
        """Vérifie qu'un mouvement d'entrée augmente le stock via le signal."""
        MouvementStock.objects.create(
            category=self.category,
            type_mouvement='entree',
            quantite=50,
            utilisateur=self.user,
            commentaire="Entrée de test"
        )
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 150)

    def test_mouvement_sortie_updates_stock(self):
        """Vérifie qu'un mouvement de sortie diminue le stock via le signal."""
        MouvementStock.objects.create(
            category=self.category,
            type_mouvement='sortie',
            quantite=30,
            utilisateur=self.user,
            commentaire="Sortie de test"
        )
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 70)

    def test_mouvement_delete_restores_stock(self):
        """Vérifie que la suppression d'un mouvement rétablit le stock."""
        mvt = MouvementStock.objects.create(
            category=self.category,
            type_mouvement='sortie',
            quantite=20,
            utilisateur=self.user
        )
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 80)
        
        mvt.delete()
        self.category.refresh_from_db()
        self.assertEqual(self.category.stock_actuel, 100)
