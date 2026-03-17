# 🏗️ ARCHITECTURE - ARECOM DEPLOYMENT

## 📐 Vue d'ensemble du projet

```
┌─────────────────────────────────────────────────────────────┐
│                    ARECOM MANAGEMENT SYSTEM                 │
│                   (Gestion des redevances)                   │
└─────────────────────────────────────────────────────────────┘

┌─── APPLICATIONS DJANGO ────────────────────────────────────┐
│                                                              │
│  ┌─────────────┐    ┌──────────┐    ┌────────────────┐    │
│  │     VET     │    │  STOCK   │    │   ACTIVITES    │    │
│  │             │    │          │    │                │    │
│  │• Recettes   │    │• Vignettes│   │• Commerces     │    │
│  │• Redevances │    │• Inventory│   │• Activités     │    │
│  │• Paiements  │    │• Mouvements│  │• Autorisation  │    │
│  │• Vignettes  │    │• Audit    │   │• Statistiques  │    │
│  │• GPS Mapping│    │           │   │• Configuration │    │
│  └─────────────┘    └──────────┘    └────────────────┘    │
│                                                              │
└────────────────────────────────────────────────────────────┘

┌─── INFRASTRUCTURE ─────────────────────────────────────────┐
│                                                              │
│   LOCAL DEVELOPMENT           RENDER DEPLOYMENT             │
│   ═════════════════════      ════════════════════            │
│                                                              │
│   Python 3.11                                               │
│      │                                                      │
│   SQLite ◄──────────┐                                       │
│   (local)           │                                       │
│      │              │  Git Push                PostgreSQL   │
│      │              ├─────────────────────────► (250MB)     │
│   Django           │                            │           │
│   (manage.py)──────┴─► GitHub Repo ────────►  │           │
│                        (main branch)       Render.com       │
│                                                │           │
│                                           Gunicorn Server   │
│                                           (Web Service)     │
│                                                │           │
│                                            HTTPS Proxy      │
│                                                │           │
│                                   arecom-vet.onrender.com   │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUX DE DÉPLOIEMENT

```
1. DÉVELOPPEMENT LOCAL
   ├─ Code modifications
   ├─ Test avec SQLite (db.sqlite3)
   ├─ python manage.py runserver
   └─ Vérifier http://localhost:8000/admin

2. GIT & GITHUB
   ├─ git add .
   ├─ git commit -m "message"
   └─ git push origin main
        │
        └─► GitHub reçoit le push
            Trigger: Render webhook

3. RENDER DEPLOYMENT
   ├─ Détecte le push sur GitHub
   ├─ Clone le repo
   ├─ Exécute render-build.sh:
   │   ├─ pip install requirements.txt
   │   ├─ python manage.py collectstatic
   │   ├─ python manage.py migrate (PostgreSQL)
   │   └─ Crée superuser admin
   │
   ├─ Lance Gunicorn
   └─ Application disponible en ligne

4. PRODUCTION
   ├─ PostgreSQL persiste les données
   ├─ WhiteNoise sert les fichiers statiques
   ├─ Gunicorn gère les requests
   └─ HTTPS automatique (Render)
