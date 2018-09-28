#este archivo funciona como una especie de controlador de microservicios

#importaciones
import json
import logging
import os
import requests

from nameko.web.handlers import http
from nameko.events import event_handler

from models import (
    create_user_node,
    create_label_node,
    create_recommendation,
    get_labels_by_user_id,
    get_users_by_label,
)

#escribiremos al lector de los mensajes que estarán en el corredor de mensajes. El siguiente código es una clase normal con un método receptor, un decorador que hace que el método se convierta en un manejador para el mensajero
class Recommendation:

    name = 'recommendation'

    # declaring the receiver method as a handler to message broker
    @event_handler('recommendation_sender', 'receiver')
    def receiver(self, data):
        try:
            # getting the URL to do a sequential HTTP request to UsersService
            user_service_route = os.getenv('USER_SERVICE_ROUTE')
            # consuming data from UsersService using the requests lib
            user = requests.get(
                "{}{}".format(
                    user_service_route,
                    data['user_id'],
                )
            )
            # serializing the UsersService data to JSON
            user = user.json()
            # creating user node on Neo4j
            create_user_node(user)
            # getting all tags read
            for label in data['news']['tags']:
                # creating label node on Neo4j
                create_label_node(label)
                # creating the recommendation on Neo4j
                create_recommendation(
                    user['id'],
                    label,
                )
        except Exception as e:
            logging.error('RELATIONSHIP_ERROR: {}'.format(e))

#escribimos el código de la API responsable de informar las recomendaciones registradas por el Servicio de Recomendación
class RecommendationApi:

    name = 'recommnedation_api'

    #recibe user_id como parámetro. Este método devuelve las etiquetas que están relacionadas con el usuario
    @http('GET', '/user/<int:user_id>')
    def get_recommendations_by_user(self, request, user_id):
        """Get recommendations by user_id"""
        try:
            relationship_response = get_labels_by_user_id(user_id)
            http_response = [
                rel.end_node()
                for rel in relationship_response
            ]
            return 200, json.dumps(http_response)
        except Exception as ex:
            error_response(500, ex)

    #recibimos la etiqueta como parámetro y responderemos a todos los IDs de los usuarios que estén relacionados con esta etiqueta
    @http('GET', '/label/<string:label>')
    def get_users_recomendations_by_label(self, request, label):
        """Get users recommendations by label"""
        try:
            relationship_response = get_users_by_label(label)
            http_response = [
                rel.end_node()
                for rel in relationship_response
            ]
            return 200, json.dumps(http_response)
        except Exception as ex:
            error_response(500, ex)

    #función que sirve para ayudar a las respuestas con algunas posibles excepciones
    def error_response(code, ex):
    response_object = {
        'status': 'fail',
        'message': str(ex),
    }
    return code, json.dumps(response_object)