# materiales/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Material, CategoriaMaterial, Proveedor
from .forms import MaterialForm, CategoriaMaterialForm, ProveedorForm

def lista_materiales(request):
    materiales = Material.objects.all()
    return render(request, 'materiales/lista.html', {'materiales': materiales})

def crear_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save()
            messages.success(request, 'Material creado exitosamente.')
            return redirect('materiales:detalle', pk=material.pk)
    else:
        form = MaterialForm()
    return render(request, 'materiales/crear.html', {'form': form})

def detalle_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'materiales/detalle.html', {'material': material})

def editar_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material actualizado exitosamente.')
            return redirect('materiales:detalle', pk=material.pk)
    else:
        form = MaterialForm(instance=material)
    return render(request, 'materiales/editar.html', {'form': form})

def eliminar_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material eliminado exitosamente.')
        return redirect('materiales:lista')
    return render(request, 'materiales/eliminar.html', {'material': material})