# 📊 ANALYSE APPROFONDIE - FONCTIONNALITÉS VET → ENTITÉ

## 1️⃣ FONCTIONNALITÉS CLÉS IDENTIFIÉES DANS VET

### A. VALIDATIONS MÉTIER
| Validation | Code VET | À Adapter |
|-----------|----------|-----------|
| GPS XOR | Si lat → long DOIT exister | ✅ Même pour entité |
| Dates | expiration >= emission | ✅ Adapter pour type d'entité |
| Montants | >= 0 (DecimalField) | ✅ Déjà presente |
| Téléphone | Regex: `^\+?[0-9\s\-\(\)]{7,20}$` | ✅ À ajouter |
| Fichiers | Max 10MB + whitelist extensions | ✅ À ajouter |

### B. CHAMPS DE PAIEMENT & SUIVI
```python
# VET a:
frais_de_dossier_payes = BooleanField()      # Booléen
redevance_payee = BooleanField()             # Booléen
dossier_suivi_par = CharField()              # Personne responsable
statut = Choice('actif', 'inactif')          # État

# Adapté pour ENTITÉ:
frais_instruction_payes = BooleanField()     # À ajouter
frais_exploitation_payes = BooleanField()    # À ajouter
contribution_payee = BooleanField()          # À ajouter
statut = Choice('actif', 'inactif')          # Déjà present
```

### C. PROPRIÉTÉ CALCULÉE
```python
# VET montant_total_a_recouvrer =
#   redevance_annuelle
#   + frais_dossier (50,000 si non payés)
#   + sum(vignettes)

# ENTITÉ montant_total_redevance =
#   frais_exploitation_annuel (si présent)
#   + contribution_fonds_universel (si présent)
#   + frais_instruction_dossier (si présent)
```

### D. RELATIONS & FORMSETS INLINE
```python
# VET a:
VETVignette (inline formset) → Quantités par catégorie
VETDocument (inline formset) → Documents attachés

# ENTITÉ a:
EntiteDocument (inline formset) → Documents attachés
EntiteVignette (OPTIONNEL FUTUR) → Pour gérer vignettes/frais
```

### E. AUDIT & TRAÇABILITÉ
```python
# VET a AuditLog avec:
- user (Utilisateur ayant fait l'action)
- vet (Référence)
- action ('create', 'update', 'delete')
- details (Changements)
- timestamp (auto_now_add)

# ENTITÉ aura: EntiteAuditLog (même structure)
```

### F. DATETIMES & TIMESTAMPS
```python
# VET:
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)

# ENTITÉ: Déjà présent
created_at, updated_at ✅
```

---

## 2️⃣ FORMULAIRES VET - FEATURES

### VETForm
```python
# ✅ Auto-styling Bootstrap
for name, field in self.fields.items():
    - CheckboxInput → form-check-input
    - Select → form-select
    - Autres → form-control

# ✅ DateInput avec type='date' (HTML5)
'date_d_emission': DateInput(attrs={'type': 'date'})
'date_d_expiration': DateInput(attrs={'type': 'date'})

# ✅ Custom clean_fichier()
# Valide: Max 10MB + affiche message d'erreur clair
```

---

## 3️⃣ IMPLÉMENTATION PLAN POUR ENTITÉ

### Phase 1: MODELS (activites/models.py)
- [ ] Ajouter champs paiement (frais_instruction_payes, frais_exploitation_payes, contribution_payee)
- [ ] Ajouter champs suivi (dossier_suivi_par, statut='actif'/'inactif')
- [ ] Ajouter validation GPS XOR dans clean()
- [ ] Ajouter validation Téléphone Regex
- [ ] Ajouter validation dates (expiration >= emission)
- [ ] Ajouter EntiteAuditLog model
- [ ] Adapter propriété montant_total_redevance pour NULL checks

### Phase 2: FORMS (activites/forms.py)
- [ ] Créer EntiteForm avec VETForm-style Bootstrap auto-styling
- [ ] Clean methods pour validations custom
- [ ] DateInput type='date'
- [ ] EntiteDocumentForm avec clean_fichier()
- [ ] EntiteDocumentFormSet inline

### Phase 3: VIEWS (activites/views.py)
- [ ] Ajouter audit trail on create/update
- [ ] Ajouter formset documents dans CreateView/UpdateView
- [ ] Afficher montant_total_redevance dans contexte

### Phase 4: TEMPLATES
- [ ] entite_form.html avec formsets documents
- [ ] entite_detail.html affichant paiements + montant
- [ ] activites/components/Payment status badge

---

## 4️⃣ CONSIDÉRATIONS SPÉCIALES

### VET vs ENTITÉ - Différences
| Aspect | VET | ENTITÉ | Adaptation |
|--------|-----|--------|-----------|
| Redevance | OBLIGATOIRE fixe | OPTIONNEL par type | NULL checks |
| Vignettes | N:M requis | OPTIONNEL futur | Laisser la logique |
| Frais dossier | FIXE 50,000 | VARIABLE | Garder comme field |
| Types | UNI (juste VET) | MULTI (4+ types) | Validation conditionnelle |

### Validation Conditionnelle par TypeEntite
```python
# Dans Entite.clean():
if self.type_entite.a_frais_exploitation and not self.frais_exploitation_annuel:
    raise ValidationError("Frais exploitation requis pour ce type")
```

---

## 5️⃣ TIMELINE ESTIMÉE

- **Phase 1 (Models)**: 30 min
- **Phase 2 (Forms)**: 30 min
- **Phase 3 (Views)**: 20 min
- **Phase 4 (Templates)**: 30 min
- **Testing**: 20 min

**Total: ~2h30**
