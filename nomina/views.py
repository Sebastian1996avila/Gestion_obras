from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse  # Añadido para API
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from usuarios.models import Usuario
from .models import Nomina
from .forms import NominaForm
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view  # Añadido para API
from rest_framework.response import Response  # Añadido para API
from django.core.exceptions import ValidationError

@login_required
def index(request):
    nominas = Nomina.objects.all().order_by('-fecha_creacion')
    context = {
        'nominas': nominas,
        'api_url': reverse('nomina:api-nomina-list')  # URL para la API
    }
    return render(request, 'nomina/index.html', context)

@login_required
@permission_required('usuarios.gestionar_nomina', raise_exception=True)
def registrar_nomina(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            try:
                nomina = calcular_totales_nomina(form, request.user)
                nomina.save()
                messages.success(request, 'Nómina registrada exitosamente.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect_url': reverse('nomina:index')})
                return redirect('nomina:index')
                
            except Exception as e:
                error_msg = f'Error al guardar la nómina: {str(e)}'
                messages.error(request, error_msg)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
        else:
            error_msg = 'Por favor corrija los errores en el formulario.'
            messages.error(request, error_msg)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = NominaForm()
    
    return render(request, 'nomina/registrar.html', {'form': form})

# Función reusable para cálculo de totales
def calcular_totales_nomina(form, user):
    try:
        nomina = form.save(commit=False)
        sueldo_base = Decimal(str(nomina.sueldo_base))
        horas_extras = Decimal(str(nomina.horas_extras))
        bonificaciones = Decimal(str(nomina.bonificaciones))
        deducciones = Decimal(str(nomina.deducciones))
        
        # Validar valores negativos
        if any(x < 0 for x in [sueldo_base, horas_extras, bonificaciones, deducciones]):
            raise ValidationError('Los valores no pueden ser negativos')
        
        # Calcular valor hora normal
        valor_hora_normal = sueldo_base / (Decimal('30') * Decimal('8'))
        valor_horas_extras = horas_extras * valor_hora_normal * Decimal('1.5')
        
        # Calcular total
        nomina.total = sueldo_base + valor_horas_extras + bonificaciones - deducciones
        
        # Validar que el total no sea negativo
        if nomina.total < 0:
            raise ValidationError('El total no puede ser negativo')
            
        nomina.ultimo_cambio_por = user
        return nomina
    except Exception as e:
        raise ValidationError(f'Error al calcular totales: {str(e)}')

@login_required
def detalle_nomina(request, nomina_id):
    nomina = get_object_or_404(Nomina, id=nomina_id)
    return render(request, 'nomina/detalle.html', {'nomina': nomina})

# Vista API para detalle (nueva)
@api_view(['GET'])
def api_detalle_nomina(request, pk):
    nomina = get_object_or_404(Nomina, id=pk)
    data = {
        'id': nomina.id,
        'empleado': nomina.empleado.get_full_name(),
        'sueldo_base': float(nomina.sueldo_base),
        'total': float(nomina.total),
        # ... otros campos
    }
    return Response(data)

@login_required
@permission_required('usuarios.gestionar_nomina', raise_exception=True)
def editar_nomina(request, nomina_id):
    nomina = get_object_or_404(Nomina, id=nomina_id)
    if request.method == 'POST':
        form = NominaForm(request.POST, instance=nomina)
        if form.is_valid():
            try:
                nomina = calcular_totales_nomina(form, request.user)
                nomina.save()
                messages.success(request, 'Nómina actualizada exitosamente.')
                return redirect('nomina:index')
            except Exception as e:
                messages.error(request, f'Error al actualizar la nómina: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = NominaForm(instance=nomina)
    
    return render(request, 'nomina/editar.html', {'form': form, 'nomina': nomina})

@login_required
@permission_required('usuarios.gestionar_nomina', raise_exception=True)
def eliminar_nomina(request, nomina_id):
    nomina = get_object_or_404(Nomina, id=nomina_id)
    if request.method == 'POST':
        try:
            nomina.delete()
            messages.success(request, 'Nómina eliminada exitosamente.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
        except Exception as e:
            error_msg = f'Error al eliminar la nómina: {str(e)}'
            messages.error(request, error_msg)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
        return redirect('nomina:index')
    return render(request, 'nomina/eliminar.html', {'nomina': nomina})

@login_required
def reporte_nomina(request):
    nominas = Nomina.objects.all().order_by('-fecha_creacion')
    return render(request, 'nomina/reporte.html', {'nominas': nominas})