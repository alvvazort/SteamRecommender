#encoding:utf-8
from django import forms
   
class UsuarioBusquedaForm(forms.Form):
    idUsuario = forms.CharField(label="Id de Usuario", widget=forms.TextInput, required=True)
    
class JuegoBusquedaForm(forms.Form):
    idJuego = forms.CharField(label="Id del Juego", widget=forms.TextInput, required=True)