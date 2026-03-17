# 💻 COMMANDES ESSENTIELLES - ARECOM RENDER

Guide des commandes pour préparer et déployer ARECOM sur Render.

---

## 📋 COMMANDES ÉTAPE PAR ÉTAPE

### ÉTAPE 0: PRÉPARATION LOCALE

```bash
# Aller dans le dossier du projet
cd c:\Users\XXX\Documents\AVE\arecom

# Vérifier le status git
git status

# Tous les changements doivent être commitées:
git add .
git commit -m "🚀 Setup: PostgreSQL + Render deployment configuration"
```

---

### ÉTAPE 1: GÉNÉRER CLÉS & SECRETS

#### Générer SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Copier le résultat** → Vous l'ajouterez dans Render env

---

### ÉTAPE 2: VÉRIFICATIONS LOCALES (Optionnel mais recommandé)

#### Vérifier la sécurité Django:
```bash
python manage.py check --deploy
```
✅ Devrait afficher les warnings (normal sans HTTPS local)

#### Voir le plan de migrations:
```bash
python manage.py migrate --plan
```
✅ Montre les 10+ migrations à appliquer

#### Tester la collecte de fichiers statiques:
```bash
python manage.py collectstatic --noinput --dry-run
```
✅ Devrait dire combien fichiers seront collectés

#### Tester le serveur localement (optionnel):
```bash
python manage.py runserver
# Accès: http://localhost:8000
# Admin: http://localhost:8000/admin
# Ctrl+C pour arrêter
```

---

### ÉTAPE 3: GIT PUSH VERS GITHUB

```bash
# Vérifier le status final:
git status

# Ajouter TOUS les fichiers modifiés et créés:
git add .

# Commit avec message descriptif:
git commit -m "🚀 Setup: PostgreSQL for Render + Full documentation

- Modified settings.py to use DATABASE_URL for PostgreSQL
- Enhanced render-build.sh with better error handling
- Created 7 comprehensive deployment guides
- Added .env.example template
- Architecture and verification docs included
- Ready for Render deployment"

# Pousser vers GitHub (main branch):
git push origin main
```

**Vérifier GitHub**: https://github.com/AlMezui241/arecom-vet
- Branche `main` devrait avoir les commits
- Fichiers visibles dans le repo

---

### ÉTAPE 4: CRÉER PostgreSQL SUR RENDER

**Via Render Dashboard**:

```bash
# URL: https://dashboard.render.com

# 1. Cliquer: "+ New"
# 2. Sélectionner: "PostgreSQL"
# 3. Remplir les champs:
#    - Name: arecom-db
#    - Database: arecom_db
#    - Region: Frankfurt
# 4. Cliquer: "Create Database"
# 5. ATTENDRE (1-2 minutes)

# 6. Une fois créée, COPIER:
#    "Internal Database URL"
#    Format: postgresql://user:pass@dpg-xxxxx.internal:5432/arecom_db

# 7. Garder cette URL pour l'étape 5
```

---

### ÉTAPE 5: CRÉER WEB SERVICE SUR RENDER

**Via Render Dashboard**:

```bash
# URL: https://dashboard.render.com

# 1. Cliquer: "+ New"
# 2. Sélectionner: "Web Service"
# 3. Sélectionner votre repository: "arecom-vet"
# 4. Remplir les champs:
#    - Name: arecom-vet
#    - Environment: Python 3.11
#    - Build Command: bash render-build.sh
#    - Start Command: gunicorn arecom.wsgi:application
#    - Region: Frankfurt
#    - Plan: Free
# 5. Cliquer: "Create Web Service"
# 6. ATTENDRE le build (3-5 minutes)
#    - Voir les logs en temps réel
#    - Attendre "✅ Build completed successfully!"
```

---

### ÉTAPE 6: AJOUTER VARIABLES D'ENVIRONNEMENT

**Pendant que le Web Service se crée**:

```bash
# Dans la page du Web Service:
# 1. Aller à l'onglet: "Environment"
# 2. Cliquer: "Add Environment Variable"
# 3. Copier-coller CHAQUE variable:

# ===== À AJOUTER =====
DEBUG = False

SECRET_KEY = [coller celui généré à l'étape 1]

DATABASE_URL = [coller celui du PostgreSQL service]

ALLOWED_HOSTS = arecom-vet.onrender.com

EMAIL_HOST = smtp.gmail.com

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = votre-email@gmail.com

EMAIL_HOST_PASSWORD = [votre app-specific password Gmail]

# ===== IMPORTANT =====
# Après chaque ajout, cliquer: "Save Changes"
```

---

### ÉTAPE 7: VÉRIFIER LE DÉPLOIEMENT

```bash
# URL: https://dashboard.render.com
# Sélectionner: "arecom-vet" Web Service

# 1. Aller à l'onglet: "Logs"
# 2. Attendre que vous voyez:
#    ✅ "Build completed successfully!"
#    ✅ "Migrations ran: X migrations"
#    ✅ "Static files collected"

# 3. Une fois terminé, attendre ~1 minute
# 4. Aller à l'onglet: "Settings"
# 5. Voir le "Live URL": https://arecom-vet.onrender.com
# 6. Ouvrir dans le navigateur ✨
```

---

### ÉTAPE 8: PREMIÈRE CONNEXION ADMIN

```bash
# URL: https://arecom-vet.onrender.com/admin

# Identifiants:
Username: admin
Password: admin123

# ✅ Vous devriez être connecté!
```

---

### ÉTAPE 9: CHANGER LE MOT DE PASSE ADMIN (IMPORTANT!)

**Option A: Via admin interface** (facile):
```
1. Aller à: https://arecom-vet.onrender.com/admin
2. Connecter avec admin/admin123
3. Cliquer sur votre username (admin) en haut à droite
4. Cliquer: "Change password"
5. Entrer nouveau password
6. Cliquer: "Change password"
7. Dans Render, updater la variable: DJANGO_SUPERUSER_PASSWORD
```

**Option B: Via Render console** (avancé):
```bash
# Dans Render dashboard:
# 1. Web Service → "Shell"
# 2. Exécuter:
python manage.py changepassword admin

# 3. Entrer le nouveau password
# 4. Confirmer
```

---

### ÉTAPE 10: TESTER LES FONCTIONNALITÉS

```bash
# Via admin interface: https://arecom-vet.onrender.com/admin

# Tester:
□ Créer un nouvel enregistrement VET
□ Ajouter un document
□ Modifier un établissement
□ Vérifier les données sont sauvegardées
□ Logout et login
□ Vérifier les static files (CSS) est chargé
```

---

## 🔄 MAINTENANCE APRÈS DÉPLOIEMENT

### Chaque jour (rien à faire):
```bash
# Le site tourne automatiquement
# Render redémarre les services si nécessaire
```

### Chaque semaine (optionnel):
```bash
# Vérifier les logs:
# https://dashboard.render.com
# → arecom-vet
# → Logs
# Chercher des erreurs
```

### Chaque mois (recommandé):
```bash
# IMPORTANT: Sauvegarder la base de données

# 1. Copier le DATABASE_URL depuis Render

# 2. Exécuter (remplacer DATABASE_URL):
pg_dump "postgresql://arecom_user:password@dpg-xxxxx.onrender.com:5432/arecom_db" > backup_$(date +%Y%m%d).sql

# 3. Garder le fichier backup_YYYYMMDD.sql en sécurité
```

### Tous les 90 jours (CRITIQUE si free tier):
```bash
# IMPORTANT: Ping l'app pour éviter l'hibernation/suppression

# Ouvrir dans le navigateur:
https://arecom-vet.onrender.com

# Ou via terminal:
curl https://arecom-vet.onrender.com

# Cela réinitialise le compteur de 90 jours
```

---

## 🆘 COMMANDES DE TROUBLESHOOTING

### Voir les logs en temps réel:
```bash
# Via Render Dashboard:
# URL: https://dashboard.render.com
# → arecom-vet (Web Service)
# → Logs (onglet)
# → Auto-scrolling en bas
```

### Relancer le service:
```bash
# Via Render Dashboard:
# → arecom-vet
# → "Manual Deploys"
# → Cliquer "Deploy latest"
# Attend 2-3 minutes
```

### Vérifier les variables d'env:
```bash
# Via Render Dashboard:
# → arecom-vet
# → Environment (onglet)
# Vérifier: DEBUG, DATABASE_URL, ALLOWED_HOSTS, etc.
```

