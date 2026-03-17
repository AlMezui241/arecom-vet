# 🚀 GUIDE DE DÉPLOIEMENT - ARECOM SUR RENDER.COM

## 📋 PRÉREQUIS

- [x] Projet Git poussé sur GitHub: `https://github.com/AlMezui241/arecom-vet`
- [x] Compte Render.com (gratuit)
- [x] PostgreSQL gratuit sur Render (limité mais idéal pour le free tier)

---

## 🔧 ÉTAPE 1: Configuration des Fichiers (ÉTÉ FAIT ✅)

### A. Settings.py - Configuration PostgreSQL
```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```
✅ **Mis à jour** - La BD utilise maintenant `DATABASE_URL` pour PostgreSQL

### B. Requirements.txt - Vérifier les dépendances
```
Django>=5.0
dj-database-url              # ✅ Pour parser l'URL de BD
psycopg2-binary              # ✅ Driver PostgreSQL
gunicorn                      # ✅ Serveur WSGI
whitenoise[brotli]           # ✅ Serveur fichiers statiques
```
✅ **Tous les packages requis sont présents**

### C. Procfile - Configuration de la commande de démarrage
```
web: gunicorn arecom.wsgi
```
✅ **Correcto - Render utilisera cette configuration**

### D. render-build.sh - Script de déploiement
✅ **Mis à jour** - Gère maintenant correctement les migrations ET la création du superutilisateur

---

## 🌐 ÉTAPE 2: Configuration sur Render.com

### CRÉER LE SERVICE POSTGRESQL (Gratuit)

1. **Aller sur Render.com** → Dashboard
2. **Cliquer** `+ New` → PostgreSQL
3. **Remplir les champs:**
   ```
   Name:               arecom-db
   Database:           arecom_db
   User:               arecom_user
   Region:             Frankfurt (EU)  [Plus proche]
   PostgreSQL Version: 15 (ou plus récent)
   ```
4. **Limites du Free Tier:**
   - 250MB stockage
   - 90 jours d'inactivité = suppression
   - **Solution:** Faire un ping chaque mois OU upgrader pour ~$7/mois

5. **Copier** la `Internal Database URL` (commence par `postgresql://`)
   ```
   postgresql://arecom_user:xxx@dpg-xxxxx.internal:5432/arecom_db
   ```

---

### CRÉER LE SERVICE WEB (Gratuit)

1. **Cliquer** `+ New` → `Web Service`
2. **Connecter GitHub:**
   - Connecter votre compte GitHub
   - Autoriser Render
   - Sélectionner le repo `arecom-vet`

3. **Remplir la configuration:**
   ```
   Name:                arecom-vet
   Environment:         Python 3.11
   Build Command:       bash render-build.sh
   Start Command:       gunicorn arecom.wsgi:application
   Region:              Frankfurt
   Plan:                Free
   ```

4. **Ajouter les variables d'environnement** (cliquer `Environment`):

   ```
   DEBUG=False
   SECRET_KEY=django-insecure-CHANGEZ-CECI-DANS-VOTRE-VRAIE-CLE-SECRETE-HERE
   DATABASE_URL=postgresql://arecom_user:PASSWORD@dpg-xxxxx.internal:5432/arecom_db
   ALLOWED_HOSTS=arecom-vet.onrender.com
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=votre-email@gmail.com
   EMAIL_HOST_PASSWORD=votre-app-password-gmail
   ```

   **⚠️ IMPORTANT:**
   - Remplacez `DATABASE_URL` par la vraie URL de votre BD PostgreSQL
   - Remplacez `SECRET_KEY` par une clé unique et sécurisée
   - Remplacez les identifiants email

5. **Déployer** en cliquant `Create Web Service`

---

## 📍 ÉTAPE 3: Configuration des VARIABLES D'ENVIRONNEMENT

### Où trouver le `DATABASE_URL` ?

**Option A: Via Render Dashboard**
1. Allez sur PostgreSQL service created
2. Info → "Internal Database URL"
3. Copiez la chaîne complète

**Option B: Via .env.example (local)**
```
DATABASE_URL=postgresql://arecom_user:password@host:5432/arecom_db
```

### Générer une clé SECRET_KEY sécurisée :

**Localement en Python:**
```python
python
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
# Copier le résultat dans RENDER
```

---

## 💾 ÉTAPE 4: PERSISTENCE DES DONNÉES

### Le problème avec Render Free Tier:
- Après **90 jours d'inactivité**, la BD PostgreSQL est **supprimée**
- Les fichiers uploadés (media/) peuvent être perdus

### Solutions de PERSISTANCE:

#### **❌ NE PAS FAIRE:**
- Compter sur SQLite (fichiers non persistés sur Render)

