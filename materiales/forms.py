# materiales/forms.py
from django import forms
from .models import Material, CategoriaMaterial, Proveedor

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'cantidad',
            'unidad_medida',
            'precio_unitario',
            'stock_minimo',
            'ubicacion',
            'proveedor'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'cantidad': forms.NumberInput(attrs={'min': 0}),
            'precio_unitario': forms.NumberInput(attrs={'min': 0}),
            'stock_minimo': forms.NumberInput(attrs={'min': 0}),
        }

class CategoriaMaterialForm(forms.ModelForm):
    class Meta:
        model = CategoriaMaterial
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'color',
            'orden',
            'activa'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'orden': forms.NumberInput(attrs={'min': 0}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre',
            'contacto',
            'telefono',
            'email',
            'direccion'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }