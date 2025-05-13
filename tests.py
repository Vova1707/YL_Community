from app import app
from db_session import global_init


class TestView:
    def setup_method(self):
        global_init(app.config['DATABASE_URI'])
        app.testing = True
        self.client = app.test_client()

    def test_connection(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def teardown_method(self):
        print('\nТесты завершены')
