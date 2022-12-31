#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Categoria(models.Model):
    nombre = models.CharField(max_length=30, verbose_name='Categoría')
    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering =('nombre', )

class Juego(models.Model):
    titulo = models.TextField(verbose_name='Título', unique=True)
    imagen = models.URLField(verbose_name="Imagen del juego", null= True)
    categorias = models.ManyToManyField(Categoria)
    desarrollador= models.TextField(verbose_name='Desarrollador', null=True)
    editor = models.TextField(verbose_name='Editor', null=True)
    appId= models.PositiveBigIntegerField(null=True)

    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', )

class Behavior(models.Model):
    ACCIONES = [
        ("pl","play"),
        ("pu","purchase")
    ]

    idUsuario = models.PositiveBigIntegerField()
    juego = models.ForeignKey(Juego,on_delete=models.CASCADE)
    accion= models.CharField(choices=ACCIONES, max_length=10)
    horasJugadas = models.FloatField(verbose_name='Horas Jugadas')
    

    def __str__(self):
        return (str(self.idUsuario)+ " "+ str(self.horasJugadas)+ "horas jugadas")
    
    class Meta:
        ordering=('idUsuario','horasJugadas', )