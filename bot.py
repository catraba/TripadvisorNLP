import json
import random
import numpy as np

import re
from spacy import load
import es_core_news_lg

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

import telebot
bot = telebot.TeleBot('token')


#VARIABLES VARIAS
faltas_ortograficas = ['alante', 'aver', 'llendo', 'contra mas', 'contra menos', 'haiga']
contestaciones = ['Escribe bien que te meto eh', 'En este grupo hay que escribir sin faltas melón',
                  '¿A ti quién te ha enseñado a escribir?', 'Mis hogos higo de fruta']


# CARGAMOS LOS DATOS
with open('conversaciones.json') as datos_json:
    intenciones = json.load(datos_json)

nlp = load('es_core_news_lg') # Modelo NLP con datos Word2Vec de spacy

# EXTRAEMOS DATOS
etiquetas = []
oraciones = []

for intencion in intenciones['intenciones']:
    with nlp.disable_pipes():

        for patron in intencion['patrones']:

            etiquetas.append(intencion['etiqueta'])
            oraciones.append(nlp(patron).vector)

# Categorizamos la etiqueta
diccionario = {'saludos': 0, 'despedida': 1, 'gracias': 2, 'horario': 3, 'pago': 4, 'metodo': 5, 'contenido': 6,
               'adulto': 7, 'peticiones': 8, 'nombre': 9, 'edad': 10, 'localizacion': 11}
etiquetas_cat = [diccionario.get(valor) for valor in etiquetas]


# Convertimos listas a arrays
vectors = np.asarray(oraciones)
labels = np.asarray(etiquetas_cat)


# Diseñamos el modelo de aprendizaje
LR = LogisticRegression()
modelo = LR.fit(vectors, labels)


# FUNCIÓN PARA CALCULAR LA RESPUESTA 
def mencionBot(mensaje, modelo):

    respuestas = []

    x = nlp(mensaje).vector
    x = x.reshape(1, -1)
    y_prob = modelo.predict(x)

    diccionario_inverso = {0: 'saludos', 1: 'despedida', 2: 'gracias', 3: 'horario', 4: 'pago', 5: 'metodo',
                           6: 'contenido', 7: 'adulto', 8: 'peticiones', 9: 'nombre', 10: 'edad', 11: 'localizacion'}
    elegida = diccionario_inverso.get(y_prob[0])

    for intencion in intenciones['intenciones']:
        # for respuesta in intencion['respuestas']:
        if intencion['etiqueta'] == elegida:
            respuestas.append(respuesta)

    return random.choise(respuestas)


# FUNCIÓN PARA EL BOT DE TELEGRAM

@bot.message_handler(func=lambda message: True)
def respuestaTO(message):

    mensaje = message.text

    patron = '(.*)+@nombredelbot+(.*)'
    match = re.match(patron, mensaje)

    if match:
        respuesta = mensaje.replace('@nombredelbot', '')
        bot.send_message(message.chat.id, respuesta)

    else:
        for i in range(0, len(faltas_ortograficas)):
            falta = faltas_ortograficas[i]
            if falta in mensaje:
                reply = random.choice(contestaciones)

        bot.send_message(message.chat.id, reply)

bot.polling()


