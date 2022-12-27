#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Ocupacion(models.Model):
    ocupacionId = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, verbose_name='Ocupación', unique=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre', )

class Usuario(models.Model):
    idUsuario = models.IntegerField(primary_key=True)
    edad = models.PositiveSmallIntegerField(verbose_name='Edad', help_text='Debe introducir una edad')
    sexo = models.CharField(max_length=1, verbose_name='Sexo', help_text='Debe elegir entre M o F', choices=(('M','Masculino'),('F', 'Femenino')))
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.SET_NULL, null=True)
    codigoPostal = models.CharField(max_length=6,verbose_name='Código Postal')

    def __str__(self):
        return str(self.idUsuario)
    
    class Meta:
        ordering = ('idUsuario', )

class Categoria(models.Model):
    idCategoria = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=30, verbose_name='Categoría')

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering =('nombre', )

class Pelicula(models.Model):
    idPelicula = models.IntegerField(primary_key=True)
    titulo = models.TextField(verbose_name='Título')
    fechaEstreno = models.DateField(verbose_name='Fecha de Estreno', null=True)
    imdbUrl = models.URLField(verbose_name='URL en IMDB')
    categorias = models.ManyToManyField(Categoria)
    puntuaciones = models.ManyToManyField(Usuario, through='Puntuacion')

    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', 'fechaEstreno', )

class Puntuacion(models.Model):
    PUNTUACIONES = ((1, 'Muy mala'), (2,'Mala'), (3,'Regular'), (4,'Buena'), (5,'Muy Buena'))
    idUsuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    idPelicula = models.ForeignKey(Pelicula,on_delete=models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField(verbose_name='Puntuación', validators=[MinValueValidator(0), MaxValueValidator(5)], choices=PUNTUACIONES)
    
    def __str__(self):
        return (str(self.puntuacion))
    
    class Meta:
        ordering=('idPelicula','idUsuario', )