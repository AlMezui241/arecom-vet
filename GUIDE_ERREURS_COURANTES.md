# 🆘 GUIDE DES ERREURS COURANTES - ARECOM RENDER

Solutions rapides pour les problèmes les plus fréquents.

---

## ❌ ERREUR 1: "502 Bad Gateway"

### Symptôme:
```
Erreur 502 Bad Gateway
Render service is temporarily unavailable
```

### Causes Possibles:
- [ ] Build pas complété
- [ ] Database URL invalide
- [ ] Application crash au démarrage
- [ ] Gunicorn pas chargé

### Solutions:

**Étape 1**: Vérifier les logs
```
Render Dashboard
└─ arecom-vet (Web Service)
   └─ Logs (tab)
   └─ Chercher les erreurs en RED
```

**Étape 2**: Relancer le service
```
Render Dashboard
└─ arecom-vet
   └─ Manual Deploys
   └─ Click "Deploy latest"
   └─ Wait 2-3 min
```

**Étape 3**: Vérifier DATABASE_URL
```
Render Dashboard
└─ arecom-vet
   └─ Environment (tab)
   └─ Vérifier que DATABASE_URL est correct:
      - Format: postgresql://user:pass@host:5432/db
      - Pas d'espaces au début/fin
```

**Étape 4**: Vérifier SECRET_KEY
```
- DEBUG doit être: False
- SECRET_KEY ne doit pas être vide
```

---

## ❌ ERREUR 2: "No such table: auth_user"

### Symptôme:
```
Django error
ProgrammingError: relation "auth_user" does not exist
```

### Cause:
Les migrations n'ont pas roulé sur la base de données.

### Solution:

**Option A**: Relancer le build (simple)
```
Render Dashboard
└─ arecom-vet
   └─ Manual Deploys
   └─ "Deploy latest"
   
Attend que tu vois:
"✅ Migrations ran: X migrations"
```

**Option B**: Manuellement via Render Shell (avancé)
```
Render Dashboard
└─ arecom-vet
└─ Shell (haut à droite)

Exécuter:
python manage.py migrate

Tu devrais voir:
"Applying contenttypes.0001_initial..."
"Applying auth.0001_initial..."
etc.
```

---

## ❌ ERREUR 3: "TemplateDoesNotExist"

### Symptôme:
```
TemplateDoesNotExist at /admin
Couldn't find template 'admin/login.html'
```

### Cause:
Les fichiers statiques n'ont pas été collectés.

### Solution:

**Relancer collectstatic**:
```
Render Dashboard
└─ arecom-vet
   └─ Shell
   
Exécuter:
python manage.py collectstatic --noinput

Devrait dire:
"X static files copied to '/opt/render/project/.../'"
```

---

## ❌ ERREUR 4: "Connection refused" ou "Cannot connect to database"

### Symptôme:
```
psycopg2.OperationalError: 
could not connect to server: Connection refused
```

### Cause:
- DATABASE_URL invalide ou manquante
- PostgreSQL Render pas actif

### Solution:

**Étape 1**: Vérifier le DATABASE_URL
```
Render Dashboard
└─ PostgreSQL service
   └─ Click dessus
   └─ Copy "Internal Database URL"
   
Devrait ressembler à:
postgresql://user:pass@dpg-xxxxx.internal:5432/arecom_db

Puis:
└─ Web Service
   └─ Environment
   └─ Coller exactement
```

**Étape 2**: Vérifier que PostgreSQL est "Available"
```
Render Dashboard
└─ arecom-db (PostgreSQL)
└─ En bas, vérifier le status
   Devrait être: "Available" (pas "Creating")
```

**Étape 3**: Relancer le Web Service
```
Render Dashboard
└─ arecom-vet
   └─ Manual Deploys
   └─ "Deploy latest"
```

---

## ❌ ERREUR 5: "Admin login: Invalid username or password"

### Symptôme:
```
Impossible de se connecter avec admin/admin123
```

### Cause:
- Le superuser n'a pas été créé
- Mauvais password

### Solution:

**Via Render Shell** (meilleure façon):
```
Render Dashboard
└─ arecom-vet
   └─ Shell

Exécuter:
python manage.py shell

Puis dans Python:
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.save()
exit()
```

**Puis**: Réessayer avec admin/admin123

---

## ❌ ERREUR 6: "Static files return 404"

### Symptôme:
```
GET /static/css/style.css HTTP/1.1" 404
Page sans styles (CSS chargé)
```

### Cause:
Fichiers statiques pas collectés ou mal configurés.

### Solution:

**Relancer collectstatic**:
```
Render Dashboard
└─ arecom-vet
   └─ Shell

Exécuter:
python manage.py collectstatic --noinput

Vérifier:
"Copying '/opt/render/...' to '/opt/render/.../staticfiles/'"
```

**Si toujours problème**:
```
Vérifier settings.py:
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = 'static/'

Et que Render build inclut:
python manage.py collectstatic --no-input
```

---

## ❌ ERREUR 7: "ALLOWED_HOSTS doesn't allow this host"

### Symptôme:
```
400 Bad Request
Invalid HTTP_HOST header: 'arecom-vet.onrender.com'
Allowed hosts: ...
```

### Cause:
ALLOWED_HOSTS n'a pas l'URL Render.

### Solution:

```
Render Dashboard
└─ arecom-vet
   └─ Environment
   └─ ALLOWED_HOSTS
   └─ Changer pour:
      arecom-vet.onrender.com
   
Ou si domaine personnalisé:
      yourdomain.com
```

**Puis**: Relancer le deploy.

---

## ❌ ERREUR 8: "DEBUG=True in production"

### Symptôme:
```
Django warning or security issue
Site affiche les erreurs complètes
```

