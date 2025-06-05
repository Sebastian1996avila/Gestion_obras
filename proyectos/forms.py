from django import forms
from .models import Proyecto
from django.core.validators import MinValueValidator
from decimal import Decimal

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'presupuesto',
            'activo',
            'foto',
            'responsable',
            'asignados'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'presupuesto': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def clean_presupuesto(self):
        presupuesto = self.cleaned_data.get('presupuesto')
        if presupuesto is not None and presupuesto < 0:
            raise forms.ValidationError('El presupuesto no puede ser negativo')
        return presupuesto