# ✅ CHECKLIST IMPRIMABLE - ARECOM DEPLOYMENT

Imprimez cette page et cochez les cases au fur et à mesure du déploiement!

---

## 📋 PRÉPARATION (Local)

```
□ Lire QUICK_START_RENDER.md (5 min)
□ Vérifier que Git est configuré
□ Vérifier la connexion GitHub
□ Générer SECRET_KEY:
  SECRET_KEY = _________________________________
```

---

## 🔑 GÉNÉRER CLÉS

```
□ Dans terminal Python:
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

□ Copier le résultat:
  SECRET_KEY = _________________________________
```

---

## 📤 GIT PUSH

```
□ Vérifier les changements: git status
□ Ajouter les fichiers: git add .
□ Committer: git commit -m "🚀 Setup Render"
□ Pousser: git push origin main
□ Vérifier sur GitHub: https://github.com/AlMezui241/arecom-vet
  └─ Commit visible? OUI / NON
```

---

## 🗄️ CRÉER PostgreSQL (Render)

```
□ Aller à: https://dashboard.render.com
□ Cliquer: "+ New"
□ Sélectionner: "PostgreSQL"
□ Remplir:
  Name:       arecom-db
  Database:   arecom_db
  Region:     Frankfurt
  
□ Cliquer: "Create Database"
□ ATTENDRE 1-2 minutes
□ Copier "Internal Database URL":
  DATABASE_URL = _________________________________
  
  Format: postgresql://user:pass@dpg-xxxxx.internal:5432/arecom_db
```

---

## 🌐 CRÉER WEB SERVICE (Render)

```
□ Aller à: https://dashboard.render.com
□ Cliquer: "+ New"
□ Sélectionner: "Web Service"
□ Sélectionner le repo: "arecom-vet"
□ Remplir:
  Name:              arecom-vet
  Environment:       Python 3.11
  Build Command:     bash render-build.sh
  Start Command:     gunicorn arecom.wsgi:application
  Region:            Frankfurt
  Plan:              Free
  
□ Cliquer: "Create Web Service"
□ ATTENDRE 3-5 minutes (voir les logs)
```

---

## 🔐 AJOUTER VARIABLES D'ENVIRONNEMENT

```
Dans la page du Web Service créé:

□ Onglet:    Environment
□ Bouton:    "Add Environment Variable"

Ajouter CHAQUE variable (copier-coller exact):

1. DEBUG
   Valeur: False
   □ Save Changes

2. SECRET_KEY
   Valeur: [coller celui généré plus haut]
   □ Save Changes

3. DATABASE_URL
   Valeur: [coller celui du PostgreSQL]
   □ Save Changes

4. ALLOWED_HOSTS
   Valeur: arecom-vet.onrender.com
   □ Save Changes

5. EMAIL_HOST
   Valeur: smtp.gmail.com
   □ Save Changes

6. EMAIL_PORT
   Valeur: 587
   □ Save Changes

7. EMAIL_USE_TLS
   Valeur: True
   □ Save Changes

8. EMAIL_HOST_USER
   Valeur: [votre adresse email]
   □ Save Changes

9. EMAIL_HOST_PASSWORD
   Valeur: [app-specific password Gmail]
   □ Save Changes
```

---

## 📊 VÉRIFIER LE BUILD

```
□ Onglet: "Logs"
□ ATTENDRE le message:
  ✅ "Build completed successfully!"

□ Si erreur, vérifier:
  - DATABASE_URL correct? Oui / Non
  - SECRET_KEY ajouté? Oui / Non
  - Toutes les variables présentes? Oui / Non

□ Une fois OK:
  - Voir le statut: "Live"
  - URL fournie: https://arecom-vet.onrender.com
```

---

## 🌍 ACCÈS INITIAL

```
□ Ouvrir dans navigateur:
  https://arecom-vet.onrender.com

□ Vérifier que la page charge

□ Admin initial:
  URL:      https://arecom-vet.onrender.com/admin
  Username: admin
  Password: admin123
  
□ Se connecter ✅ OUI / ❌ NON
```

---

## 🔑 CHANGER MOT DE PASSE ADMIN

```
□ Connecté au /admin avec admin/admin123

□ Click sur "admin" en haut à droite

□ Click: "Change password"

□ Entrer:
  Current password:    admin123
  New password:        _________________________
  Confirm password:    _________________________

□ Click: "Change password"

□ Se reconnecter avec le nouveau password ✅
```

---

## 🧪 TESTS FONCTIONNELS

```
Dans l'admin ou l'interface:

□ PAGE VET:
  - Créer un nouvel enregistrement VET
  - Ajouter des données
  - Sauvegarder
  - Vérifier que ça apparaît

□ PAGE STOCK:
  - Voir les catégories de vignettes
  - Vérifier les mouvements

□ PAGE ACTIVITES:
  - Créer une activité
  - Tester les formulaires

□ UPLOAD FICHIER:
  - Créer un VET ou Activité
  - Upload un document PDF
  - Vérifier que c'est sauvegardé

□ CSS/STATIC:
  - Vérifier que la page a du style (CSS chargé)
  - Pas de fichiers manquants (404)

□ LOGOUT/LOGIN:
  - Logout
  - Se reconnecter
  - Vérifier que la session fonctionne
```

