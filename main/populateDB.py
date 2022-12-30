#encoding:utf-8
from ssl import SSLError
from main.models import *
from datetime import datetime
import csv
from io import StringIO
from bs4 import BeautifulSoup
import urllib.request
import json
import time
import os.path
# third-party imports
import requests
from whoosh.fields import Schema, TEXT, ID
import shutil
from whoosh.index import open_dir, create_in
from whoosh.qparser import QueryParser


path = "data"

def get_request(url, parameters=None):
    """Return json-formatted response of a get request using optional parameters.
    
    Parameters
    ----------
    url : string
    parameters : {'parameter': 'value'}
        parameters to pass as part of get request
    
    Returns
    -------
    json_data
        json-formatted response (dict-like)
    """
    try:
        response = requests.get(url=url, params=parameters)
    except SSLError as s:
        print('SSL Error:', s)
        
        for i in range(5, 0, -1):
            print('\rWaiting... ({})'.format(i), end='')
            time.sleep(1)
        print('\rRetrying.' + ' '*10)
        
        # recusively try again
        return get_request(url, parameters)
    
    if response:
        return response.json()
    else:
        # response is none usually means too many requests. Wait and try again 
        print('No response, waiting 10 seconds...')
        time.sleep(10)
        print('Retrying.')
        return get_request(url, parameters)

def get_list_of_appId():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    parameters = {}

    # request 'all' from steam spy and parse into dataframe
    json_data = get_request(url, parameters=parameters)["applist"]["apps"]

    # Almacenar todas las Ids de los juegos de Steam y sus respectivos nombres con woosh
    schem = Schema(appId=ID(stored=True), titulo=TEXT(stored=True))

    #eliminamos el directorio del Ãíndice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    #creamos el í­ndice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder aÃ±adir documentos al indice
    writer = ix.writer()

    for game in json_data:
        writer.add_document(appId=str(game["appid"]), titulo= game["name"])   

    writer.commit()

    return "Índice creado correctamente \nHay " + str(ix.doc_count_all()) + " registros (appId y nombre del juego)"

def scrap_categories(appId, juego):
    f = urllib.request.urlopen("https://store.steampowered.com/app/"+appId)
    s = BeautifulSoup(f, "html.parser")

    print(s)

def populate_categories():
    ix=open_dir("Index")
    qp = QueryParser("titulo", schema=ix.schema)

    with ix.searcher() as searcher:

        for juego in Juego.objects.all(): # Juego por juego se busca en el index para así poder obtener el appId y guardarlo en la DB
            q = qp.parse(str(juego.titulo))
            results=searcher.search(q,limit=1)
            for r in results:
                juego.appId=r["appId"]
                scrap_categories(r["appId"], juego)
                juego.save()




def populate():
    Behavior.objects.all().delete()
    Categoria.objects.all().delete()

    behaviors=[]
    fileobj=open(path+"\\steam-200k.csv", "r")
    for line in fileobj.readlines(): # idUsuario, juego, accion, horas, ?
        line = csv.reader(StringIO(line), delimiter=",")
        rip = [row for row in line][0]
        if len(rip) != 5:
            continue
        juego, created=Juego.objects.get_or_create(titulo=rip[1])
        behaviors.append(Behavior(idUsuario=rip[0],juego=juego, accion=rip[2], horasJugadas=rip[3]))
        
    fileobj.close()
    Behavior.objects.bulk_create(behaviors)  
    
    return Behavior.objects.count()

'''
def populateOccupations():
    Ocupacion.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\u.occupation", "r")
    for line in fileobj.readlines():
        lista.append(Ocupacion(nombre=str(line.strip())))
    fileobj.close()
    Ocupacion.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return Ocupacion.objects.count()

def populateGenres():
    Categoria.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\u.genre", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        if len(rip) != 2:
            continue
        lista.append(Categoria(idCategoria=int(rip[1]), nombre=rip[0]))
    fileobj.close()
    Categoria.objects.bulk_create(lista)
    
    return Categoria.objects.count()

def populateUsers():
    Usuario.objects.all().delete()
    
    lista=[]
    dict={} # diccionario de los usuarios {idusuario:objeto_usuario}
    fileobj=open(path+"\\u.user", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        if len(rip) != 5:
            continue
        u=Usuario(idUsuario=int(rip[0]), edad=int(rip[1]), sexo=rip[2], ocupacion=Ocupacion.objects.get(nombre=rip[3]), codigoPostal=rip[4])
        lista.append(u)
        dict[int(rip[0])]=u
    fileobj.close()
    Usuario.objects.bulk_create(lista)
    
    return(dict, Usuario.objects.count())

def populateMovies():
    Pelicula.objects.all().delete()
    
    lista_peliculas =[]  # lista de peliculas
    dict_categorias={}  #  diccionario de categorias de cada pelicula (idPelicula y lista de categorias)
    fileobj=open(path+"\\u.item", "r")
    for line in fileobj.readlines():
        rip = line.strip().split('|')
        
        date = None if len(rip[2]) == 0 else datetime.strptime(rip[2], '%d-%b-%Y')
        lista_peliculas.append(Pelicula(idPelicula=int(rip[0]), titulo=rip[1], fechaEstreno=date, imdbUrl=rip[4]))
        
        lista_aux=[]
        for i in range(5, len(rip)):
            if rip [i] == '1':
                lista_aux.append(Categoria.objects.get(pk = (i-5)))
        dict_categorias[int(rip[0])]=lista_aux
    fileobj.close()    
    Pelicula.objects.bulk_create(lista_peliculas)

    dict={} # diccionario de las pel�culas {idpelicula:objeto_pelicula}
    for pelicula in Pelicula.objects.all():
        #aqu� se a�aden las categorias a cada pel�cula
        pelicula.categorias.set(dict_categorias[pelicula.idPelicula])
        dict[pelicula.idPelicula]=pelicula
    
    return(dict, Pelicula.objects.count())

def populateRatings(u,m):
    # usamos los diccionarios de usuarios y pel�culas para acelerar la creaci�n de las puntuaciones
    # evitando tener que acceder a las tablas de Usuario y Pelicula
    Puntuacion.objects.all().delete()

    lista=[]
    fileobj=open(path+"\\u.data", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('\t')
        lista.append(Puntuacion(idUsuario=u[int(rip[0])], idPelicula=m[int(rip[1])], puntuacion=int(rip[2])))
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)

    return Puntuacion.objects.count()

'''
    

