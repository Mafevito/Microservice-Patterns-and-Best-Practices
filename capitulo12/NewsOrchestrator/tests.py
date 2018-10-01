import json
import unittest

from mock import patch #estamos importando el decorador de parches desde el paquete simulado. Esto será muy útil para crear pruebas unitarias determinísticas

from app import app
from views import error_response

from flask_testing import TestCase

#clase BaseTestCase, que es responsable de cargar los ajustes básicos de la prueba
class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

#hemos creado las pruebas que validan los ajustes de nuestro entorno de desarrollo
class TestDevelopmentConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)

#las pruebas que validan la configuración de la pruebas
class TestTestingConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])

#Para finalizar las pruebas de configuración, los casos que validan las configuraciones para producción son los siguientes
class TestProductionConfig(TestCase)

    def create_app(self):
        app.config.from_object('config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])

#creamos una prueba unitaria para cuando buscamos un artículo de noticias. Primero, declaramos la clase de prueba
class TestGetSingleNews(BaseTestCase):
    #método que valida el caso de éxito de la búsqueda. Tenga en cuenta que estamos aplicando el decorador de parches, que nos permite crear el simulacro para la función rpc_get_news y para la función event_dispatcher. Las instancias de los parches se pasan por inyección de dependencia
    @patch('views.rpc_get_news')
    @patch('nameko.standalone.events.event_dispatcher')
    def test_success(self, event_dispatcher_mock, rpc_get_news_mock):
        #declararemos los valores que deben ser devueltos por los mocks. El primer simulacro es el event_dispatcher_mock, donde se pasará una función anónima que toma los valores y no hace nada. El segundo simulacro se refiere a la devolución de la RPC
        event_dispatcher_mock.return_value = lambda v1, v2, v3: None
        rpc_get_news_mock.return_value = {
            "news": [
                {
                    "_id": 1,
                    "author": "unittest",
                    "content": "Just a service test",
                    "created_at": {
                        "$date": 1514741833010
                    },
                    "news_type": "famous",
                    "tags": [
                        "Test",
                        "unit_test"
                    ],
                    "title": "My Test",
                    "version": 1
                }
            ],
            "status": "success"
        }

        #Ahora, llamaremos al endpoint get_single_news enviando un ID de artículo de noticias como parámetro. Luego, interpretamos la llamada que viene de los mocks y validamos la respuesta
        With self.client:
        response = self.client.get('/famous/1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertTrue(len(data['news']) > 0)
            for d in data['news']:
                self.assertEqual(d['title'], 'My Test')
                self.assertEqual(d['content'], 'Just a service test')
                self.assertEqual(d['author'], 'unittest')

       #Utilizaremos un proceso muy similar para validar un evento de fallo del mismo endpoint get_single_news. También usamos los decoradores de parches y pasamos los valores a las burlas, pero en este caso, estamos forzando un error. Tenga en cuenta que rpc_get_news_mock recibe None como un valor; esto generará un error porque la función no sabe cómo trabajar usando el valor None. Al final del proceso, validamos si el mensaje de error es lo que esperamos
       @patch('views.rpc_get_news')
    @patch('nameko.standalone.events.event_dispatcher')
    def test_fail(self, event_dispatcher_mock, rpc_get_news_mock):
        event_dispatcher_mock.return_value = lambda v1, v2, v3: None
        rpc_get_news_mock.return_value = None
        response = self.client.get('/famous/1')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 500)
        self.assertEqual('fail', data['status'])
        self.assertEqual("'NoneType' object is not subscriptable", data['message'])

        #Después de probar la búsqueda de un artículo de noticias, probaremos la creación. Una vez más, declaramos una clase para la prueba unitaria
        class TestAddNews(BaseTestCase):
            #nuestro parche será de la función rpc_command. Una vez más, la instancia del parche se pasa como parámetro del método de prueba a través de la inyección de dependencia
            @patch('views.rpc_command')
            def test_sucess(self, rpc_command_mock):
            """Test to insert a News."""

        #crear un dictado que será la entrada de datos y también será parte de la respuesta esperada
        dict_obj = dict(
            title='My Test',
            content='Just a service test',
            author='unittest',
            tags=['Test', 'unit_test'],
        )
        rpc_command_mock.return_value = {
            'status': 'success',
            'news': dict_obj,
        }
        with self.client:
            response = self.client.post(
                '/famous',
                data=json.dumps(dict_obj),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual('success', data['status'])
            self.assertEqual('My Test', data['news']['title'])
        
        #En este escenario, estamos asignando el valor Ninguno a dic_obj. Esto creará un error, indicando que la carga útil recibida por la función add_news es inválida
        def test_fail_by_invalid_input(self):
        dict_obj = None
        with self.client:
            response = self.client.post(
                '/famous',
                data=json.dumps(dict_obj),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual('fail', data['status'])
            self.assertEqual('Invalid payload', data['message'])

        #Es muy importante pensar en una variedad de escenarios para las pruebas unitarias. Escribimos una prueba que valida lo que ocurre cuando se pasa una carga útil errónea, pero ¿qué pasa si el problema está en el microservicio que registra la carga útil en una base de datos? Es exactamente esta prueba la que vamos a escribir ahora
        #Primero, aplicamos el decorador con el parche y luego creamos el diccionario con una carga útil válida
        @patch('views.rpc_command')
        def test_fail_to_register(self, rpc_command_mock):
        """Test to insert a News."""
        dict_obj = dict(
            title='My Test',
            content='Just a service test',
            author='unittest',
            tags=['Test', 'unit_test'],
        )

        #vamos a crear el simulacro con un efecto secundario, que dará lugar a una excepción. Completamos el proceso de envío de información llamando al punto final de la función add_news
        rpc_command_mock.side_effect = Exception('Forced test fail')
        with self.client:
            response = self.client.post(
                '/famous',
                data=json.dumps(dict_obj),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())

        #validaremos si recibimos el mensaje enviado por la excepción del simulacro
        self.assertEqual(response.status_code, 500)
        self.assertEqual('fail', data['status'])
        self.assertEqual('Forced test fail', data['message'])

        #La siguiente clase validará la función get_all_news_per_type usando pruebas unitarias. El proceso es exactamente el mismo que hemos aplicado hasta ahora. Hacemos una declaración de la clase, luego usamos un decorador para el parche, creamos el simulacro, llamamos al punto final y validamos lo que se devuelve
        class TestGetAllNewsPerType(BaseTestCase):

        @patch('views.rpc_get_all_news')
        def test_sucess(self, rpc_get_all_news_mock):
        """Test to get all News paginated."""
        rpc_get_all_news_mock.return_value = {
            "news": [
                {
                    "_id": 1,
                    "author": "unittest",
                    "content": "Just a service test 1",
                    "created_at": {
                        "$date": 1514741833010
                    },
                    "news_type": "famous",
                    "tags": [
                        "Test",
                        "unit_test"
                    ],
                    "title": "My Test 1",
                    "version": 1
                },
                {
                    "_id": 2,
                    "author": "unittest",
                    "content": "Just a service test 2",
                    "created_at": {
                        "$date": 1514741833010
                    },
                    "news_type": "famous",
                    "tags": [
                        "Test",
                        "unit_test"
                    ],
                    "title": "My Test 2",
                    "version": 1
                },
            ],
            "status": "success"
        }
        with self.client:
            response = self.client.get('/famous/1/10')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertEqual(2, len(data['news']))
            counter = 1
            for d in data['news']:
                self.assertEqual(
                    d['title'],
                    'My Test {}'.format(counter)
                )
                self.assertEqual(
                    d['content'],
                    'Just a service test {}'.format(counter)
                )
                self.assertEqual(
                    d['author'],
                    'unittest'
                )
                counter += 1

        #vamos a crear una prueba unitaria para el caso de fallo
        @patch('views.rpc_get_all_news')
        def test_fail(self, rpc_get_all_news_mock):
        """Test to get all News paginated."""
        rpc_get_all_news_mock.side_effect = Exception('Forced test fail')
        with self.client:
            response = self.client.get('/famous/1/10')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 500)
            self.assertEqual('fail', data['status'])
            self.assertEqual('Forced test fail', data['message'])
        
        #valida si la función responsable de encapsular la lógica de los mensajes de error está funcionando correctamente
        class TestUtilsFunctions(BaseTestCase):
    def test_error_message(self):
        response = error_response('test message error', 500)
        data = json.loads(response[0].data.decode())
        self.assertEqual(response[1], 500)
        self.assertEqual('fail', data['status'])
        self.assertEqual('test message error', data['message'])

        #Al final del archivo, escribimos una condición para que se pueda ejecutar la herramienta de prueba nativa de Python
        if __name__ == '__main__':
        unittest.main()














