from django import forms
from django.forms import inlineformset_factory
from .models import Activite, ActiviteDocument


class ActiviteForm(forms.ModelForm):
    """✅ Formulaire Entité - Inspiré de VETForm avec Bootstrap styling auto"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Auto-styling Bootstrap comme VETForm
        for name, field in self.fields.items():
            widget = field.widget
            base = widget.attrs.get("class", "")

            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs["class"] = (base + " form-check-input").strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = (base + " form-select").strip()
            else:
                widget.attrs["class"] = (base + " form-control").strip()

    class Meta:
        model = Activite
        fields = [
            'type_activite',
            'numero',
            'nom_activite',
            'province',
            'localite',
            'quartier_zone',
            'telephone',
            'email',
            'latitude',
            'longitude',
            'precision_gps',
            'frais_instruction_dossier',
            'frais_exploitation_annuel',
            'contribution_fonds_universel',
            'frais_de_dossier_payes',
            'redevance_payee',
            'dossier_suivi_par',
            'presence_facture',
            'presence_autorisation',
            'presence_homologation',
            'date_emission_redevance',
            'date_expiration_redevance',
            'statut_autorisation',
            'contrepartie_financiere',
            'statut',
            'observation',
        ]

        # ✅ DateInput avec type='date' (HTML5) comme VET
        widgets = {
            'date_emission_redevance': forms.DateInput(attrs={'type': 'date'}),
            'date_expiration_redevance': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_telephone(self):
        """✅ Valider le téléphone - Regex déjà dans model + message clair"""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            import re
            pattern = r"^\+?[0-9\s\-\(\)]{7,20}$"
            if not re.match(pattern, telephone):
                raise forms.ValidationError(
                    "Format de numéro invalide. Exemples: +243123456789 ou (243) 123-456789"
                )
        return telephone


class ActiviteDocumentForm(forms.ModelForm):
    """✅ Formulaire document - Validation fichier comme VETDocumentForm"""

    class Meta:
        model = ActiviteDocument
        fields = ['fichier', 'type_document', 'description']
        widgets = {
            # ✅ Ajoute l'attribut capture pour mobile (Identique à VET)
            'fichier': forms.FileInput(attrs={'capture': 'environment'}),
        }

    def clean_fichier(self):
        """✅ FIX #3: Valider la taille du fichier avec message d'erreur clair (comme VET)"""
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
            if fichier.size > MAX_FILE_SIZE:
                max_size_mb = MAX_FILE_SIZE / 1024 / 1024
                raise forms.ValidationError(
                    f"Fichier trop volumineux. Taille maximum: {max_size_mb:.0f} MB. "
                    f"Votre fichier fait {fichier.size / 1024 / 1024:.1f} MB."
                )
        return fichier


# ✅ Formsets inline pour documents (comme VET)
ActiviteDocumentFormSet = inlineformset_factory(
    Activite, ActiviteDocument, form=ActiviteDocumentForm, extra=1, can_delete=True
)
