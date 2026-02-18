from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('', views.iniciar_sesion, name='login_index'),
    path('registro/', views.registro_usuario, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('editar/<str:leccion_id>/', views.editar_leccion, name='editar_leccion'),
    path('eliminar/<str:leccion_id>/', views.eliminar_leccion, name='eliminar_leccion'),
]