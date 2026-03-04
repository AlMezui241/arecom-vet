from django import forms
from .models import MouvementStock, VignetteCategory

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['category', 'quantite', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Commande n°123 reçue le 27/02'}),
            'quantite': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
