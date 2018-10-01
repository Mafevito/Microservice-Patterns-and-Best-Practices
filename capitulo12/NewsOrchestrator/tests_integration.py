import json
import unittest
from app import app
from flask_testing import TestCase

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

#crearemos una clase para toda la prueba de integración
class TestIntegration(BaseTestCase):

#Ahora, escribamos el método setUp. Este método se ejecuta siempre que se instancie la clase y antes que cualquier otro método. Tenga en cuenta que estamos haciendo un HTTP POST para el microservicio, pero no hay simulacros. Esto significa que estamos efectivamente persistiendo en la información de la base de datos. Cuando ejecutamos setUp, estamos guardando la respuesta y el JSON devuelve las variables de instancia
def setUp(self):
        dict_obj = dict(
            title='My Test',
            content='Just a service test',
            author='unittest',
            tags=['Test', 'unit_test'],
        )
        with self.client:
            self.response_post = self.client.post(
                '/famous',
                data=json.dumps(dict_obj),
                content_type='application/json',
            )
            self.data_post = json.loads(
                self.response_post.data.decode()
            )

        #primer test de integración sólo valida si la información de post es perfecta
        def test_add_news(self):
        """Test to insert a News."""
        self.assertEqual(self.response_post.status_code, 201)
        self.assertEqual('success', self.data_post['status'])
        self.assertEqual('My Test', self.data_post['news']['title'])

        #segunda prueba de integración hace una llamada a get_single_news y se integra con el microservicio FamousNewsService. Aquí está el ID del artículo que acabamos de crear
        def test_get_single_news(self):
        response = self.client.get(
            'famous/{id}'.format(id=self.data_post['news']['id'])
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertTrue(len(data['news']) > 0)
        self.assertEqual(data['news']['title'], 'My Test')
        self.assertEqual(data['news']['content'], 'Just a service test')
        self.assertEqual(data['news']['author'], 'unittest')

        #Al final, tenemos una vez más la condición de que se realicen las pruebas de integración
        if __name__ == '__main__':
        unittest.main()
