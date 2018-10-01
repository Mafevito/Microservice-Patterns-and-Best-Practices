import datetime
from flask_mongoengine import MongoEngine

#MongoEngine, la herramienta que utilizamos para estructurar los datos procedentes de MongoDB.
db = MongoEngine()

#La clase News es la que representa el punto central del dominio de la aplicación.
class News(db.Document): 
    title = db.StringField(required=True, max_length=200) 
    content = db.StringField(required=True) 
    author = db.StringField(required=True, max_length=50) 
    created_at = db.DateTimeField(default=datetime.datetime.now) 
    published_at = db.DateTimeField() 
    news_type = db.StringField(default="famous") 
    tags = db.ListField(db.StringField(max_length=50))