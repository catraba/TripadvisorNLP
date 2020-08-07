# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 13:46:31 2020

@author: Adrián
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

import telebot
from telebot import types



# VARIABLES

url = 'https://covid-2019.es/provincias'
nombre_tabla = 'table'

bot = telebot.Telebot('token')


# FUNCIONES

def extraer_tabla_web(url, nombre_tabla):
    
    pagina = requests.get(url).text
    soup = BeautifulSoup(pagina, 'lxml')

    tabla = soup.find('table', attrs={'id': nombre_tabla})
    
    listas = {i: [] for i in range(5)}
    
    i = 0
    
    for celda in tabla.find_all('td'):
        
        clave = i % 5 
              
        lista = listas.get(clave) 
        lista.append(celda.text) 
        listas[clave] = lista
        
        i += 1
        
    covid = pd.DataFrame({'Provincias': listas.get(0),
                      'Afectados': listas.get(1),
                      'Activos': listas.get(2),
                      'Fallecidos': listas.get(3),
                      'Recuperados': listas.get(4)})

    covid.set_index('Provincias', inplace = True)
    covid = covid.astype({'Afectados': int, 'Activos': int, 'Fallecidos': int, 'Recuperados': int})
    
    return covid

def quien_gana(mensaje):
    
    eleccion = ['piedra', 'papel', 'tijera']
    ganador = {'Piedrapiedra': 0, 'Piedratijera': 1, 'Piedrapapel': 2,
               'Papelpapel': 0, 'Papelpiedra': 1, 'Papeltijera': 2,
               'Tijeratijera': 0, 'Tijerapapel': 1, 'Tijerapiedra': 2}
    
    num_aleatorio = random.randint(0,2)
    valor_final = eleccion[num_aleatorio]
    
    resultado = mensaje + valor_final

    buscar_ganador = ganador.get(resultado)
    
    if buscar_ganador == 0:
        mensaje_final = 'He escogido ' + valor_final + ', así que hemos empatado :D'
    elif buscar_ganador == 1:
        mensaje_final = 'He escogido ' + valor_final + ', así que... pues eso'
    elif buscar_ganador == 2:
        mensaje_final = 'He escogido ' + valor_final + ', así que has perdido :)'
    
    return mensaje_final


def imprimir_datos(provincia):
    
    afectados = str(resultado.loc[provincia, 'Afectados'])
    fallecidos = str(resultado.loc[provincia, 'Fallecidos'])
    recuperados = str(resultado.loc[provincia, 'Recuperados'])
        
    stats = 'Afectados: ' + afectados + '\nFallecidos: ' + fallecidos + '\nRecuperados: ' + recuperados
          
    return stats


resultado = extraer_tabla_web(url, nombre_tabla) # Extraemos losdatos de la tabla

'''
BOT TELEGRAM
'''

# PANELES

juego = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3)
juego.add('Piedra', 'Papel', 'Tijera')

ocultar_panel = types.ReplyKeyboardRemove()



# COMANDOS

@bot.message_handler(commands=['start', 'help'])
def accion_help(message):
    
    archivo = open('help_text.txt', 'r')
    
    texto = archivo.read()
    
    bot.send_message(message.chat.id, texto)
        
    archivo.close()
    
@bot.message_handler(commands=['lista'])
def accion_lista(message):
    
    archivo = open('listado_provincias.txt', 'r')
    
    texto = archivo.read()
    
    bot.send_message(message.chat.id, texto)
    
    archivo.close()

@bot.message_handler(commands=['juego'])
def piedra_papel_tijera(message):
    bot.send_message(message.chat.id, 'Elige una opción: ', reply_markup=juego)



# FUNCIÓN QUE RECIBE CUALQUIER MENSAJE

@bot.message_handler(func=lambda message: True)
def respuesta_panel(message):
    
    provincias = ['A Coruña', 'Araba/Álava', 'Albacete', 'Alacant/Alicante', 'Almería','Asturias', 
              'Ávila', 'Badajoz', 'Baleares', 'BizkaiaVizcaya', 'Cataluña*', 'Burgos', 'Cáceres',
              'Cádiz', 'Cantabria', 'Castelló/Castellón', 'Ceuta', 'Ciudad Real', 'Córdoba',
              'Cuenca', 'EL Hierro', 'Fuerteventura', 'Galicia', 'Girona', 'Gran Canaria', 'Granada', 'Guadalajara', 'Gipuzkoa/Guipúzcoa', 'Huelva', 
              'Huesca', '*Illes Balears', 'Jaén', 'La Gomera', 'La Rioja', 'La Palma', 'Lanzarote', 'León', 'Lérida', 'Lugo', 
              'Madrid', 'Málaga', 'Melilla', 'Murcia', 'Navarra', 'Ourense', 'Palencia', 
              'Pontevedra', 'Salamanca', 'Segovia', 'Sevilla', 'Soria', 'Tarragona', 
              'Santa Cruz de Tenerife', 'Tenerife', 'Teruel', 'Toledo', 'València/Valencia', 'Valladolid', 
              'Zamora', 'Zaragoza']
    
    p_p_t = ['Piedra', 'Papel', 'Tijera']
    
    if message.text in provincias:
        
        bot.send_message(message.chat.id, imprimir_datos(message.text))
    
    elif message.text in p_p_t:
    
        bot.send_message(message.chat.id, quien_gana(message.text), reply_markup=ocultar_panel)
        
    else: 
        
        bot.send_message(message.chat.id, 'Lo siento, mi dueño no me ha enseñado a hablar bien su idioma...')


bot.polling()
