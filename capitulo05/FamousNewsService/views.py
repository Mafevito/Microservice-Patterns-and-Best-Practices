#declaramos las importaciones necesarias para el funcionamiento del archivo
import datetime 
import mongoengine 
from flask import Blueprint, jsonify, request 
from models import News

#instanciaremos la clase del frasco llamado Blueprint
famous_news = Blueprint('famous_news', __name__)

#es la encargada de proporcionar una Noticia por ID
@famous_news.route('/famous/news/<string:news_id>', methods=['GET'])

#declaramos el nombre de la función que será nuestra vista. Dentro de la función, hay un dictado como plantilla para crear la respuesta que será enviada por nuestra vista
def get_single_news(news_id): 
    """Get single user details""" 
    response_object = { 
        'status': 'fail', 
        'message': 'User does not exist' 
    }
    try: 
    news = News.objects.get(id=news_id) 
    response_object = { 
        'status': 'success', 
        'data': news, 
    } 
    return jsonify(response_object), 200 
except mongoengine.DoesNotExist:
    return jsonify(response_object), 404

#primera función de vista está en el siguiente formato
@famous_news.route('/famous/news/<string:news_id>', methods=['GET']) 
def get_single_news(news_id): 
    """Get single user details""" 
    response_object = { 
        'status': 'fail', 
        'message': 'User does not exist' 
    } 
    try: 
        news = News.objects.get(id=news_id) 
        response_object = { 
            'status': 'success', 
            'data': news, 
        } 
        return jsonify(response_object), 200 
    except mongoengine.DoesNotExist: 
        return jsonify(response_object), 404

#responsable de traer todas las noticias en forma de página
@famous_news.route('/famous/news/<int:num_page>/<int:limit>', methods=['GET']) 
def get_all_news(num_page, limit): 
    """Get all users""" 
    news = News.objects.paginate(page=num_page, per_page=limit) 
    response_object = { 
        'status': 'success',
        'data': news.items, 
    } 
    return jsonify(response_object), 200

#responsable de la vista de la creación de Noticias
if not post_data: 
        response_object = { 
            'status': 'fail', 
            'message': 'Invalid payload.' 
        } 
        return jsonify(response_object), 400

#después de la validación, instanciamos y guardamos las noticias con los datos de la solicitud
news = News( 
        title=post_data['title'], 
        content=post_data['content'], 
        author=post_data['author'], 
        tags=post_data['tags'], 
    ).save()

#publicación de la noticia, recibe en su ruta el ID de las Noticias que publicamos, realiza la misma búsqueda en la base de datos, realiza una actualización en la fecha de publicación de las Noticias, y devuelve la respuesta HTTP apropiada
@famous_news.route('/famous/news/<string:news_id>/publish/', methods=['GET'])
def publish_news(news_id):
    try:
        news = News.objects.get(id=news_id)
        news.update(published_at=datetime.datetime.now)
        news.reload()
        response_object = {
            'status': 'success',
            'news': news,
        }
        return jsonify(response_object), 200
    except mongoengine.DoesNotExist:
        return jsonify(response_object), 404

#editar noticia
@famous_news.route('/famous/news', methods=['PUT'])
def update_news():
    try:
        post_data = request.get_json()
        news = News.objects.get(id=post_data['news_id'])
        news.update(
            title=post_data.get('title', news.title),
            content=post_data.get('content', news.content),
            author=post_data.get('author', news.author),
            tags=post_data.get('tags', news.tags),
        )
        news.reload()
        response_object = {
            'status': 'success',
            'news': news,
        }
        return jsonify(response_object), 200
    except mongoengine.DoesNotExist:
        return jsonify(response_object), 404

#eliminar noticia
@famous_news.route('/famous/news/<string:news_id>', methods=['DELETE']) 
def delete_news(news_id): 
    News.objects(id=news_id).delete() 
    response_object = { 
        'status': 'success', 
        'news_id': news_id, 
    } 
    return jsonify(response_object), 200