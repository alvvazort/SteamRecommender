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
    if s.find("b", text="Genre:"):
        generos=s.find("b", string="Genre:").find_next_sibling("span").text.strip().split(",")
        for genero in generos: #Crear si no existe la categoría y asignarlo
            genero = genero.strip()
            categoria, created = Categoria.objects.get_or_create(nombre=genero)
            categoria.save()
            juego.categorias.add(categoria)
        if s.find("b", string="Publisher:"): # Guardar el editor si existe
            editor=s.find("b", string="Publisher:").find_next_sibling("a").text.strip()
            juego.editor=editor
        if s.find("b", string="Developer:"): # Guardar desarrollador si existe
            desarrollador=s.find("b", string="Developer:").find_next_sibling("a").text.strip()
            juego.desarrollador=desarrollador
        if s.find("img", class_="game_header_image_full"):
            imagen= s.find("img", class_="game_header_image_full")["src"]
            juego.imagen= imagen

        juego.save()


def populate_categories():
    ix=open_dir("Index")
    qp = QueryParser("titulo", schema=ix.schema)

    with ix.searcher() as searcher:
        print("Comienzo del scraping, esto llevará una gran cantidad de tiempo")
        for i,juego in enumerate(Juego.objects.all()): # Juego por juego se busca en el index para así poder obtener el appId y guardarlo en la DB
            q = qp.parse(str(juego.titulo))
            results=searcher.search(q,limit=1)
            for r in results:
                juego.appId=r["appId"]
                scrap_categories(r["appId"], juego)
            if i%100==99:
                print("Se han añadido las categorías e información de "+ str(i+1)+" juegos")




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


    

