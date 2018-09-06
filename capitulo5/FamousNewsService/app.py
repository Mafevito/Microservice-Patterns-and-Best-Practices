#archivo reponsable de ejecutar cualquier aplicación

#importamos el Blueprint con todas nuestras rutas y la instancia MongoEngine que contiene la declaración de nuestra entidad
import os 
from flask import Flask 
from views import famous_newsfrom models import db

#instanciar Flask y pasar la configuración de los entornos, la instancia de la base de datos, y la instancia de las rutas de visualización
# instantiate the app 
app = Flask(__name__) 
 
# set config 
app_settings = os.getenv('APP_SETTINGS') 
app.config.from_object(app_settings) 
 
db.init_app(app) 
 
# register blueprints 
app.register_blueprint(famous_news)

#realizar Flask en el puerto 5000
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000)