```

---

## 🗄️ MODÈLE DE DONNÉES

```
┌─────────────────────────────────────────────────────┐
│                  VET TABLE                          │
├─────────────────────────────────────────────────────┤
│ PK: numero (Auto-increment)                         │
│ FK: Type d'établissement                            │
│                                                      │
│ PRIMARY INFO:                                       │
│ • numero_ordre_de_recette (UNIQUE, indexed)        │
│ • nom_etablissement                                │
│ • statut_juridique                                 │
│                                                      │
│ LOCALISATION:                                      │
│ • region, zone, quartier (indexed together)        │
│ • latitude, longitude (GPS)                        │
│                                                      │
│ FINANCIER:                                         │
│ • montant_redevance_annuelle                       │
│ • frais_dossier                                    │
│ • redevance_payee (boolean)                        │
│ • frais_de_dossier_payes (boolean)                 │
│                                                      │
│ VIGNETTES:                                         │
│ • possede_vignettes (boolean)                      │
│ ◄────FK────► VET_VIGNETTE (M2M bridge)             │
│                ├─ VET_ID                            │
│                ├─ CATEGORIE_ID                      │
│                └─ quantite                          │
│                │                                    │
│                └────FK────► VIGNETTE_CATEGORY      │
│                              • niveau               │
│                              • prix                 │
│                              • stock_actuel         │
│                                                      │
│ DOCUMENTS:                                         │
│ • presence_facture (boolean)                       │
│ ◄────FK────► VET_DOCUMENT (1toMany)                │
│                ├─ file                              │
│                ├─ type (photo, scan, other)        │
│                └─ date_upload                       │
│                                                      │
│ AUDIT:                                              │
│ • date_creation                                    │
│ • date_mise_a_jour                                 │
│ • statut (actif, suspendu, fermé)                 │
│                                                      │
│ CONSTRAINTS:                                       │
│ ✓ date_expiration >= date_emission                │
│ ✓ montant_redevance >= 0                          │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│            STOCK MOVEMENT TABLE                     │
├─────────────────────────────────────────────────────┤
│ PK: id                                              │
│ FK: vignette_category_id                           │
│ FK: vet_id (optionnel)                             │
│ FK: user_id (qui a fait le mouvement)              │
│                                                      │
│ • type (entree, sortie, ajustement)               │
│ • quantite                                          │
│ • date_mouvement                                   │
│ • description                                      │
│ • est_automatique (boolean)                        │
│                                                      │
│ SIGNALS DJANGO:                                    │
│ ├─ post_save → Met à jour VignetteCategory.stock  │
│ └─ post_delete → Recalcule les stocks              │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│             ACTIVITE TABLE (Polymorphe)             │
├─────────────────────────────────────────────────────┤
│ PK: id                                              │
│ FK: type_activite_id                               │
│       │                                              │
│       └─► TYPE_ACTIVITE (configuration flexible)   │
│           • nom (telecoms, poste, etc.)            │
│           • a_frais_exploitation (boolean)         │
│           • a_contribution_fonds (boolean)         │
│           • Flags pour validation dynamique        │
│                                                      │
│ DONNÉES (similaires à VET):                        │
│ • nom_activite                                     │
│ • region, zone, quartier, GPS                      │
│ • redevance_annuelle                               │
│ • statut_autorisation                              │
│ • contrepartie_financiere                          │
│                                                      │
│ VALIDATION:                                        │
│ def clean():                                       │
│   if typeactivite.a_frais_instruction:             │
│       montant_total = redevance + frais_instruction│
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 CONFIGURATION POUR LA SÉCURITÉ

```
┌─ LOCAL (.env) ─────────────────────────────┐
│ DEBUG=True                                 │
│ SECRET_KEY=test-key                       │
│ DATABASE_URL=sqlite:///db.sqlite3         │
│ EmailBackend=console❎ en prod            │
└────────────────────────────────────────────┘

         ⬇️  (JAMAIS commiter .env)

┌─ GITHUB ────────────────────────────────────┐
│ • Code uniquement                           │
│ • .env ignoré par .gitignore               │
│ • db.sqlite3 ignoré                         │
│ • settings.py lisait depuis os.environ      │
└────────────────────────────────────────────┘

         ⬇️  (Webhook autorise Render)

┌─ RENDER ENVIRONMENT ───────────────────────┐
│ DEBUG=False                                │
│ SECRET_KEY=very-long-random-key           │
│ DATABASE_URL=postgresql://...             │
│ ALLOWED_HOSTS=arecom-vet.onrender.com     │
│ EMAIL_HOST=smtp.gmail.com                 │
│                                             │
│ Sécurité:                                  │
│ ✅ HTTPS automatique (Render cert)         │
│ ✅ SECURE_SSL_REDIRECT = True             │
│ ✅ CSRF_COOKIE_SECURE = True              │
│ ✅ SESSION_COOKIE_SECURE = True           │
│ ✅ X-Frame-Options = DENY                 │
└────────────────────────────────────────────┘
```

---

## 📊 DÉPLOIEMENT - MATRICE DES RESPONSABILITÉS

