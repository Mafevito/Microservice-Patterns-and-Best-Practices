#archivo de configuración del microservicio
# encuentran los ajustes para cada entorno de desarrollo
# se divide en clases que tienen la definición de cada entorno.

# BaseConfig. Esta clase se utiliza sólo como herencia para las otras clases
class BaseConfig: 
    """Base configuration""" 
    DEBUG = False 
    TESTING = False 
    MONGODB_SETTINGS = {}

#estas manipulan la configuración de cada entorno
class DevelopmentConfig(BaseConfig): 
    """Development configuration""" 
    DEBUG = True 
    MONGODB_SETTINGS = { 
        'db': 'politics_dev', 
        'host': '{}{}'.format( 
            os.environ.get('DATABASE_HOST'), 
            'politics_dev', 
        ), 
    } 
class TestingConfig(BaseConfig): 
    """Testing configuration""" 
    DEBUG = True 
    TESTING = True 
    MONGODB_SETTINGS = { 
        'db': 'politics_test', 
        'host': '{}{}'.format( 
            os.environ.get('DATABASE_HOST'), 
            'politics_test', 
        ), 
    } 
 
class ProductionConfig(BaseConfig): 
    """Production configuration""" 
    DEBUG = False 
    MONGODB_SETTINGS = { 
        'db': 'politics', 
        'host': '{}{}'.format( 
            os.environ.get('DATABASE_HOST'), 
            'politics', 
        ), 
    }