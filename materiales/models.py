# materiales/models.py
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.utils import timezone

class CategoriaMaterial(models.Model):
    codigo = models.CharField(max_length=10, unique=True, null=True, blank=True, help_text="Código único para identificar la categoría")
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#000000", help_text="Color en formato hexadecimal para identificar la categoría")
    orden = models.IntegerField(default=0, help_text="Orden de visualización de la categoría")
    activa = models.BooleanField(default=True, help_text="Indica si la categoría está activa")

    def __str__(self):
        return f"{self.codigo or ''} - {self.nombre}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código automático si no se proporciona uno
            ultima_categoria = CategoriaMaterial.objects.order_by('-id').first()
            if ultima_categoria:
                ultimo_numero = int(ultima_categoria.codigo[3:]) if ultima_categoria.codigo and ultima_categoria.codigo.startswith('CAT') else 0
                self.codigo = f'CAT{str(ultimo_numero + 1).zfill(3)}'
            else:
                self.codigo = 'CAT001'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Categoría de Material'
        verbose_name_plural = 'Categorías de Materiales'
        ordering = ['orden', 'nombre']

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.fecha_creacion:
            self.fecha_creacion = timezone.now()
        self.fecha_actualizacion = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

class Material(models.Model):
    UNIDADES_MEDIDA = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('m', 'Metros'),
        ('cm', 'Centímetros'),
        ('m2', 'Metros cuadrados'),
        ('m3', 'Metros cúbicos'),
        ('un', 'Unidad'),
        ('pkg', 'Paquete'),
    ]

    codigo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        CategoriaMaterial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    unidad_medida = models.CharField(
        max_length=5,
        choices=UNIDADES_MEDIDA,
        default='un'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materiales'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['codigo']

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código automático si no se proporciona uno
            ultimo_material = Material.objects.order_by('-id').first()
            if ultimo_material:
                ultimo_numero = int(ultimo_material.codigo[3:]) if ultimo_material.codigo.startswith('MAT') else 0
                self.codigo = f'MAT{str(ultimo_numero + 1).zfill(3)}'
            else:
                self.codigo = 'MAT001'
        super().save(*args, **kwargs)

@receiver(post_migrate)
def crear_categoria_default(sender, **kwargs):
    if sender.name == 'materiales':
        CategoriaMaterial.objects.get_or_create(
            nombre="Sin categoría",
            defaults={
                'codigo': 'CAT000',
                'descripcion': 'Categoría por defecto para materiales sin categoría asignada',
                'color': '#808080'
            }
        )