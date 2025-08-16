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
            'identificador_paciente': forms.TextInput(attrs={
                'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mt-2 mb-4',
            }),
            'dias_validez': forms.Select(choices=[(30, "30 días"), (60, "60 días"), (90, "90 días")], attrs={
                'class': 'border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mt-2 mb-4',
            }),
        }


class OrdenMedicaFiltroForm(forms.Form):
    identificador = forms.CharField(
        label="Identificador",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar identificador',
            'class': 'form-control'
        })
    )
    fecha_emision = forms.DateField(
        label="Fecha de emisión",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    fecha_vencimiento = forms.DateField(
        label="Fecha de vencimiento",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
