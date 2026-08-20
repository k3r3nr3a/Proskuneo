from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from my_page import views
from my_page.views import email_confirmed_view

urlpatterns = [
    path('', views.index, name='index'),  # Ruta principal
    path('inscripcion/', views.inscripcion, name='inscripcion'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('signout/', views.signout, name='signout'),
    path('signin/', views.signin, name='signin'),
    path('perfil/', views.perfil, name='perfil'),
    path('guardar-compra/', views.guardar_compra, name='guardar_compra'),
    path('curso/<int:course_id>/', views.curso_detail, name='curso_detail'),
    path('guardar-compra-curso/', views.guardar_compra_curso, name='guardar_compra_curso'),
    path('curso/<int:course_id>/ver/', views.ver_curso, name='ver_curso'),
    path('paypal-test/', views.paypal_test, name='paypal_test'),

    # Django Allauth urls
    path('accounts/', include('allauth.urls')),
    
    # Activación de cuenta
    path('reenviar-verificacion/', views.resend_email_verification, name='resend_email_verification'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate_user'),
    path('email-confirmed/', email_confirmed_view, name='email_confirmed'),

    # Galería de vectores
    path('vectores/', views.vector_gallery, name='vector_gallery'),
    path('vectores/<int:design_id>/', views.vector_detail, name='vector_detail'),
]

# Configuración para servir archivos estáticos en modo desarrollo
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


