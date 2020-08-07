# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:30:18 2020

@author: Adrián
"""

import os
import re
import requests
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from tensorflow.keras.preprocessing import image

import telebot



# FUNCIONES

def descargar_fotos(url, headers):
    
    num = 25000 # Valor inicial
    
    while(num < 30000): # Modificar hasta el valor deseado
    
        filename = r'C:\Users\Adrián\Downloads\trainphotos_FacialReconBOT\IMG_' + str(num) + '.png'
    
        r = requests.get(url, headers=headers)
    
        with open(filename, 'wb') as f:
            f.write(r.content)
            f.close()
        
        int(num)
        num = num + 1
    
        time.sleep(1.5)

def calcular_etapa(path):
    
    # Cargamos la imagen y la redimensionamos
    imagen = image.load_img(path, target_size=(128, 128))
    
    # La convertimos en un array de (128, 128, 3)
    x = image.img_to_array(imagen)
    x = x / 255.0
    # Agregamos num de imágenes -> (1, 128, 128, 3)
    x = np.expand_dims(x, axis = 0)

    y_prob = model.predict(x) * 100
    
    return(y_prob)
    
def imprimir_etapa(array):
    
    tabla = pd.DataFrame({'Valores': [array[0, 0], array[0, 1], array[0, 2], 
                                       array[0, 3], array[0, 4], array[0, 5]], 
                          'Etapas': ['% Adolescencia', '% Adultez', '% Infancia', 
                                      '% Juventud', '% Niñez', '% Senectud']})
    
    redondeo = tabla.round(decimals = 2)
    ordenada = redondeo.sort_values(by=['Valores'], ascending = False)
    
    primer_valor = ordenada.iloc[0, 0]
    primer_etapa = ordenada.iloc[0, 1]
    segundo_valor = ordenada.iloc[1, 0]
    segundo_etapa = ordenada.iloc[1, 1]
    tercer_valor = ordenada.iloc[2, 0]
    tercer_etapa = ordenada.iloc[2, 1]
    cuarto_valor = ordenada.iloc[3, 0]
    cuarto_etapa = ordenada.iloc[3, 1]
    quinto_valor = ordenada.iloc[4, 0]
    quinto_etapa = ordenada.iloc[4, 1]
    sexto_valor = ordenada.iloc[4, 0]
    sexto_etapa = ordenada.iloc[5, 1]
    
    texto = str(primer_valor) + primer_etapa + '\n' + str(segundo_valor) + segundo_etapa + '\n' + str(tercer_valor) + tercer_etapa + '\n' + str(cuarto_valor) + cuarto_etapa + '\n' + str(quinto_valor) + quinto_etapa + '\n' + str(sexto_valor) + sexto_etapa

    return(texto)



# DESCARGA DE FOTOS
'''
direccion_fotos = 'https://thispersondoesnotexist.com/image'
user_agent = {'User-Agent': 'Mozilla/5.0'} # Necesario para descargar_fotos

descargar_fotos(direccion_fotos, user_agent)
'''
    


# Une ruta de trabajo con la carpeta 'Categorías'
ruta_directorio = os.path.join(os.getcwd(), 'Categorías') + os.sep 

imagenes = []
directorios = []
cont_dir = []
etiquetas = []
ruta_previa = ''
cant_img = 0
indice = 0

# Genera ruta, carpetas y archivos de una ruta dada 
for ruta, carpetas, archivos in os.walk(ruta_directorio):  
    
    for nombre in archivos:
        
        if re.search("\.png$", nombre):
            
            cant_img = cant_img + 1
            
            ruta_archivo = os.path.join(ruta, nombre)
            img = plt.imread(ruta_archivo, 0)
            imagenes.append(img) # Lista con todas las imágenes
        
            if ruta_previa != ruta:
                
                # Lista con la cantidad de imágenes por cada ruta
                cont_dir.append(cant_img) 
                
                ruta_previa = ruta
                cant_img = 0
                
cont_dir.append(cant_img)
 
cont_dir = cont_dir[1:]
cont_dir[0] = cont_dir[0] + 1

# Clasificamos cada imagen a un valor entre 0 y 5 
for num in cont_dir:
    
    for i in range(num):
        
        etiquetas.append(indice)
        
    indice = indice + 1

X = np.array(imagenes, dtype=np.uint8) # Array con las imágenes
Y = np.array(etiquetas) # Array con las etapas



# Dividimos X e Y en datos de entrenamiento y testeo
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.20)

# Normalizamos valores de las imágenes entre 0 y 1
X_train = X_train / 255.0
X_test = X_test / 255.0

# Volvemos a dividir para obtener datos de validación
X_train, X_valid, train_label, valid_label = train_test_split(X_train, Y_train, test_size = 0.20)



# CONTRUCCIÓN DE LA RED NEURONAL

model = Sequential()

# Primera capa neuronal. Con ReLu hacemos: f(x) = max(0, x)
model.add(Conv2D(32, kernel_size = (3, 3), activation = 'relu',
                 input_shape = (128, 128, 3)))
# Reducimos la matriz conv a la mitad
model.add(MaxPool2D(pool_size = (2, 2)))
model.add(Dropout(0.5)) # Evitamos overfitting

model.add(Conv2D(64, kernel_size = (3, 3), activation = 'relu'))
model.add(MaxPool2D(pool_size = (2, 2)))
model.add(Dropout(0.5))
model.add(Flatten()) # Aplanamos las imágenes
# Con softmax calculamos la probabilidad de cada clase
model.add(Dense(6, activation='softmax')) # 6 neuronas de salida
 
model.summary()

model.compile(loss = 'sparse_categorical_crossentropy', 
              optimizer = 'SGD', metrics = ['accuracy'])



# GENERAR MODELO

modelo = model.fit(X_train, train_label, 
                          batch_size = 32, 
                          epochs = 30,
                          validation_data = (X_valid, valid_label))



# GUARDAR MODELO
#model.save('model.h5')



# CARGAR MODELO
#anterior_modelo = load_model('model.h5')
#nuevo_modelo = Sequential(anterior_modelo.layers)



# EVALUACIÓN DEL MODELO

evaluacion = model.evaluate(X_test, Y_test)
 
print('Test loss:', evaluacion[0])
print('Test accuracy:', evaluacion[1])



# BOT TELEGRAM

token = '1113756889:AAG-0wVQl3BSQ8oKO-ecR-bab_x6ChIwbQA'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'ayuda'])
def comando_inicio(message):
    archivo = open('texto_start.txt', 'r')
    texto = archivo.read()

    bot.send_message(message.chat.id, texto)

    archivo.close()


@bot.message_handler(commands=['instrucciones'])
def comando_instrucciones(message):
    archivo = open('texto_instrucciones.txt', 'r')
    texto = archivo.read()

    bot.send_message(message.chat.id, texto)

    archivo.close()


@bot.message_handler(commands=['info'])
def comando_info(message):
    archivo = open('texto_info.txt', 'r')
    texto = archivo.read()

    bot.send_message(message.chat.id, texto)

    archivo.close()


@bot.message_handler(content_types=['photo'])
def foto(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('C:\\Users\\CatrabaPC\\imagen.jpg', 'wb') as write_file:
        write_file.write(downloaded_file)
        write_file.close()

    vector = calcular_etapa('C:\\Users\\CatrabaPC\\imagen.jpg')

    bot.send_message(message.chat.id, imprimir_etapa(vector))


@bot.message_handler(func=lambda message: True)
def mensaje_defecto(message):
    bot.send_message(message.chat.id,
                     'Lo siento, pero mi dueño no me ha enseñado a hablar su idoma... Pruebe a enviar un comando')


bot.polling()