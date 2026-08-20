from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import TaskForm, CustomSignupForm
from .models import Task, VectorDesign
from allauth.account.models import EmailAddress
from django.contrib.auth.decorators import login_required
from .models import Task, VectorDesign, Purchase
import os
import json
from django.http import JsonResponse
from django.http import FileResponse
from .models import Course, CoursePurchase
from decimal import Decimal
from django.views.decorators.http import require_POST
import requests

def get_paypal_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    response = requests.post(
        url,
        auth=(
            os.getenv("PAYPAL_CLIENT_ID"),
            os.getenv("PAYPAL_SECRET")
        ),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={
            "grant_type": "client_credentials"
        },
        timeout=15
    )

    response.raise_for_status()

    return response.json()["access_token"]

def paypal_test(request):
    try:
        token = get_paypal_access_token()

        return JsonResponse({
            "status": "ok",
            "message": "Conexión con PayPal Sandbox funcionando"
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@login_required
@require_POST
def guardar_compra(request):
    try:
        data = json.loads(request.body)

        design = get_object_or_404(
            VectorDesign,
            id=data['design_id']
        )

        paypal_order_id = data.get('paypal_order_id')

        if not paypal_order_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Falta el ID de la orden de PayPal.'
            }, status=400)

        # Obtener token de PayPal
        access_token = get_paypal_access_token()

        # Consultar la orden directamente a PayPal
        paypal_response = requests.get(
            f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        paypal_response.raise_for_status()

        paypal_order = paypal_response.json()

        # Verificar que PayPal considera la orden completada
        if paypal_order.get('status') != 'COMPLETED':
            return JsonResponse({
                'status': 'error',
                'message': 'El pago todavía no está completado.'
            }, status=400)

        # Obtener el precio realmente registrado en PayPal
        purchase_units = paypal_order.get('purchase_units', [])

        if not purchase_units:
            return JsonResponse({
                'status': 'error',
                'message': 'La orden de PayPal no contiene información de compra.'
            }, status=400)

        paypal_amount = Decimal(
            purchase_units[0]['amount']['value']
        )

        # Comparar con el precio de nuestra base de datos
        if paypal_amount != design.price:
            return JsonResponse({
                'status': 'error',
                'message': 'El precio de la orden no coincide con el producto.'
            }, status=400)

        # Registrar la compra
        purchase, created = Purchase.objects.get_or_create(
            user=request.user,
            design=design,
            defaults={
                'paypal_order_id': paypal_order_id,
                'amount': design.price
            }
        )

        if not created:
            purchase.download_count += 1
            purchase.paypal_order_id = paypal_order_id
            purchase.save()

        return JsonResponse({
            'status': 'ok'
        })

    except requests.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': 'No se pudo verificar el pago con PayPal.'
        }, status=502)

    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({
            'status': 'error',
            'message': 'Datos de compra inválidos.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='signin')
def vector_detail(request, design_id):
    design = get_object_or_404(VectorDesign, id=design_id)

    return render(request, 'my_page/vector_detail.html', {
        'design': design,
        'paypal_client_id': os.getenv('PAYPAL_CLIENT_ID')
    })


@login_required(login_url='signin')
def download_vector(request, design_id):
    design = get_object_or_404(VectorDesign, id=design_id)

    purchase = Purchase.objects.filter(
        user=request.user,
        design=design
    ).first()

    if not purchase:
        messages.error(
            request,
            "Debes comprar este diseño antes de descargarlo."
        )
        return redirect('vector_detail', design_id=design.id)

    if not design.vector_file:
        messages.error(
            request,
            "Este diseño no tiene archivo disponible."
        )
        return redirect('vector_detail', design_id=design.id)

    purchase.download_count += 1
    purchase.save(update_fields=['download_count'])

    return FileResponse(
        design.vector_file.open('rb'),
        as_attachment=True
    )
User = get_user_model()


def index(request):
    return render(request, 'my_page/index.html')


def inscripcion(request):
    return render(request, 'my_page/inscripcion.html')


def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (ObjectDoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'my_page/activation_success.html')
    else:
        return render(request, 'my_page/activation_failed.html')


def home(request):
    return render(request, 'my_page/home.html')


@login_required
def tasks(request):
    if not request.user.is_active:
        messages.warning(request, "Debes verificar tu correo para acceder a las tareas.")
        return render(request, 'my_page/verify_email.html')

    tasks = Task.objects.filter(user=request.user, datacompleted__isnull=True)
    return render(request, 'my_page/tasks.html', {'tasks': tasks})


@login_required
def resend_email_verification(request):
    """Reenvía el correo de verificación usando el método actualizado de django-allauth"""
    email_address, created = EmailAddress.objects.get_or_create(
        user=request.user,
        email=request.user.email
    )

    if not email_address.verified:
        email_address.send_confirmation(request)
        messages.success(
            request,
            "✅ Se ha reenviado el correo de verificación. Revisa tu bandeja de entrada."
        )
    else:
        messages.info(request, "📧 Tu correo ya está verificado.")

    return redirect("tasks")


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        else:
            return render(request, 'my_page/create_task.html', {'form': form, 'error': 'Datos inválidos'})

    return render(request, 'my_page/create_task.html', {'form': TaskForm()})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    return render(request, 'my_page/task_detail.html', {'task': task})


def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            return render(request, 'my_page/signin.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña incorrectos'
            })

    next_url = request.GET.get('next', '')
    return render(request, 'my_page/signin.html', {'form': AuthenticationForm(), 'next': next_url})


def signup(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            EmailAddress.objects.add_email(request, user, user.email, confirm=True)

            request.session['next_url'] = next_url

            return render(request, 'my_page/confirmation_pending.html')
    else:
        form = CustomSignupForm()

    return render(request, "my_page/signup.html", {"form": form, "next": next_url})


def email_confirmed_view(request):
    return render(request, 'account/email_confirmed.html')


def vector_gallery(request):
    designs = VectorDesign.objects.all()
    return render(request, 'my_page/vector_gallery.html', {'designs': designs})




@login_required
def perfil(request):
    compras = Purchase.objects.filter(user=request.user).order_by('-purchased_at')
    return render(request, 'my_page/perfil.html', {
        'user': request.user,
        'compras': compras
    })



@login_required(login_url='signin')
def curso_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'my_page/curso_detail.html', {
        'course': course,
        'paypal_client_id': os.getenv('PAYPAL_CLIENT_ID')
    })


@login_required
@require_POST
def guardar_compra_curso(request):
    try:
        data = json.loads(request.body)

        course = get_object_or_404(
            Course,
            id=data['course_id']
        )

        paypal_order_id = data.get('paypal_order_id')

        if not paypal_order_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Falta el ID de la orden de PayPal.'
            }, status=400)

        # Obtener token de PayPal
        access_token = get_paypal_access_token()

        # Consultar la orden directamente a PayPal
        paypal_response = requests.get(
            f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        paypal_response.raise_for_status()

        paypal_order = paypal_response.json()

        # Verificar que PayPal considera la orden completada
        if paypal_order.get('status') != 'COMPLETED':
            return JsonResponse({
                'status': 'error',
                'message': 'El pago todavía no está completado.'
            }, status=400)

        purchase_units = paypal_order.get('purchase_units', [])

        if not purchase_units:
            return JsonResponse({
                'status': 'error',
                'message': 'La orden de PayPal no contiene información de compra.'
            }, status=400)

        paypal_amount = Decimal(
            purchase_units[0]['amount']['value']
        )

        # Comprobar que el precio pagado coincide
        # con el precio del curso
        if paypal_amount != course.price:
            return JsonResponse({
                'status': 'error',
                'message': 'El precio de la orden no coincide con el curso.'
            }, status=400)

        # Registrar la compra solamente después
        # de verificarla con PayPal
        CoursePurchase.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'paypal_order_id': paypal_order_id,
                'amount': course.price
            }
        )

        return JsonResponse({
            'status': 'ok'
        })

    except requests.RequestException:
        return JsonResponse({
            'status': 'error',
            'message': 'No se pudo verificar el pago con PayPal.'
        }, status=502)

    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({
            'status': 'error',
            'message': 'Datos de compra inválidos.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def ver_curso(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    tiene_acceso = CoursePurchase.objects.filter(user=request.user, course=course).exists()

    if not tiene_acceso:
        messages.error(request, "Debes comprar este curso para acceder.")
        return redirect('curso_detail', course_id=course.id)

    return render(request, 'my_page/ver_curso.html', {'course': course})


@login_required
def perfil(request):
    compras = Purchase.objects.filter(user=request.user).order_by('-purchased_at')
    cursos_comprados = CoursePurchase.objects.filter(user=request.user).order_by('-purchased_at')
    return render(request, 'my_page/perfil.html', {
        'user': request.user,
        'compras': compras,
        'cursos_comprados': cursos_comprados
    })