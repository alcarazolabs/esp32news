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
import time
client = requests.Session()


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

# Noticias EuropaPress PortalTic
html = client.get("https://www.europapress.es/portaltic/")
soup = BeautifulSoup(html.text, 'html.parser')
noticias= "Estas son las noticias de EuropaPress portal tic.\\n"

# Obtener la noticia de portada principal
for div in soup.findAll('h2', attrs={'class':'titulo-principal'}):
    noticias += div.text+"\\n"
    #print(div.text)

# Obtener el resto de noticias listado:
for div in soup.findAll('h2', attrs={'class':'home-articulo-titulo'}):
    noticias += div.text + "\\n"

# Noticias Russia Today
noticias += "Estas son las noticias del portal Russia Today en español.\\n"
html = client.get("https://actualidad.rt.com/")
soup = BeautifulSoup(html.text, 'html.parser')

# Obtener la noticia de portada principal

for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_2'}):
    noticias += div.text+"\\n"


for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_5'}):
    noticias += div.text+"\\n"

for div in soup.findAll('div', attrs={'class':'HeaderNews-root HeaderNews-type_4'}):
    noticias += div.text+"\\n"

#print(noticias)


# Inserta datos en la tabla "news"
news = News(news=noticias, created_at=getFechaActual())

# Agrega las nuevas noticias a la sesión
session.add(news)

# Confirma los cambios (realiza la inserción en la base de datos)
session.commit()

# Cierra la sesión
session.close()


