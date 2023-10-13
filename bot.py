"""
CREATE DATABASE esp32news;

USE esp32news;

CREATE TABLE news(
   id INT AUTO_INCREMENT PRIMARY KEY,
   news TEXT,
   created_at DATETIME
);
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Text
from datetime import datetime
import pytz

import requests #
from bs4 import BeautifulSoup #pip install beautifulsoup4
client = requests.Session()

# sudo pip install paho-mqtt (Libreria para conectar al broker MQTT)
# Importar libreria paho para conectarse al servidor MQTT.
import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = '192.168.18.27'
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqttClient.subscribe("/project/news")
    doWork()

def on_message(client, userdata, msg):
    print("Message Recieved. ", msg.payload.decode())
    command = msg.payload.decode()

    if command == "R":  # PR = Process
        print("Some message")



# Configura la conexión a la base de datos MySQL
# Cambia 'mysql://usuario:contraseña@localhost/nombre_de_la_base_de_datos' con tus propias credenciales
engine = create_engine('mysql://root:123456789@192.168.18.27/esp32news')

# Crea una instancia de la clase base declarativa
Base = declarative_base()

# Define la clase que representa la tabla "news"
class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    news = Column(Text)
    created_at = Column(DateTime,  nullable=False)

# Crea la tabla en la base de datos (solo la primera vez)
#Base.metadata.create_all(engine)

# Crea una sesión para interactuar con la base de datos
Session = sessionmaker(bind=engine)
session = Session()


def getFechaActual():
    ist = pytz.timezone('America/Lima')
    datetime_ist = datetime.now(ist)
    fecha_actual = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')

    return fecha_actual

def doWork() :
    # =============================================================================================
    noticias = "Estas son las noticias del diario el Peruano."

    # Obtener noticia principal
    principal_news = requests.get('https://elperuano.pe/Portal/_GetPortadaPrincipal').json()
    noticias += principal_news['vchTitulo'].strip() + "\\n"

    noticias += "Estas son las noticias destacadas del diario el peruano.\\n"
    # Obtener noticias destacadas
    recommended_news = requests.get('https://elperuano.pe/Portal/_GetNoticiasDestacadas').json()
    for news in recommended_news:
        noticias += news['vchTitulo'].strip() + "\\n"

    noticias += "Estas son las ultimas noticias del diario el peruano.\\n"
    # Obtener ultimas noticias
    last_news = requests.get('https://elperuano.pe/Portal/_GetNoticiasLoUltimo').json()
    for news in last_news:
        noticias += news['vchTitulo'].strip() + "\\n"

    # =============================================================================================
    # Noticias del diario la republica.
    noticias += "Estas son las noticias en portada del diario la republica.\\n"
    noticias += "Sección Economia.\\n"

    # Obtener la noticias de portada principal:
    # Sección Economia:
    # Larepublica.pe bloqueaba el scrapper se tubo que usar cabeceras:

    url = "https://larepublica.pe/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
    }

    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")

    for h2 in soup.select("div:has(*:-soup-contains(Economía)) + div h2"):
        #print(h2.text)
        noticias += h2.text + "\\n"

    # Obtener noticias de sección Politica:
    noticias += "Sección de Politica\\n"
    for h2 in soup.select("div:has(*:-soup-contains(Política)) + div h2"):
        noticias += h2.text+"\\n"


    # Obtener noticias de sección Sociedad:
    noticias += "Sección de Sociedad\\n"
    for h2 in soup.select("div:has(*:-soup-contains(Sociedad)) + div h2"):
        noticias += h2.text+"\\n"

    # Obtener noticias de sección Mundo:
    noticias += "Sección de Mundo\\n"
    for h2 in soup.select("div:has(*:-soup-contains(Mundo)) + div h2"):
        noticias += h2.text + "\\n"

    # Obtener noticias de sección Tecnología:
    noticias += "Sección de Tecnología\\n"
    for h2 in soup.select("div:has(*:-soup-contains(Tecnología)) + div h2"):
        noticias += h2.text + "\\n"

    # =============================================================================================
    # Noticias EuropaPress PortalTic
    html = client.get("https://www.europapress.es/portaltic/")
    soup = BeautifulSoup(html.text, 'html.parser')
    noticias += "Estas son las noticias de EuropaPress portal tic.\\n"

    # Obtener la noticia de portada principal
    for div in soup.findAll('h2', attrs={'class':'titulo-principal'}):
        noticias += div.text+"\\n"
        #print(div.text)

    # Obtener el resto de noticias listado:
    for div in soup.findAll('h2', attrs={'class':'home-articulo-titulo'}):
        noticias += div.text + "\\n"

    # =============================================================================================
    # Noticias Russia Today
    noticias += "Estas son las noticias del portal Rusia Today en español.\\n"
    html = client.get("https://actualidad.rt.com/")
    soup = BeautifulSoup(html.text, 'html.parser')

    # Obtener la noticia de portada principal

    for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_2'}):
        n = div.text.strip() # Eliminar "\n"
        noticias += n+"\\n"


    for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_5'}):
        n = div.text.strip() # Eliminar "\n"
        noticias += n + "\\n"

    for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_4'}):
        n = div.text.strip() # Eliminar "\n"
        noticias += n + "\\n"


    # Inserta datos en la tabla "news"
    news = News(news=noticias, created_at=getFechaActual())

    # Agrega las nuevas noticias a la sesión
    session.add(news)

    # Confirma los cambios (realiza la inserción en la base de datos)
    session.commit()

    # Cierra la sesión
    session.close()

    print("Done!");
    mqttClient.publish("/project/news", "R")  # R = read


mqttClient = mqtt.Client()
mqttClient.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE_INTERVAL)
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message
mqttClient.loop_forever()