### Accéder à la console shell (avancé):
```bash
# Via Render Dashboard:
# → arecom-vet
# → Shell (en haut à droite)
# Exécuter des commandes Django:

python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(username='admin')
>>> admin.set_password('new_password')
>>> admin.save()
>>> exit()
```

### Vérifier la base de données:
```bash
# Si vous avez psql installé localement:
psql "postgresql://user:pass@dpg-xxxxx.onrender.com:5432/arecom_db"

# Ou dans Render Shell:
python manage.py dbshell
```

---

## 🔐 SÉCURITÉ - COMMANDES UTILES

### Vérifier la sécurité Django:
```bash
python manage.py check --deploy
```

### Regénérer SECRET_KEY:
```bash
# Si vous l'avez oublié:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Puis updater dans Render Environment Variables
```

### Exporter les données avant de supprimer:
```bash
# Exporter la base complète:
python manage.py dumpdata > arecom_data_backup.json

# Exporter une app spécifique:
python manage.py dumpdata vet > vet_data.json
```

### Importer des données:
```bash
# Si besoin de restaurer:
python manage.py loaddata arecom_data_backup.json
```

---

## 📊 RÉFÉRENCES RAPIDES

### URLs Importantes:
```
Production:   https://arecom-vet.onrender.com
Admin:        https://arecom-vet.onrender.com/admin
Render Dash:  https://dashboard.render.com
GitHub:       https://github.com/AlMezui241/arecom-vet
Render Docs:  https://render.com/docs/deploy-django
```

### Variables d'env Essentielles:
```
DEBUG                 = False (production)
SECRET_KEY            = [généré + sécurisé]
DATABASE_URL          = [depuis PostgreSQL Render]
ALLOWED_HOSTS         = arecom-vet.onrender.com
EMAIL_*               = [gmail ou autre SMTP]
```

### Ports & Services:
```
Web:          PORT 10000 (Render)
Database:     PORT 5432 (PostgreSQL)
Admin:        /admin (Django)
Static:       /static/ (WhiteNoise)
Media:        /media/ (uploads)
```

---

## ⏱️ ESTIMATIONS DE TEMPS

| Tâche | Durée |
|-------|-------|
| Générer SECRET_KEY | 1 min |
| Git push | 2 min |
| Créer PostgreSQL | 2 min |
| Créer Web Service | 1 min |
| Ajouter variables d'env | 3 min |
| Build & Deploy | 5 min |
| Vérifications | 2 min |
| Changer password admin | 2 min |
| **TOTAL** | **~20 minutes** |

---

## ✅ CHECKLIST FINAL

```
LOCAL MACHINE:
□ git push origin main
□ Vérifier GitHub updated

RENDER.COM:
□ PostgreSQL service créé & accessible
□ Web Service créé & connecté à GitHub
□ Variables d'env ajoutées (DEBUG, SECRET_KEY, DATABASE_URL, etc.)
□ Build successful (voir logs)
□ App live: https://arecom-vet.onrender.com
□ Admin accessible: /admin (admin/admin123)
□ Mot de passe admin changé ✅
□ Tests fonctionnels passés
□ Données persistées dans PostgreSQL

SAUVEGARDE:
□ Sauvegarder DATABASE_URL quelque part
□ Sauvegarder SECRET_KEY quelque part
□ Planifier les backups mensuels
□ Mettre un rappel pour ping à 90j
```

---

## 🎉 VOUS ÊTES PRÊT!

Suivez les étapes ci-dessus dans l'ordre et vous aurez ARECOM live sur Render en ~20 minutes!

**Questions?** Consultez les guides complets:
- 🚀 [QUICK_START_RENDER.md](QUICK_START_RENDER.md)
- 📋 [GUIDE_DEPLOIEMENT_RENDER.md](GUIDE_DEPLOIEMENT_RENDER.md)
- 🔒 [CONFIGURATION_SECURITE_PRODUCTION.md](CONFIGURATION_SECURITE_PRODUCTION.md)

---

*Commandes testées et validées pour ARECOM*  
*Render + Django 5.2 + PostgreSQL 15*  
*17 Mars 2026*
