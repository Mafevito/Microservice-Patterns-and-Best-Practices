#Este archivo es ligeramente diferente de los otros archivos models.py que escribimos en la aplicación, debido a las características del controlador de base de datos que estamos usando. Al final, no será un modelo compuesto de entidades, sino una agrupación de funciones que trabajan con los datos de la base de datos.

#Debido a que es una base de datos que utiliza gráficos, no importamos tipos no identificables a una base de datos, sino que importamos tipos que crean relaciones en un modelo de gráfico
import os
from py2neo import (
    Graph,
    Node,
    Relationship,
)

#las relaciones serán entre usuarios de aplicaciones y etiquetas de noticias, donde el tipo de relación siempre será una recomendación
USERS_NODE = 'Users'
LABELS_NODE = 'Labels'
REL_TYPE = 'RECOMMENDATION'

#creamos la conexión a la base de datos usando una variable de entorno creada en el archivo docker-compos.yml
graph = Graph(os.getenv('DATABASE_URL'))

#responsable de recuperar el nodo de un usuario, pasando el user_id como parámetro
def get_user_node(user_id):
    return graph.find_one(
        USERS_NODE,
        property_key='id',
        property_value=user_id,
    )

#La segunda función es muy similar a la primera. Sin embargo, busca el nodo utilizando el parámetro etiqueta
def get_label_node(label):
    return graph.find_one(
        LABELS_NODE,
        property_key='id',
        property_value=label,
    )

#responsable de obtener todas las etiquetas que tienen una relación con el usuario. Para esta búsqueda, utilizamos el user_id como parámetro
def get_labels_by_user_id(user_id):
    user_node = get_user_node(user_id)
    return graph.match(
        start_node=user_node,
        rel_type=REL_TYPE,
    )

#La cuarta función es muy similar a la tercera, con la diferencia de que ahora estamos buscando a todos los usuarios relacionados con una etiqueta
def get_users_by_label(label):
    label_node = get_label_node(label)
    return graph.match(
        start_node=label_node,
        rel_type=REL_TYPE,
    )


#AHORA escribiremos las funciones responsables de crear los datos en la base de datos.
#crea un nodo de usuario en Neo4j si el nodo no ha sido creado previamente en la base de datos
def create_user_node(user):
    # get user info from UsersService
    if not get_user_node(user['id']):
        user_node = Node(
            USERS_NODE,
            id=user['id'],
            name=user['name'],
            email=user['email'],
        )
        graph.create(user_node)

#realiza el mismo proceso que la primera, pero crea nodos de etiqueta
def create_label_node(label):
    # get user info from UsersService
    if not get_label_node(label):
        label_node = Node(LABELS_NODE, id=label)
        graph.create(label_node)

#La tercera función funciona creando la relación usuario/etiqueta y etiqueta/usuario. Al ejecutar el proceso de relación en ambos lados, estamos permitiendo que el proceso de búsqueda se ejecute en ambos lados; de lo contrario, esto no sería posible
def create_recommendation(user_id, label):
    user_node = get_user_node(user_id)
    label_node = get_label_node(label)
    graph.create(Relationship(
        label_node,
        REL_TYPE,
        user_node,
    ))
    graph.create(Relationship(
        user_node,
        REL_TYPE,
        label_node,
    ))