### Cause:
DEBUG n'est pas mis à False.

### Solution:

```
Render Dashboard
└─ arecom-vet
   └─ Environment
   └─ DEBUG
   └─ Valeur: False
   
   Si manquante, ajouter:
   DEBUG = False
```

---

## ❌ ERREUR 9: "Email not configured / SMTP error"

### Symptôme:
```
SMTPAuthenticationError
Email_HOST_USER or EMAIL_HOST_PASSWORD incorrect
```

### Cause:
Variables email mal configurées.

### Solution:

**Avec Gmail** (recommandé):
```
1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail + Windows Computer
3. Copy the 16-character password
4. Dans Render:
   EMAIL_HOST = smtp.gmail.com
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = votre-email@gmail.com
   EMAIL_HOST_PASSWORD = 16-char-app-password
```

**Test local**:
```
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@gmail.com', ['to@gmail.com'])
```

---

## ❌ ERREUR 10: "Application crashes on upload"

### Symptôme:
```
500 Internal Server Error lors d'upload de fichier
```

### Cause:
- Fichier trop gros (max 10MB)
- Format non autorisé
- Permission d'écriture

### Solution:

**Vérifier limite fichier** (settings.py):
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
```

**Formats autorisés**:
```python
ALLOWED_UPLOAD_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx'}
```

**Si fichier trop gros**: Réduire la taille ou upgrader le plan Render.

---

## ❌ ERREUR 11: "SECRET_KEY is insecure or missing"

### Symptôme:
```
Django warning: Error checking SECRET_KEY...
```

### Cause:
- SECRET_KEY manquante
- SECRET_KEY trop courte
- SECRET_KEY par défaut utilisée

### Solution:

**Générer nouvelle clé**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Ajouter à Render**:
```
Render Dashboard
└─ arecom-vet
   └─ Environment
   └─ SECRET_KEY = [coller la clé générée]
```

**JAMAIS faire**: Laisser la SECRET_KEY par défaut!

---

## ❌ ERREUR 12: "Build takes too long / times out"

### Symptôme:
```
Build command timed out
Render: Build exceeded timeout
```

### Cause:
- pip install trop lent
- Trop de migrations
- Connexion réseau lente

### Solution:

**Relancer le build**:
```
Render Dashboard
└─ arecom-vet
   └─ Manual Deploys
   └─ "Deploy latest"
```

**Si problème persiste**:
- Upgrader à PostgreSQL Pro (meilleure perf)
- Vérifier requirements.txt (pas de dépendances inutiles)

---

## ❌ ERREUR 13: "Migrations conflict / cannot rollback"

### Symptôme:
```
Migration error: Conflicting migrations detected
```

### Cause:
Migrations mal résolues.

### Solution:

**Via Render Shell**:
```
python manage.py showmigrations

python manage.py migrate --plan

python manage.py migrate
```

**Si encore problème**:
```
Ne pas essayer de rollback!

Au lieu de cela:
1. Backup database
2. Contact Render support
3. Ou relancer avec une BD neuve
```

---

## 🔧 COMMANDES DE DEBUGGING

### Voir les logs en temps réel:
```bash
# Via Render Shell:
tail -f /opt/render/service.log
```

### Accéder au Django shell:
```bash
python manage.py shell

# Puis:
from django.conf import settings
print(settings.DATABASES)
print(settings.DEBUG)
print(settings.ALLOWED_HOSTS)
```

### Tester la connexion DB:
```bash
python manage.py dbshell
# Ou
psql "postgresql://..."
```

### Vérifier les migrations:
```bash
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate --verbose
```

### Tester les settings:
```bash
python manage.py check
python manage.py check --deploy
```

---

## 📞 ESCALADE EN CAS DE PROBLÈME

### Niveau 1: Documentation (gratuit)
- [ ] Lire les guides: QUICK_START, GUIDE_DEPLOIEMENT
- [ ] Consulter ce fichier
- [ ] Vérifier les logs

### Niveau 2: Forum & Community (gratuit)
- [ ] Django: https://www.djangoproject.com/community/
- [ ] Render: https://render.com/docs/
- [ ] Stack Overflow: Search your error

### Niveau 3: Pay Support (payant)
- [ ] Render Support: https://render.com/support
- [ ] Django Professional Support
- [ ] Consultant Django

---

## ✅ CHECKLIST QUAND ÇA NE MARCHE PAS

```
□ Vérifier les logs Render (99% des solutions là)
□ Relancer le build (parfois ça suffit)
□ Vérifier DATABASE_URL
□ Vérifier SECRET_KEY
□ Vérifier DEBUG=False
□ Vérifier ALLOWED_HOSTS
□ Attendre 5 minutes (les services prennent du temps)
□ Relancer PostgreSQL
□ Relancer Web Service
□ Lire ce guide des erreurs
□ Contacter support si rien ne marche
```

---

## 🎯 PRÉVENTION

Pour éviter les erreurs:

```
✅ Toujours vérifier les logs avant d'escalader
✅ Relancer le build après chaque changement env var
✅ Faire des backups régulièrement
✅ Tester localement avant de déployer en prod
✅ Documenter tous les changements
✅ Garder une trace des erreurs passées
✅ Mettre à jour les guides après new errors
```

---

**Besoin d'aide?** Consultez:
1. Ce fichier (erreurs courantes)
2. [GUIDE_DEPLOIEMENT_RENDER.md](GUIDE_DEPLOIEMENT_RENDER.md#-déboguer-les-erreurs)
3. [QUICK_START_RENDER.md](QUICK_START_RENDER.md#-si-ça-ne-marche-pas)
4. Render Support

---

**Created**: 17 Mars 2026  
**Purpose**: Quick troubleshooting reference  
**Print it!**: Keep a copy handy