---

## 📱 APPAREILS TESTÉS

```
Test sur différents appareils:

□ Desktop (Chrome):      OK / NON OK
□ Desktop (Firefox):     OK / NON OK
□ Desktop (Safari):      OK / NON OK
□ Mobile (Smartphone):   OK / NON OK
□ Tablet:                OK / NON OK

Notes:
_________________________________________________
_________________________________________________
```

---

## 💾 SAUVEGARDE & MAINTENANCE

```
IMMÉDIAT:
□ Créer un dossier "ARECOM_BACKUPS" sur votre PC

□ Sauvegarder DATABASE_URL dans:
  Fichier: ARECOM_BACKUPS/database_url.txt
  Contenu: [coller DATABASE_URL ici]

□ Sauvegarder SECRET_KEY dans:
  Fichier: ARECOM_BACKUPS/secret_key.txt
  Contenu: [coller SECRET_KEY ici]

MENSUEL:
□ Première du mois: Créer backup DE LA BD
  Commande: pg_dump "DATABASE_URL" > backup_202603.sql
  Fichier: ARECOM_BACKUPS/backup_202603.sql

□ Calendrier: Set reminder pour prochain backup

TOUS LES 90 JOURS (IMPORTANT SI FREE TIER):
□ Ouvrir: https://arecom-vet.onrender.com
  (Cela réinitialise la chrono d'inactivité)

□ Calendrier: Set reminder pour dans 90 jours
```

---

## 🎉 CÉLÉBRATION!

```
SI TOUT EST ✅:

□ Notifier l'équipe que le site est live
□ Documenter la date de déploiement: ______________
□ Envoyer le lien aux utilisateurs
□ Faire un test utilisateur final

EMAIL À ENVOYER:
═════════════════════════════════════════════════════
Subject: ARECOM est live! 🚀

Bienvenue sur la nouvelle version d'ARECOM!

URL:      https://arecom-vet.onrender.com
Admin:    https://arecom-vet.onrender.com/admin

Les données sont maintenant sauvegardées sur 
une base de données PostgreSQL sécurisée.

N'hésitez pas à tester!

═════════════════════════════════════════════════════
```

---

## 🆘 TROUBLESHOOTING RAPIDE

```
Site dit "502 Bad Gateway"?
□ Vérifier les logs Render
  Aller à: Render Dashboard → arecom-vet → Logs
  Chercher un message d'erreur rouge

Identifiants admin ne fonctionnent pas?
□ Vérifier DATABASE_URL est correct
□ Relancer le build: Manual Deploys

Fichiers statiques (CSS) manquants?
□ Relancer depuis: Manual Deploys → Deploy latest

Fichiers uploadés ne s'affichent pas?
□ C'est normal avec Render free tier
□ Solution: Upgrader à S3 (optionnel, $2/mois)

Besoin d'aide?
□ Voir: GUIDE_DEPLOIEMENT_RENDER.md (section Troubleshooting)
□ Voir: QUICK_START_RENDER.md (section "Si ça ne marche pas")
```

---

## 📝 NOTES PERSONNELLES

Espace pour vos notes:

```
Date du déploiement: ___________________

Problèmes rencontrés:
_________________________________________________
_________________________________________________
_________________________________________________

Solutions appliquées:
_________________________________________________
_________________________________________________
_________________________________________________

Contacts importants:
- Admin local: _________________________
- Email support: _________________________
- Render account: _________________________

URLs à retenir:
- Site: https://arecom-vet.onrender.com
- Admin: https://arecom-vet.onrender.com/admin
- Render: https://dashboard.render.com
- GitHub: https://github.com/AlMezui241/arecom-vet

Prochaines actions:
□ _________________________________________________
□ _________________________________________________
□ _________________________________________________
```

---

## ✨ HAPPY DEPLOYMENT!

**Time Elapsed**: _________ minutes  
**Status**: ✅ SUCCESS / ⚠️ ISSUES

**Témoignage du déploiement**:
_________________________________________________
_________________________________________________
_________________________________________________

---

**Date de ce déploiement**: ___________________
**Par**: ___________________
**Téléphone**: ___________________

**Backup sauvegardé?** OUI / NON  
**Équipe notifiée?** OUI / NON  
**Utilisateurs testés?** OUI / NON

---

**🎉 ARECOM EST MAINTENANT EN PRODUCTION! 🎉**

Gardez cette checklist pour la prochaine fois!

---

*Checklist ARECOM Deployment*  
*Created: 17 Mars 2026*  
*Print & Share!*
