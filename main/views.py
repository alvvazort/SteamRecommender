#encoding:utf-8
from main.models import *
from main.populateDB import populate, get_list_of_appId, populate_categories
from main.forms import  UsuarioBusquedaForm, JuegoBusquedaForm
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.conf import settings
from main.recommendations import  transformPrefs, getRecommendations, topMatches, sim_distance
import shelve

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

def rate_by_hours_played(hours):
    rate=0
    if(hours<=1):
        rate=1
    elif(hours<=2):
        rate=2
    elif(hours<=4):
        rate=3
    elif(hours<=8):
        rate=4
    else:
        rate=5
    
    return rate

# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a juegos. Tambien carga el diccionario inverso
# Serializa los resultados en dataRS.dat
def loadDict():
    
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    behaviors = Behavior.objects.all()
    for ra in behaviors:
        if ra.accion== "play":
            user = ra.idUsuario
            itemid = ra.juego.appId
            rating = rate_by_hours_played(ra.horasJugadas)
            Prefs.setdefault(user, {})
            Prefs[user][itemid] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf.close()
    



#Funcion de acceso restringido que carga los datos en la BD  
@login_required(login_url='/ingresar')
def populateDatabase(request):
    
    numBehaviors=populate()
    mensaje = 'Se han cargado: ' + str(numBehaviors) + ' comportamientos, ' + str(Juego.objects.count())+ ' juegos'
    logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    return render(request, 'mensaje.html',{'titulo':'FIN DE CARGA DE LA BD','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})
    
#Funcion de acceso restringido que carga los datos en la BD  
@login_required(login_url='/ingresar-scraping')
def scraping(request):
    mensaje=get_list_of_appId()
    populate_categories()
    logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    mensaje += "Se han cargado " + str(Categoria.objects.count()) + " categorías"
    return render(request, 'mensaje.html',{'titulo':'Datos de videojuegos cargados','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})


def loadRS(request):
    loadDict()
    mensaje = 'Se han cargado la matriz y la matriz invertida '
    return render(request, 'mensaje.html',{'titulo':'FIN DE CARGA DEL RS','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})


def recomendar_juegos_usuario_RSusuario(request):
    
    formulario = UsuarioBusquedaForm()
    items = None
    idUsuario = None

    try:
        if request.method=='POST':
            formulario = UsuarioBusquedaForm(request.POST)
            
            if formulario.is_valid():
                idUsuario=formulario.cleaned_data['idUsuario']
                shelf = shelve.open("dataRS.dat")
                Prefs = shelf['Prefs']
                shelf.close()
                rankings = getRecommendations(Prefs,int(idUsuario))
                recomendadas= rankings[:6]
                juegos = []
                puntuaciones = []
                for re in recomendadas:
                    juegos.append(Juego.objects.filter(appId=re[1])[0])
                    puntuaciones.append(re[0])
                items= zip(juegos,puntuaciones)
    except:
        mensaje = 'La id del usuario no es correcto'
        return render(request, 'mensaje.html',{'titulo':'ERROR','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

    return render(request, 'recomendar_juegos_usuarios.html', {'formulario':formulario, 'items':items, 'usuario':idUsuario, 'STATIC_URL':settings.STATIC_URL})
    

def mostrar_juegos_parecidos(request):
    formulario = JuegoBusquedaForm()
    juego = None
    items = None
    if request.method=='POST':
        formulario = JuegoBusquedaForm(request.POST)
        try:
            if formulario.is_valid():
                idJuego = formulario.cleaned_data['idJuego']
                
                juego = Juego.objects.filter(appId=idJuego)[0]
                
                shelf = shelve.open("dataRS.dat")
                ItemsPrefs = shelf['ItemsPrefs']
                shelf.close()
                #utilizo distancia euclidea para que se vea mejor en los listados
                parecidas = topMatches(ItemsPrefs, int(idJuego),n=6,similarity=sim_distance)
                juegos = []
                similaridad = []
                for re in parecidas:
                    juegos.append(Juego.objects.filter(appId=re[1])[0])
                    similaridad.append(re[0])
                items= zip(juegos,similaridad)
        except:
            mensaje = 'La id del juego no es correcto'
            return render(request, 'mensaje.html',{'titulo':'ERROR','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})
    
    return render(request, 'juegos_similares.html', {'formulario':formulario, 'juego': juego, 'items': items, 'STATIC_URL':settings.STATIC_URL})



def mostrar_acciones_usuario(request):
    
    formulario = UsuarioBusquedaForm()
    acciones = None
    idusuario = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            idusuario = formulario.cleaned_data['idUsuario']
            acciones = Behavior.objects.filter(idUsuario = idusuario)
            
    return render(request, 'acciones_usuario.html', {'formulario':formulario, 'acciones':acciones, 'idusuario':idusuario, 'STATIC_URL':settings.STATIC_URL})


def index(request):
    juegos = Juego.objects.all()[3:12]
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL, 'juegos':juegos})


def ingresar(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/populate'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

def ingresar_scraping(request):
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/scraping'))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar_scraping.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

