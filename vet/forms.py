from django import forms
from django.forms import inlineformset_factory
from .models import VET, VETVignette, VETDocument


class VETForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        model = VET
        fields = [
            "numero_ordre_de_recette",
            "identification_de_l_exploitant_ou_raison_sociale",
            "region",
            "zone",
            "quartier",
            "longitude",
            "latitude",
            "numero_de_telephone",
            "email",
            "dossier_suivi_par",
            "frais_de_dossier_payes",
            "redevance_payee",
            "montant_de_la_redevance_annuelle",
            "date_d_emission_de_la_redevance_annuelle",
            "date_d_expiration_de_la_redevance_annuelle",
            "statut",
            "notes",
        ]
        widgets = {
            'date_d_emission_de_la_redevance_annuelle': forms.DateInput(attrs={'type': 'date'}),
            'date_d_expiration_de_la_redevance_annuelle': forms.DateInput(attrs={'type': 'date'}),
        }

class VETDocumentForm(forms.ModelForm):
    class Meta:
        model = VETDocument
        fields = ['fichier', 'type_document', 'description']

    def clean_fichier(self):
        """✅ FIX #3: Valider la taille du fichier avec message d'erreur clair"""
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            if fichier.size > VETDocument.MAX_FILE_SIZE:
                max_size_mb = VETDocument.MAX_FILE_SIZE / 1024 / 1024
                raise forms.ValidationError(
                    f"Fichier trop volumineux. Taille maximum: {max_size_mb:.0f} MB. "
                    f"Votre fichier fait {fichier.size / 1024 / 1024:.1f} MB."
                )
        return fichier

VETDocumentFormSet = inlineformset_factory(
    VET, VETDocument, form=VETDocumentForm, extra=1, can_delete=True
)

VETVignetteFormSet = inlineformset_factory(
    VET, VETVignette, fields=['categorie', 'quantite'], extra=1, can_delete=True
)
