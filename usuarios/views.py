from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import auth, firestore
from CURSO_ingles.firebase_config import initialize_firebase
from functools import wraps
import requests
import os

db = initialize_firebase()

# ==============================
# ✅ REGISTRO
# ==============================
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

            mensaje = "Alumno registrado correctamente"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'registro.html', {'mensaje': mensaje})


# ==============================
# ✅ DECORADOR LOGIN
# ==============================
def login_required_firebase(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if 'uid' not in request.session:
            messages.warning(request, 'Debes iniciar sesión')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# ==============================
# ✅ LOGIN
# ==============================
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


# ==============================
# ✅ LOGOUT
# ==============================
def cerrar_sesion(request):
    request.session.flush()
    return redirect('login')


# ==============================
# ✅ DASHBOARD
# ==============================
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

    return render(request, 'dashboard.html', {'datos': datos_usuario})


# ============================================================
# ============================================================
# 🔥🔥🔥 CRUD DE LECCIONES (CURSO DE INGLÉS) 🔥🔥🔥
# ============================================================
# ============================================================

# ✅ LISTAR LECCIONES
@login_required_firebase
def listar_lecciones(request):

    uid = request.session.get('uid')

    lecciones_ref = db.collection('lecciones') \
        .where('usuario_id', '==', uid) \
        .stream()

    lecciones = []

    for lec in lecciones_ref:
        data = lec.to_dict()
        data['id'] = lec.id
        lecciones.append(data)

    return render(request, 'listar_lecciones.html', {'lecciones': lecciones})


# ✅ CREAR LECCIÓN
@login_required_firebase
def crear_leccion(request):

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')

        uid = request.session.get('uid')

        db.collection('lecciones').add({
            'titulo': titulo,
            'descripcion': descripcion,
            'estado': 'Pendiente',
            'usuario_id': uid,
            'fecha_creacion': firestore.SERVER_TIMESTAMP
        })

        messages.success(request, "Lección creada correctamente")
        return redirect('listar_lecciones')

    return render(request, 'crear_leccion.html')


# ✅ EDITAR LECCIÓN
@login_required_firebase
def editar_leccion(request, leccion_id):

    leccion_ref = db.collection('lecciones').document(leccion_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')

        leccion_ref.update({
            'titulo': titulo,
            'descripcion': descripcion,
            'estado': estado
        })

        messages.success(request, "Lección actualizada")
        return redirect('listar_lecciones')

    leccion = leccion_ref.get().to_dict()
    leccion['id'] = leccion_id

    return render(request, 'editar_leccion.html', {'leccion': leccion})


# ✅ ELIMINAR LECCIÓN
@login_required_firebase
def eliminar_leccion(request, leccion_id):

    db.collection('lecciones').document(leccion_id).delete()

    messages.success(request, "Lección eliminada")
    return redirect('listar_lecciones')
