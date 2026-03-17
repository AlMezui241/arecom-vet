# 🔐 GUIDE D'ACCÈS - COMPTE ADMIN

**Date**: 12 Mars 2026

---

## 📝 IDENTIFIANTS ADMIN

```
Username: admin
Password: admin123
Email:    admin@arecom.local
```

---

## 🌐 ACCÈS À L'APPLICATION

### 1. Démarrer le serveur Django

```bash
cd /c/Users/XXX/Documents/AVE/arecom
python manage.py runserver
```

Sortie attendue:
```
Starting development server at http://127.0.0.1:8000/
```

### 2. Accéder à l'application

**Interface publique**: http://localhost:8000/
**Admin Django**: http://localhost:8000/admin/

### 3. Se connecter

**URL**: http://localhost:8000/login/
- **Username**: admin
- **Password**: admin123

### 4. Dashboard Admin

**URL**: http://localhost:8000/admin/
- Cliquez sur **"Log in"**
- Entrez les identifiants ci-dessus
- Accédez à l'interface d'administration

---

## 📊 PAGES PRINCIPALES

| Page | URL | Statut |
|------|-----|--------|
| **Accueil** | http://localhost:8000/ | ✅ Public |
| **VET** | http://localhost:8000/vet/ | ✅ Authentifié |
| **Stock** | http://localhost:8000/stock/ | ✅ Authentifié |
| **Activités** | http://localhost:8000/activites/ | ✅ Authentifié |
| **Admin** | http://localhost:8000/admin/ | ✅ Admin uniquement |

---

## 🔑 GESTION DES COMPTES

### Changer le mot de passe admin

```bash
python manage.py changepassword admin
```

### Créer un nouvel utilisateur

```bash
python manage.py createsuperuser
```

### En ligne de commande Django

```bash
python manage.py shell
```

Puis dans le shell:
```python
from django.contrib.auth.models import User

# Changer le mot de passe
user = User.objects.get(username='admin')
user.set_password('nouveau_mot_de_passe')
user.save()

# Créer un nouvel utilisateur
User.objects.create_user(
    username='utilisateur',
    email='user@example.com',
    password='password123',
    is_staff=True,
    is_superuser=True
)
```

---

## ✅ TEST DE CONNEXION

1. **Démarrer le serveur**
   ```bash
   python manage.py runserver
   ```

2. **Aller à**: http://localhost:8000/

3. **Cliquer sur**: "Se connecter"

4. **Entrer**:
   - Username: `admin`
   - Password: `admin123`

5. **Vous devriez voir**: Le dashboard principal

---

## ⚠️ SÉCURITÉ

### ⚠️ À UTILISER UNIQUEMENT EN DÉVELOPPEMENT

Cette configuration est **INSECURE** en production:
- ✅ OK pour développement local
- ❌ JAMAIS en production
- ❌ JAMAIS sur serveur public

### Pour la production:

1. **Créer un mot de passe fort**
   ```bash
   python manage.py changepassword admin
   ```

2. **Utiliser des variables d'environnement**
   ```python
   # settings.py
   SECRET_KEY = os.environ['SECRET_KEY']
   DEBUG = os.environ.get('DEBUG', 'False') == 'True'
   ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
   ```

3. **Activer HTTPS**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Désactiver l'admin Django** (si possible)
   Ou restreindre l'accès à une IP spécifique

---

## 🚀 COMMANDES UTILES

```bash
# Démarrer le serveur
python manage.py runserver

# Créer un nouvel admin
python manage.py createsuperuser

# Changer le mot de passe
python manage.py changepassword admin

# Shell Django
python manage.py shell

# Migrations
python manage.py migrate

# Tests
python manage.py test activites

# Collecte des fichiers statiques
python manage.py collectstatic
```

---

## 📱 FONCTIONNALITÉS PRINCIPALES

### Dashboard (/ - Page d'accueil)
- Vue d'ensemble du système
- Statistiques VET et Activités
- Accès aux différentes apps

### VET (/vet/)
- Gestion des établissements assujettis
- Suivi des vignettes
- Rapports et exports

### Stock (/stock/)
- Gestion du stock de vignettes
- Mouvements de stock
- Inventaire

### Activités (/activites/)
- Gestion des distributeurs, réseaux, cybercafés
- Cartes GPS
- Exports (Excel, CSV)
- Dashboard par type

### Admin (/admin/)
- Interface complète d'administration
- Gestion des utilisateurs
- Gestion de tous les modèles
- Logs d'audit

---

## 🆘 DÉPANNAGE

### "Page not found" (Error 404)

Vérifiez que:
1. Le serveur est démarré: `python manage.py runserver`
2. L'URL est correcte
3. L'app est en `INSTALLED_APPS`

### "Permission denied" (Error 403)

Vérifiez que:
1. Vous êtes connecté
2. Votre utilisateur a les permissions requises
3. DEBUG = True en développement

### "Database error"

Vérifiez que:
1. Les migrations ont été appliquées: `python manage.py migrate`
2. La base de données existe
3. Les permissions fichiers sont correctes

### Mot de passe oublié

Réinitialisez-le:
```bash
python manage.py changepassword admin
```

---

## 📞 SUPPORT

Pour les questions sur l'accès:
1. Vérifier cette page: `GUIDE_ACCES_ADMIN.md`
2. Consulter: `README_ANALYSE.md`
3. Consulter: `INDEX_COMPLET.md`

---

**Guide créé le 12 Mars 2026**