| Ressource | Provider | Gratuit? | Limites | Type |
|-----------|----------|---------|---------|------|
| **Code** | GitHub | ✅ | Repos publics illimités | Dépôt |
| **Web Server** | Render | ✅ | 15 min hibernation | Compute |
| **Database** | Render PostgreSQL | ✅ | 250MB, 90j inactivité | Storage |
| **Static Files** | WhiteNoise (Render) | ✅ | Intégré à Web Service | Serving |
| **Media Files** | Render Filesystem | ⚠️ | À considérer S3/Supabase | Storage |
| **Email** | SMTP Gmail | ✅ | Limité à 500/jour | Service |
| **Monitoring** | Render Logs | ✅ | 24h rétention | Logs |
| **SSL/TLS** | Render | ✅ | Automatique | Sécurité |

---

## 🔄 DONNÉES ET PERSISTANCE

```
Scenario: 90 jours sans activité sur Render

Jour 0-30:        Jour 31-60:       Jour 61-90:      Jour 91+:
✅ BD Persiste    ✅ BD Persiste    ✅ BD Persiste   ❌ BD SUPPRIMÉE!
                                    ⚠️  Avertissement
                                    
SOLUTIONS:
──────────

1️⃣  Pinger chaque mois (gratuit)
   └─ Cronjob: curl https://arecom-vet.onrender.com
      → Réinitialise le compteur d'inactivité

2️⃣  Générer clé secrète (gratuit)
   └─ python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

3️⃣  Backups PostgreSQL (semi-auto)
   └─ Sauvegarder chaque semaine:
      pg_dump postgresql://xxx > backup.sql
      Restore:
      psql postgresql://xxx < backup.sql

4️⃣  Upgrade PostgreSQL Pro ($7/mois)
   └─ Pas d'expiration
      500MB stockage

5️⃣  S3 / Supabase pour Media (gratuit) 
   └─ AWS Free Tier: 5GB pendant 1 an
      Supabase: 1GB gratuit
```

---

## 🚀 CHECKLIST DE DÉPLOIEMENT

```
AVANT LE PUSH GITHUB:
☐ Vérifier .gitignore (ne pas commiter .env)
☐ Tester localement: python manage.py check --deploy
☐ Migrations: python manage.py migrate --plan
☐ Static files: python manage.py collectstatic --dry-run
☐ Admin: Accès au /admin OK

GITHUB:
☐ git add arecom/settings.py render-build.sh .env.example
☐ git commit -m "Setup: PostgreSQL for Render"
☐ git push origin main

RENDER.COM:
☐ Créer PostgreSQL service → Copier DATABASE_URL
☐ Créer Web Service
☐ Ajouter variables d'env (DEBUG, SECRET_KEY, DATABASE_URL...)
☐ Connecter GitHub repo
☐ Cliquer "Create Web Service"
☐ Attendre le build (3-5 minutes)

POST-DÉPLOIEMENT:
☐ Vérifier logs (pas d'erreurs)
☐ Accéder à https://arecom-vet.onrender.com
☐ Test admin: /admin (user: admin, pass: admin123)
☐ Changer le mot de passe admin
☐ Test création VET/Activité
☐ Test upload fichier
```

---

## 📞 RESSOURCES UTILES

### Documentation:
- Django: https://docs.djangoproject.com/en/5.2/
- Render: https://render.com/docs/deploy-django
- PostgreSQL: https://www.postgresql.org/docs/15/
- dj-database-url: https://github.com/jazzband/dj-database-url

### Outils:
```bash
# Générer SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Vérifier sécurité:
python manage.py check --deploy

# Vérifier BD PostgreSQL (local):
psql postgresql://user:pass@localhost/arecom_db

# Export BD:
pg_dump postgresql://xxx > backup.sql

# Logs Render (SSH):
ssh -i ~/.ssh/id_rsa <user>@<service>
```

---

## ✨ RÉSULTAT ATTENDU

Après déploiement:
```
✅ https://arecom-vet.onrender.com
✅ PostgreSQL 15 avec 250MB stockage
✅ Données persistées (90 jours min)
✅ Admin accessible et sécurisé
✅ Fichiers statiques comprimés (WhiteNoise)
✅ SSL/TLS automatique
✅ Logs en temps réel sur Render
✅ Déploiement continu depuis GitHub
```

---

**Architecture: ✅ Complète & Documentée**
