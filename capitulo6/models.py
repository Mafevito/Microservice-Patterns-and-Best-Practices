# Modelos para implementar CQRS
#tenemos dos representaciones de entidades para la base de datos: una representación que sirve al CommandStack y otra que sirve al QueryStack

#empezamos con la importación de las dependencias. Primero, debemos importar las dependencias de las librerías nativas y MongoEngine, como los tipos de campos y la función de conexión que se encarga de conectar el modelo con una instancia de MongoDB
import os 
from datetime import datetime 
from mongoengine import ( 
    connect, 
    Document, 
    DateTimeField, 
    ListField, 
    IntField, 
    StringField, 
)

#añadimos las importaciones a SQLAlchemy. Estas importaciones son para definición de campo y para indicar qué tipo de base de datos SQLAlchemy usar
from sqlalchemy import ( 
    Column, 
    String, 
    BigInteger, 
    DateTime, 
    Index, 
) 
from sqlalchemy.dialects import postgresql 
from sqlalchemy.ext.declarative import declarative_base

#CommandStack

#definición de la entidad usando SQLAlchemy con Postgres. Aquí, empezamos a preparar nuestra aplicación para el uso de la organización de eventos. Además de un ID único, también poseen un campo de versión. Este campo ID y versión será la clave compuesta de nuestra base de datos. Con esto, nunca actualizaremos un artículo, sino que incluiremos una nueva versión de la misma noticia
Base = declarative_base() 
 
class CommandNewsModel(Base): 
    __tablename__ = 'news' 
 
    id = Column(BigInteger, primary_key=True) 
    version = Column(BigInteger, primary_key=True) 
    title = Column(String(length=200)) 
    content = Column(String) 
    author = Column(String(length=50)) 
    created_at = Column(DateTime, default=datetime.utcnow) 
    published_at = Column(DateTime) 
    news_type = Column(String, default='famous') 
    tags = Column(postgresql.ARRAY(String)) 
 
    __table_args__ = Index('index', 'id', 'version')

#definir la entidad QueryStack. Tenga en cuenta que la función connect establece el acceso a la base de datos utilizando una variable de entorno.
connect('famous', host=os.environ.get('QUERYBD_HOST')) 
 
class QueryNewsModel(Document): 
    id = IntField(primary_key=True) 
    version = IntField(required=True) 
    title = StringField(required=True, max_length=200) 
    content = StringField(required=True) 
    author = StringField(required=True, max_length=50) 
    created_at = DateTimeField(default=datetime.utcnow) 
    published_at = DateTimeField() 
    news_type = StringField(default="famous") 
    tags = ListField(StringField(max_length=50))

