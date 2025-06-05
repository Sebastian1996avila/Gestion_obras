from django import forms
from .models import Nomina
from decimal import Decimal
from datetime import datetime
import calendar

class NominaForm(forms.ModelForm):
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese un comentario (opcional)'
        }),
        required=False
    )

    class Meta:
        model = Nomina
        fields = [
            'empleado',
            'periodo',
            'dias_trabajados',
            'sueldo_base',
            'horas_extras',
            'bonificaciones',
            'deducciones',
            'estado',
            'comentario'
        ]
        widgets = {
            'empleado': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Seleccione un empleado'
            }),
            'periodo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM',
                'pattern': r'\d{4}-\d{2}'
            }),
            'dias_trabajados': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '31',
                'placeholder': '0.00'
            }),
            'sueldo_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'horas_extras': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'bonificaciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'deducciones': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def clean_periodo(self):
        periodo = self.cleaned_data['periodo']
        try:
            datetime.strptime(periodo, '%Y-%m')
        except ValueError:
            raise forms.ValidationError('El período debe tener el formato YYYY-MM')
        return periodo

    def clean_dias_trabajados(self):
        dias = self.cleaned_data['dias_trabajados']
        periodo = self.cleaned_data.get('periodo')
        
        if periodo:
            try:
                year, month = map(int, periodo.split('-'))
                dias_en_mes = calendar.monthrange(year, month)[1]
                if dias > dias_en_mes:
                    raise forms.ValidationError(
                        f'Los días trabajados no pueden ser mayores a {dias_en_mes} para el mes seleccionado'
                    )
            except (ValueError, AttributeError):
                pass
        
        if dias <= 0:
            raise forms.ValidationError('Los días trabajados deben ser mayores a 0')
        
        return dias

    def clean_sueldo_base(self):
        sueldo = self.cleaned_data['sueldo_base']
        if sueldo <= 0:
            raise forms.ValidationError('El sueldo base debe ser mayor a 0')
        return sueldo

    def clean_horas_extras(self):
        horas = self.cleaned_data['horas_extras']
        dias = self.cleaned_data.get('dias_trabajados', 0)
        
        if horas < 0:
            raise forms.ValidationError('Las horas extras no pueden ser negativas')
        
        max_horas = dias * 4  # Máximo 4 horas extras por día
        if horas > max_horas:
            raise forms.ValidationError(
                f'Las horas extras no pueden ser mayores a {max_horas} para {dias} días trabajados'
            )
        
        return horas

    def clean(self):
        cleaned_data = super().clean()
        try:
            sueldo_base = cleaned_data.get('sueldo_base', Decimal('0'))
            horas_extras = cleaned_data.get('horas_extras', Decimal('0'))
            bonificaciones = cleaned_data.get('bonificaciones', Decimal('0'))
            deducciones = cleaned_data.get('deducciones', Decimal('0'))

            # Calcular el valor de las horas extras (1.5 veces el valor hora normal)
            valor_hora_normal = sueldo_base / (Decimal('30') * Decimal('8'))  # 30 días, 8 horas por día
            valor_horas_extras = horas_extras * valor_hora_normal * Decimal('1.5')

            # Calcular el total
            cleaned_data['total'] = sueldo_base + valor_horas_extras + bonificaciones - deducciones
        except Exception as e:
            raise forms.ValidationError(f'Error al calcular el total: {str(e)}')
        
        return cleaned_data 