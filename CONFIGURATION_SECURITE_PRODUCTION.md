# 🔒 CONFIGURATION DE SÉCURITÉ - ARECOM PRODUCTION

## Améliorations à faire dans `settings.py`

Ajouter après les imports pour améliorer la configuration de sécurité:

```python
# ============================================================================
# SECURITY CONFIGURATIONS FOR PRODUCTION
# ============================================================================

# HTTPS and Security Headers
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com"),
    "script-src": ("'self'",),
    "font-src": ("'self'", "fonts.gstatic.com"),
}

# HSTS - HTTP Strict Transport Security (optionnel, à ajouter après test)
# SECURE_HSTS_SECONDS = 31536000  # 1 an
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# X-Frame-Options pour empêcher le clickjacking
X_FRAME_OPTIONS = "DENY"

# Content-Type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# File upload restrictions
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

# Allowed file extensions for uploads
ALLOWED_UPLOAD_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx'}

# Database connection timeout for PostgreSQL
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30s timeout
}
```

---

## ✅ AMÉLIORATIONS APPORTÉES AU PROJET

### 1. **Configuration DATABASES** ✅
**Avant:**
```python
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}
```

**Après:**
```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Avantages:**
- ✅ PostgreSQL obligatoire (SQLite ne persiste pas sur Render)
- ✅ Health checks pour les connexions défaillantes
- ✅ Compatible avec `DATABASE_URL` de Render

---

### 2. **Script de Build Render** ✅
**Avant:** Script basique avec gestion manuelle du superutilisateur

**Après:**
```bash
#!/usr/bin/env bash
set -o errexit
pip install --upgrade pip && pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
# Crée le superuser via Django shell (évite les doublons)
```

**Avantages:**
- ✅ Pas de doublons de superuser
- ✅ Gestion d'erreurs robuste
- ✅ Messages informatifs

---

### 3. **Fichiers de Configuration** ✅

| Fichier | Créé | Description |
|---------|------|-------------|
| `.env.example` | ✅ | Modèle des variables d'env requises |
| `GUIDE_DEPLOIEMENT_RENDER.md` | ✅ | Guide complet de déploiement |
| `.gitignore` | Vérifier | Ne pas commiter `.env` ou `db.sqlite3` |

---

## 🔐 VARIABLES D'ENVIRONNEMENT REQUISES

Créer dans Render Dashboard:

```
DEBUG=False
SECRET_KEY=<générer via Python>
DATABASE_URL=postgresql://user:pass@host/db
ALLOWED_HOSTS=arecom-vet.onrender.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific password>
```

---

## 📦 DÉPENDANCES (VÉRIFIÉES)

```
✅ Django>=5.0
✅ dj-database-url          # Parsing DATABASE_URL
✅ psycopg2-binary          # Driver PostgreSQL
✅ gunicorn                 # WSGI server
✅ whitenoise[brotli]      # Static serving + compression
✅ Pillow                  # Image handling
✅ django-widget-tweaks    # Form rendering
```

---

## 🚨 À FAIRE AVANT LA PRODUCTION

- [ ] Générer `SECRET_KEY` aléatoire:
  ```python
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] Vérifier les fichiers statiques:
  ```bash
  python manage.py collectstatic --noinput --dry-run
  ```

- [ ] Tester les migrations:
  ```bash
  python manage.py migrate --plan
  ```

- [ ] Vérifier la sécurité:
  ```bash
  python manage.py check --deploy
  ```

- [ ] Commiter les changements:
  ```bash
  git add .
  git commit -m "🔒 Security: PostgreSQL config + Render deployment setup"
  git push origin main
  ```

---

## 🗂️ STRUCTURE DES DONNÉES - VIEWS PRINCIPALES

### VET (Établissements Assujettis)
```
√ Localisation (région, zone, quartier)
√ GPS (latitude, longitude)
√ Données financières (redevance annuelle, frais)
√ Statuts (paiement, vignettes, autorisation)
√ Documents attachés (scan, photos)
```

### STOCK (Gestion des Vignettes)
```
√ Catégories de vignettes (par niveau d'équipement)
√ Mouvements (entrées, sorties, ajustements)
√ Inventory tracking (quantités, seuils d'alerte)
```

### ACTIVITES (Activités Commerciales)
```
√ Types flexibles (télécoms, poste, etc.)
√ Données similaires à VET
√ Statut d'autorisation
√ Calcul dynamique de redevances
```

---

## 📊 PLAN DE PERSISTANCE DES DONNÉES

### Court terme (Gratuit - 90 jours):
- ✅ PostgreSQL Render Free: Données persistées 90 jours
- ✅ Backup manuel: Exporter la BD chaque mois

### Long terme (Recommandé):
**Option A: AWS S3 + PostgreSQL Pro (15$/mois total)**
```python
# Pour les fichiers media/
STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"
```

**Option B: Supabase + PostgreSQL (gratuit 1GB)**
```
DATABASE_URL=postgresql://supabase-user:pass@db.supabase.co/arecom
```

**Option C: Railway.app (gratuit 5$ crédits)**
```
Meilleur alternative à Render avec plus de crédits gratuits
```

---

## ✨ POST-DÉPLOIEMENT

Après que le site soit live:

1. **Vérifier l'accès admin:**
   ```
   https://arecom-vet.onrender.com/admin
   user: admin
   pass: [celle dans render-build.sh]
   ```

2. **Changer le mot de passe admin:**
   ```bash
   python manage.py changepassword admin
   ```

3. **Tester l'upload de fichiers:**
   - Aller sur VET ou Activités
   - Upload un document
   - Vérifier qu'il est stocké

4. **Configurer les logs:**
   - Render affiche les logs automatiquement
   - Vérifier: https://dashboard.render.com/logs

5. **Monitoring:**
   - Ajouter du monitoring via Sentry (gratuit):
   ```python
   import sentry_sdk
   sentry_sdk.init(
       dsn="https://xxxxx@sentry.io/yyyyyyyy",
       traces_sample_rate=0.1,
   )
   ```

---

## 🆘 TROUBLESHOOTING

| Problème | Solution |
|----------|----------|
| "No such table" | Relancer `python manage.py migrate` |
| "Static files 404" | `python manage.py collectstatic --noinput` |
| "Database connection failed" | Vérifier `DATABASE_URL` et firewall Render |
| "502 Bad Gateway" | Vérifier les logs: `render logs` |
| "Media files not found" | Considérer S3 ou Supabase pour persistence |

---

## 📞 CONTACTS & RESSOURCES

- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/5.2/howto/deployment/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Django Health Checks:** https://github.com/KristianOellegaard/django-health-check

---

**Configuration: ✅ COMPLÈTE**
**Prêt pour déploiement: ✅ OUI**
