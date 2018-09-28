#el archivo de dependencias resaltadas se debe a la importación de ClusterRpcProxy. Esta dependencia proviene del marco de Nameko y nos proporcionará una conexión con los otros microservicios
import os 
import json 
import itertools 
 
from flask import Blueprint, jsonify, request 
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.standalone.events import event_dispatcher  #añadido en cap10, para usar el metodo pub/sub

#instancia de Blueprint para determinar las rutas y también el agente de mensajes de acceso a la URI usando el Protocolo de Cola de Mensajes Avanzado (AMPQ)
news = Blueprint('news', __name__) 
BROKER_CONFIG = {'AMQP_URI': os.environ.get('QUEUE_HOST')}

#primera ruta es la que busca los datos por ID.en cuenta que se deben pasar dos parámetros a la ruta: el primero es el tipo de noticia y el segundo es el ID
@news.route('/<string:news_type>/<int:news_id>', methods=['GET']) 
def get_single_news(news_type, news_id): 
    """Get single user details""" 
    try: 
        response_object = rpc_get_news(news_type, news_id) 
        dispatcher = event_dispatcher(BROKER_CONFIG) #añadido cap10, código del despachador
        #añadido cap10. El mensaje enviado al microservicio de Servicio de Recomendación está compuesto por el ID del usuario que busca la noticia. Este user_id es recogido de una cookie de petición como si estuviéramos simulando un usuario que ha iniciado sesión. El otro elemento que compone el mensaje es JSON con todos los datos de las noticias
        dispatcher('recommendation_sender', 'receiver', {
    'user_id': request.cookies.get('user_id'),
    'news': response_object['news'],
})
        return jsonify(response_object), 200 
    except Exception as e: 
        error_response(e, 500)

    #cap10, Ahora, cada vez que llamemos al método get_single_news del microservicio NewsOrchestrator, enviaremos un mensaje a la cola que el microservicio RecommendationService está esperando. 

#Esta ruta se utiliza cuando el consumidor de nuestros microservicios desea información de todas las rutas al mismo tiempo. Esta ruta es una búsqueda por páginas de todas las noticias que tenemos; lo más destacado es realizar una llamada RPC para cada uno de los microservicios y luego organizar los datos para devolverlos en una sola respuesta
@news.route( 
    '/all/<int:num_page>/<int:limit>', 
    methods=['GET']) 
def get_all_news(num_page, limit): 
    try: 
        response_famous = rpc_get_all_news( 
            'famous', 
            num_page, 
            limit 
        ) 
        response_politics = rpc_get_all_news( 
            'politics', 
            num_page,
            limit 
        ) 
        response_sports = rpc_get_all_news( 
            'sports', 
            num_page, 
            limit 
        ) 
     # Summarizing the microservices responses in just one      
        all_news = itertools.chain( 
            response_famous.get('news', []), 
            response_politics.get('news', []), 
            response_sports.get('news', []), 
        ) 
        response_object = { 
            'status': 'success', 
            'news': list(all_news), 
        } 
        return jsonify(response_object), 200 
    except Exception as e: 
        return erro_response(e, 500)

#La tercera ruta es también una búsqueda por páginas, pero para cada tipo de noticia
@news.route( 
    '/<string:news_type>/<int:num_page>/<int:limit>', 
    methods=['GET']) 
def get_all_news_per_type(news_type, num_page, limit): 
    """Get all users""" 
    try: 
        response_object = rpc_get_all_news( 
            news_type, 
            num_page, 
            limit 
        ) 
        return jsonify(response_object), 200 
    except Exception as e:
        return erro_response(e, 500)

#La cuarta ruta recibe un POST o PUT para realizar el envío de nuevos artículos de noticias del microservicio correspondiente.
@news.route('/<string:news_type>', methods=['POST', 'PUT']) 
def add_news(news_type): 
    post_data = request.get_json() 
    if not post_data: 
        return erro_response('Invalid payload', 400) 
    try: 
        response_object = rpc_command(news_type, post_data) 
        return jsonify(response_object), 201 
    except Exception as e: 
        return erro_response(e, 500)

# algunas funciones auxiliares para el trabajo de "view". La primera es error_response; esta función optimiza un código repetitivo para devolver un mensaje de error amigable
def error_response(e, code): 
    response_object = { 
        'status': 'fail', 
        'message': str(e), 
    } 
    return jsonify(response_object), code

#Las otras tres funciones auxiliares se utilizan para decidir cuál realiza la llamada RPC. rpc_get_news, rpc_get_all_news, y rpc_command tienen una lógica muy similar, y se utilizan para llamar a ClusterRpcProxy para establecer la conexión con los servicios profundos
def rpc_get_news(news_type, news_id): 
    with ClusterRpcProxy(BROKER_CONFIG) as rpc: 
        if news_type == 'famous': 
            news = rpc.query_famous.get_news(news_id) 
        elif news_type == 'sports': 
            news = rpc.query_sports.get_news(news_id) 
        elif news_type == 'politics': 
            news = rpc.query_politics.get_news(news_id) 
        else: 
            return erro_response('Invalid News type', 400) 
        return { 
            'status': 'success', 
            'news': json.loads(news) 
        } 
 
 
def rpc_get_all_news(news_type, num_page, limit): 
    with ClusterRpcProxy(BROKER_CONFIG) as rpc: 
        if news_type == 'famous': 
            news = rpc.query_famous.get_all_news(num_page, limit) 
        elif news_type == 'sports': 
            news = rpc.query_sports.get_all_news(num_page, limit) 
        elif news_type == 'politics': 
            news = rpc.query_politics.get_all_news(num_page, limit) 
        else: 
            return erro_response('Invalid News type', 400) 
        return { 
            'status': 'success', 
            'news': json.loads(news) 
        } 
 
def rpc_command(news_type, data): 
    with ClusterRpcProxy(BROKER_CONFIG) as rpc: 
        if news_type == 'famous': 
            news = rpc.command_famous.add_news(data)
            elif news_type == 'sports': 
            news = rpc.command_sports.add_news(data) 
        elif news_type == 'politics': 
            news = rpc.command_politics.add_news(data) 
        else: 
            return erro_response('Invalid News type', 400) 
        return { 
            'status': 'success', 
            'news': news, 
        }