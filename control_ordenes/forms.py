from django import forms
from .models import OrdenMedica

class OrdenMedicaForm(forms.ModelForm):
    class Meta:
        model = OrdenMedica
        fields = ['identificador_paciente', 'dias_validez']
        labels = {
            'identificador_paciente': 'Identificador del paciente',
            'dias_validez': 'Válido por',
        }
        widgets = {
            'identificador_paciente': forms.TextInput(attrs={'class': 'form-control'}),
            'dias_validez': forms.Select(choices=[(30, "30 días"), (60, "60 días")], attrs={'class': 'form-select'}),
        }
