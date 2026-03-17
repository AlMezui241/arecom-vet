# App ENTITES - Architecture Data-Driven

## Vue d'ensemble

L'app `entites` est une architecture **générique et scalable** pour gérer TOUS les types d'entités du projet ARECOM:
- VET (Vendeurs d'Équipements Électroniques Terminaux)
- Distributeurs
- Réseau Privé
- Cybercafés
- Autres types futurs (sans modifier le code!)

## Architecture

### 1. TypeEntite (Configuration par Type)
```python
class TypeEntite(models.Model):
    nom = "VET"  # Nom unique
    slug = "vet"  # Slug unique pour URLs

    # Configuration des champs (détermine quels champs sont obligatoires)
    a_frais_exploitation = False  # VET n'en a pas
    a_contribution_fonds = False  # VET n'en a pas
    a_renouvellement = False  # VET n'en a pas
    a_frais_instruction = True  # Tous en ont
```

**Avantage**: Ajouter un nouveau type = créer 1 objet TypeEntite en admin, 0 ligne de code!

### 2. Entite (Modèle Générique)
```python
class Entite(models.Model):
    type_entite = ForeignKey(TypeEntite)  # Références le type
    numero = CharField(unique=True)
    nom_entite = CharField()

    # Localisation (commune à tous)
    province, localite, quartier_zone

    # GPS (commune à tous)
    latitude, longitude, precision_gps

    # Champs OPTIONNELS (certains NULL selon le type)
    frais_instruction_dossier  # Requis si type.a_frais_instruction=True
    frais_exploitation_annuel   # Requis si type.a_frais_exploitation=True
    contribution_fonds_universel # Requis si type.a_contribution_fonds=True
```

**Clean & Validation**: La méthode `clean()` valide **dynamiquement** selon le type:
```python
def clean(self):
    if self.type_entite.a_frais_exploitation and not self.frais_exploitation_annuel:
        raise ValidationError("Frais exploitation requis pour ce type")
```

### 3. EntiteDocument (Documents Attachés)
Réutilisable pour TOUS les types d'entités.

## Données Initiales

4 types d'entités préconfigurés:

| Type | Frais Exploit | Contribution | Renouvellement |
|------|--------------|--------------|----------------|
| **VET** | ❌ | ❌ | ❌ |
| **Distributeur** | ✅ | ✅ | ✅ |
| **Réseau Privé** | ✅ | ✅ | ✅ |
| **Cybercafé** | ✅ | ✅ | ✅ |

3 exemples d'entités créées pour démo:
- DIST-001: Telecom Distributeur SA (Distributeur, Kasai)
- RES-001: Réseau Privé Congo SARL (Réseau Privé, Kasai)
- CYBER-001: Cybercafé Les Amis (Cybercafé, Kasai)

## URLs

```
/entites/                    → Liste toutes les entités (avec filtres)
/entites/dashboard/          → Dashboard stats par type/province
/entites/nouveau/            → Créer une new entité
/entites/<numero>/           → Détail d'une entité
/entites/<numero>/modifier/  → Modifier une entité
```

## Admin Django

`Admin > Entites > Types d'Entités` → Gérer les types
`Admin > Entites > Entites` → Gérer toutes les entités avec filtres

Fieldsets automatiques selon le type:
- Affiche seulement les champs pertinents
- Validation automatique

## Cas d'Utilisation: Ajouter un Nouveau Type Futur

**Scénario**: Tu dois ajouter "USSD Platform" comme nouveau type.

**Action**:
1. Admin > Entites > Types d'Entités > Ajouter
2. Nom: "USSD Platform"
3. Slug: "ussd-platform"
4. Cocher: a_frais_exploitation, a_contribution_fonds, a_renouvellement, a_frais_instruction
5. Enregistrer

**Résultat**:
- Automatiquement disponible dans filtres
- Admin prêt à créer/modifier des USSD Platform
- Views fonctionnent parfaitement
- Zéro changement de code! ✅
- Zéro migration! ✅

## Possibilité d'Améliorations Futures

1. **Service Classes**: Centraliser la logique métier (calculs, redevances)
2. **Signals**: Synchronisation auto avec app stock pour mouvements
3. **Export/Import**: Bulk upload d'entités via fichiers
4. **APIs REST**: Django REST Framework pour mobile/web queries
5. **Paiements Integration**: Lier factures/paiements par type d'entité
6. **Caching**: Redis pour stats lentes (par type/province)

## Tests

```bash
python manage.py shell

from entites.models import TypeEntite, Entite
print(f"Types: {TypeEntite.objects.count()}")
print(f"Entites: {Entite.objects.count()}")

# Créer une nouvelle entité type VET
vet_type = TypeEntite.objects.get(slug='vet')
entite = Entite.objects.create(
    type_entite=vet_type,
    numero='VET-NEW-001',
    nom_entite='Test VET',
    province='Kasai',
    localite='Tshikapa',
    quartier_zone='Centre',
    frais_instruction_dossier=50000
)
```

## Fichiers Clés

- `entites/models.py`: TypeEntite, Entite, EntiteDocument
- `entites/admin.py`: Admin Django avec fieldsets dynamiques
- `entites/views.py`: ListView, DetailView, CreateView, UpdateView
- `entites/urls.py`: Routing URL-vers-views
- `templates/entites/`: Templates list.html, detail.html, form.html

---

**Status**: ✅ Production-Ready pour démo
**Stability**: ✅ Sans impact sur VET existant
**Scalability**: ✅ Prêt pour 10+ types futurs sans refactor
