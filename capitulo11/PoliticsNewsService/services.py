#archivo responsable de establecer la comunicación con el creador de mensajes

#declaración de dependencias, modelos y todo lo necesario para el uso de nameko
import mongoengine 
 
from models import ( 
    CommandNewsModel, 
    Base, 
    QueryNewsModel, 
) 
 
from sqlalchemy import Sequence 
 
from nameko.events import EventDispatcher 
from nameko.rpc import rpc 
from nameko.events import event_handler 
from nameko_sqlalchemy import DatabaseSession

#clase responsable del comando. Los tres primeros son los atributos de clase que definen el nombre del comando e instancian el despachador de eventos y la base de datos de inyección de dependencias respectivamente
class Command: 
    name = 'command_famous' 
    dispatch = EventDispatcher() 
    db = DatabaseSession(Base)

#método con el decorador de rpc. El decorador procede del marco Nameko y establece el modelo de comunicación RPC. Como estamos utilizando el patrón interno de abastecimiento de eventos junto con CQRS, debemos prestar atención a algunas peculiaridades

#el método add_news formará parte de la llamada RPC dentro del microservicio de orquestación. Este método es imperativo y representa un comando para crear noticias
@rpc 
    def add_news(self, data):

#Este flujo de control verifica si es algo nuevo o una nueva versión del artículo de Noticias existente
try: 
            version = 1 
            if data.get('version'): 
                version = (data.get('version') + 1) 
            if data.get('id'): 
                id = data.get('id') 
            else: 
                id = self.db.execute(Sequence('news_id_seq'))

#responsable del registro de News en la base de datos
news = CommandNewsModel( 
                id=id, 
                version=version, 
                title=data['title'], 
                content=data['content'], 
                author=data['author'], 
                published_at=data.get('published_at'), 
                tags=data['tags'], 
            ) 
            self.db.add(news) 
            self.db.commit()

#con el proceso de registro en la base de datos normalizada definida, trabajaremos en el envío de un evento a registrar en la base de datos no normalizada, es decir, en la base de datos QueryStack

#generamos un nuevo evento utilizando la llamada RPC para informar de lo ocurrido al comando add_news
data['id'] = news.id 
            data['version'] = news.version 
            self.dispatch('replicate_db_event', data) 
            return data
#si tenemos algún problema en nuestro proceso, ejecutaremos un rollback en la base estándar. De manera más deferente, comprenderemos por qué no realizamos el mismo procedimiento en la base de datos no estandarizada
            except Exception as e: 
            self.db.rollback() 
            return e

#Después de crear la capa CommandStack, vamos al desarrollo de QueryStack
class Query: 
    name = 'query_famous'

#handler responsable de escuchar el evento que fue enviado por CommandStack
@event_handler('command_famous', 'replicate_db_event') 
    def normalize_db(self, data):

#Nuestra base de datos QueryStack tendrá una característica muy peculiar. Esta base no será un espejo completo de la base de datos CommandStack, sino más bien una base de datos especializada, con sólo los últimos datos de un artículo de noticias respectivo.

#Para hacer de esta una base de datos especializada, primero buscaremos datos sobre un artículo de noticias. Si no se genera ningún evento con los datos de noticias que hemos buscado, hemos creado un nuevo registro de noticias.
try: 
            news = QueryNewsModel.objects.get( 
                id=data['id'] 
            ) 
            news.update( 
                version=data.get('version', news.version), 
                title=data.get('title', news.title), 
                content=data.get('content', news.content), 
                author=data.get('author', news.author), 
                published_at=data.get('published_at', news.published_at), 
                tags=data.get('tags', news.tags), 
            ) 
            news.reload() 
        except mongoengine.DoesNotExist: 
            QueryNewsModel( 
                id=data['id'], 
                version=data['version'], 
                title=data.get('title'), 
                content=data.get('content'), 
                author=data.get('author'), 
                tags=data.get('tags'), 
            ).save() 
        except Exception as e: 
            return e

#crear los puntos de acceso para los datos de QueryStack. Primero, cree la búsqueda de ID. Escribamos un método get_news que tenga un decorador RPC de Nameko. Dentro del método get_news, no hay complejidad; simplemente usaremos MongoEngine para buscar Noticias usando el ID único como referencia
@rpc 
    def get_news(self, id): 
        try: 
            news = QueryNewsModel.objects.get(id=id) 
            return news.to_json() 
        except mongoengine.DoesNotExist as e: 
            return e 
        except Exception as e: 
            return e

#crearemos otra solicitud RPC que será una búsqueda por páginas de todas las noticias registradas en nuestra base de datos
@rpc 
    def get_all_news(self, num_page, limit): 
        try: 
            if not num_page: 
                num_page = 1 
            offset = (num_page - 1) * limit 
            news = QueryNewsModel.objects.skip(offset).limit(limit) 
            return news.to_json() 
        except Exception as e: 
            return e


#tenemos nuestro microservicio funcional de nuevo.