#### **✅ SOLUTIONS RECOMMENDED:**

**Option 1: Utiliser un stockage cloud (Recommandé)**
```python
# Dans settings.py
import storages.backends.s3boto3

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": "arecom-media",
            "access_key_id": os.environ.get('AWS_ACCESS_KEY_ID'),
            "secret_access_key": os.environ.get('AWS_SECRET_ACCESS_KEY'),
        }
    },
}
```

**Services gratuits:**
- AWS S3: 5GB gratuit pendant 1 an
- Supabase: 1GB gratuit pour les fichiers

**Option 2: Sauvegarder la BD PostgreSQL**
```bash
# Sauvegarder périodiquement (via un script cron):
pg_dump postgresql://user:pass@host/arecom_db > backup.sql

# Restaurer:
psql postgresql://user:pass@host/arecom_db < backup.sql
```

**Option 3: Upgrade Render (Payant)**
- PostgreSQL Pro: ~$7/mois (pas d'expiration)
- Web Service: ~$7/mois (pour une vrai instance)

**Option 4: Environment avec Wake-up (Gratuit)**
```bash
# Créer un cron job qui ping votre app tous les 30 mins
# Voir: https://render.com/docs/cronjobs
```

---

## ✨ ÉTAPE 5: APRÈS LE DÉPLOIEMENT

### Vérifier le déploiement:
1. **Logs**: Aller sur le Web Service → Logs
   ```
   ✅ Build completed successfully!
   Migrations ran: X migrations
   Static files collected...
   ```

2. **Accéder au site**: 
   ```
   https://arecom-vet.onrender.com
   ```

3. **Admin Panel**:
   ```
   https://arecom-vet.onrender.com/admin
   Username: admin
   Password: [Celle définie dans render-build.sh]
   ```

### Déboguer les erreurs:

**"No such table"** → Les migrations n'ont pas roulé
```bash
# Sur Render console:
python manage.py migrate
```

**"Static files not found"** → collectstatic n'a pas fonctionné
```bash
python manage.py collectstatic --noinput
```

**"Database connection refused"**
- Vérifier DATABASE_URL dans les variables d'env
- Vérifier que la BD PostgreSQL est running

---

## 🔒 SÉCURITÉ - À FAIRE AVANT PRODUCTION

- [ ] Générer une vraie `SECRET_KEY` (jamais laisser la clé par défaut)
- [ ] Définir `DEBUG=False` en production
- [ ] Configurer `ALLOWED_HOSTS` correctement
- [ ] Utiliser des variables d'env sécurisées (pas en git)
- [ ] Configurer HTTPS (Render le fait automatiquement)
- [ ] Changer le mot de passe admin par défaut
- [ ] Valider les uploadeurs de fichiers

### Commandes à faire:
```bash
# Changer le mot de passe admin:
python manage.py changepassword admin

# Vérifier la sécurité:
python manage.py check --deploy
```

---

## 📊 STRUCTURE DU PROJET (RÉSUMÉ)

```
arecom/
├── arecom/                  # Configuration Django
│   ├── settings.py          # ✅ Mis à jour avec PostgreSQL
│   ├── urls.py
│   └── wsgi.py
├── activites/              # App: Gestion des activités
├── stock/                  # App: Gestion du stock (vignettes)
├── vet/                    # App: Gestion des établissements
├── templates/              # Templates HTML
├── static/                 # Fichiers CSS, JS
├── media/                  # Fichiers uploadés
├── manage.py
├── requirements.txt        # ✅ Dépendances correctes
├── Procfile               # ✅ Configuration Render
├── render-build.sh        # ✅ Scripts de build amélioré
├── .env.example           # ✅ Variables à configurer
└── db.sqlite3             # ⚠️ SQLite local (NE PAS envoyer sur Render)
```

---

## 🆘 SUPPORTIF APRÈS DÉPLOIEMENT

### Lien documentation:
- https://render.com/docs/deploy-django
- https://docs.djangoproject.com/en/5.2/howto/deployment/

### Commandes utiles:
```bash
# Regarder les logs en temps réel:
render logs arecom-vet

# Relancer le service:
render restart arecom-vet

# Voir les variables d'env:
render env list
```

---

## ✅ CHECKLIST FINAL

- [x] settings.py configuré pour PostgreSQL
- [x] requirements.txt à jour
- [x] Procfile créé
- [x] render-build.sh amélioré
- [x] .env.example créé
- [ ] DATABASE_URL ajouté dans Render
- [ ] Web Service créé sur Render
- [ ] Déploiement réussi ✨
- [ ] Admin accessible
- [ ] Données persistées ✅

---

**Vous êtes prêt pour le déploiement! 🚀**
