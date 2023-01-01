from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('acciones_usuario/',views.mostrar_acciones_usuario),
    path('juegos_similares/',views.mostrar_juegos_parecidos),
    path('recomendar_juegos_usuarios/',views.recomendar_juegos_usuario_RSusuario),
    path('',views.index),
    path('index.html/', views.index),
    path('populate/', views.populateDatabase),
    path('scraping/',views.scraping),
    path('loadRS/', views.loadRS),
    path('ingresar/', views.ingresar),
    path('ingresar-scraping/', views.ingresar_scraping),
    path('admin/',admin.site.urls),
    ]
