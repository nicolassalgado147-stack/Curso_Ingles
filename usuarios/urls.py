from django.urls import path
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='login'),
    path('registro/', views.registro_usuario, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('lecciones/', views.listar_lecciones, name='listar_lecciones'),
    path('crear-leccion/', views.crear_leccion, name='crear_leccion'),
    path('editar-leccion/<str:leccion_id>/', views.editar_leccion, name='editar_leccion'),
    path('eliminar-leccion/<str:leccion_id>/', views.eliminar_leccion, name='eliminar_leccion'),
]
