from django import forms
from .models import Report, Adenda

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["contenido"]
        widgets = {
            "contenido": forms.Textarea(attrs={
                "rows": 18,
                "class": "w-full rounded border border-gray-300 text-gray-800 dark:text-gray-100 placeholder-gray-400 leading-relaxed tracking-wide focus:border-blue-500 focus:ring-blue-500 text-sm bg-white dark:bg-gray-900"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar atributo readonly si el instance ya está final
        inst = getattr(self, 'instance', None)
        if inst and getattr(inst, 'es_final', False):
            self.fields['contenido'].widget.attrs['readonly'] = True


class AdendaForm(forms.ModelForm):
    class Meta:
        model = Adenda
        fields = ["contenido"]
        widgets = {
            "contenido": forms.Textarea(attrs={
                "rows": 10,
                "class": "w-full rounded border border-gray-300 text-gray-800 dark:text-gray-100 placeholder-gray-400 leading-relaxed tracking-wide focus:border-blue-500 focus:ring-blue-500 text-sm bg-white dark:bg-gray-900"
            })
        }

    def clean_contenido(self):
        v = (self.cleaned_data.get('contenido') or '').strip()
        if not v:
            raise forms.ValidationError('La adenda no puede estar vacía.')
        return v
