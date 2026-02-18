from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import auth, firestore
from CURSO_ingles.firebase_config import initialize_firebase
from functools import wraps
import requests
import os

db = initialize_firebase()


# Registro de usuarios para ingresar al inicio de sesion 


def registro_usuario(request):
    mensaje = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = auth.create_user(
                email=email,
                password=password
            )

            db.collection('perfiles').document(user.uid).set({
                'email': email,
                'uid': user.uid,
                'rol': 'alumno',
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'registro.html')



# Erro del registro para iniciar sesion

def login_required_firebase(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if 'uid' not in request.session:
            messages.warning(request, 'Debes iniciar sesión')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return _wrapped_view



# LOGIN - inicio de sesion despues de registrarse correctamente y el logout o cerrar la sesion

def iniciar_sesion(request):

    if 'uid' in request.session:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200:

                request.session['uid'] = data['localId']
                request.session['email'] = data['email']

                messages.success(request, "Bienvenido al curso")
                return redirect('dashboard')

            else:
                messages.error(request, "Credenciales incorrectas")

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'login.html')


def cerrar_sesion(request):
    request.session.flush()
    return redirect('login')



# Pagina principal donde el usuarios puede ver el progreso y leccion que ha tenido,tuvo o lleva a cabo

@login_required_firebase
def dashboard(request):

    uid = request.session.get('uid')
    datos_usuario = {}

    try:
        doc_ref = db.collection('perfiles').document(uid)
        doc = doc_ref.get()

        if doc.exists:
            datos_usuario = doc.to_dict()

    except Exception as e:
        messages.error(request, f"Error BD: {e}")

    # Crear listas para lecciones del usuario
    
    lecciones = []
    cursos_activos = []
    cursos_pendientes = []
    cursos_disponibles = []

    if request.method == 'GET' and request.GET.get('titulo') and request.GET.get('descripcion'):
        titulo = request.GET.get('titulo')
        descripcion = request.GET.get('descripcion')

        if titulo and descripcion:
            try:
                db.collection('lecciones').add({
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'estado': 'Pendiente',
                    'usuario_id': uid,

                })

                messages.success(request, ".")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f". {e}")
        else:
            messages.error(request, "requerimientos")

    return render(request, 'dashboard.html', {
        'datos': datos_usuario,
        'lecciones': lecciones,
        'cursos_activos': cursos_activos,
        'cursos_pendientes': cursos_pendientes,
        'cursos_disponibles': cursos_disponibles
    })

