#Primero, declaremos nuestras declaraciones de importación. 
import json
import unittest
from app import app
from flask_testing import TestCase #será la base de todas nuestras pruebas.Esta herramienta proporciona un par de funcionalidades interesantes, incluyendo cómo acceder a la configuración de los clientes Flask y HTTP

#escribimos la clase base para nuestras pruebas funcionales. Utilizamos la configuración de TestingConfig para esta tarea
class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

#declaramos las pruebas unitarias de nuestra capa de configuración
class TestDevelopmentConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)


class TestTestingConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])


class TestProductionConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])

#prueba de nuestras rutas como ejemplo. En este caso, estamos intentando crear un microservicio de noticias. Se trata de una prueba funcional, ya que accedemos a la aplicación a través del endpoint y comprobamos el resultado recibido
class TestNewsService(BaseTestCase):
    def test_add_news(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/famous/news',
                data=json.dumps(dict(
                    title='My Test',
                    content='Just a service test',
                    author='unittest',
                    tags=['Test', 'Functional_test'],
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            self.assertIn('My Test', data['news']['title'])

#código responsable de realizar las pruebas en una llamada de Python
if __name__ == '__main__':
unittest.main()