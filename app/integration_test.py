import psycopg2
import testcontainers.compose
import time
import unittest
import pandas as pd
import requests
from threading import Thread
from uuid import uuid4
from flask import Flask, jsonify
from client.external_musician_client import ExternalMusicianClient
from client.postgres_client import PostgresClient
from config.external_musicians_client_config import ExternalMusicianClientConfig
from config.postgres_client_config import PostgresClientConfig
from repository.musician_repository import MusicianRepository
from service.musician_service import MusicianService
from abc import ABC
from pathlib import Path
from fastapi.testclient import TestClient
from musician_application import start_application

RESOURCES_DIRECTORY: Path = Path(__file__).parent / Path("./")

class MockServer(Thread):
    def __init__(self, port: int, url: str):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)
        self.url = url
        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

    def shutdown_server(self):
        requests.get(f"{self.url}:{self.port}/shutdown")
        self.join()

    def add_callback_response(self, url, callback, methods=('GET',)):
        callback.__name__ = str(uuid4())  
        self.app.add_url_rule(url, view_func=callback, methods=methods)

    def add_json_response(self, url, serializable, methods=('GET',)):
        def callback():
            return jsonify(serializable)
        self.add_callback_response(url, callback, methods=methods)

    def run(self):
        self.app.run(port=self.port)

    @staticmethod
    def _shutdown_server():
        from flask import request
        if not 'werkzeug.server.shutdown' in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'
    
class AbstractIntegrationTestClass(ABC):
    COMPOSE_PATH: Path = RESOURCES_DIRECTORY.joinpath("./docker")
    compose = None
    client = None
    server = None
    postgres_url = None
    postgres_port = None
    postgres_database = None
    postgres_user_name = None
    postgres_password = None
    client_url = None
    client_port = None

    @classmethod
    def setup(cls) -> None:
        cls.postgres_url = "localhost"
        cls.postgres_port = 8080
        cls.postgres_database = "musicians"
        cls.postgres_user_name = "postgres"
        cls.postgres_password = "postgres"
        cls.client_url = "http://localhost"
        cls.client_port = 8080
        cls.postgres_client_config = PostgresClientConfig(url=cls.postgres_url,port=cls.postgres_port,database=cls.postgres_database, user_name=cls.postgres_user_name,password=cls.postgres_password)
        cls.client_config = ExternalMusicianClientConfig(url=cls.client_url, port=cls.client_port)
        cls.compose = testcontainers.compose.DockerCompose(cls.COMPOSE_PATH.as_posix())
        cls.compose.start()
        cls.server = MockServer(url=cls.client_url, port=cls.client_port)
        cls.server.start()
        cls.server.add_json_response("/fetch-all-names", dict(musician_names=["ed", "harry"]))

        time.sleep(5)

        cls.client = TestClient(start_application())

    @classmethod
    def tear_down(cls):
        cls.compose.stop()
        cls.server.shutdown_server()

    def create_connection(self):
        return psycopg2.connect(host=self.postgres_client_config.url, port=self.postgres_client_config.port, database=self.postgres_client_config.database, user=self.postgres_client_config.user_name, password=self.postgres_client_config.password)

class MusicianServiceIntegrationTest(unittest.TestCase, AbstractIntegrationTestClass):
    def __generate_musician_service(self) -> MusicianService:
        postgres_url = "localhost"
        postgres_port = 8080
        postgres_database = "musicians"
        postgres_user_name = "postgres"
        postgres_password = "postgres"
        external_client_url = "http://localhost"
        external_client_port = 8080
        postgres_client_config = PostgresClientConfig(url=postgres_url,port=postgres_port, database=postgres_database, user_name=postgres_user_name, password=postgres_password)
        postgres_client = PostgresClient(postgres_client_config)
        musician_repository = MusicianRepository(postgres_client=postgres_client)
        external_musician_client_config = ExternalMusicianClientConfig(url=external_client_url, port=external_client_port)
        external_musician_client = ExternalMusicianClient(external_musician_client_config)
        musician_service = MusicianService(musician_repository=musician_repository, external_musician_client=external_musician_client)
        return musician_service    
    
    #implement fixtures
    @classmethod
    def setUpClass(cls) -> None:
        cls.setup()
        
    @classmethod
    def tearDownClass(cls) -> None:
        cls.tear_down()
     
    def test_get_musician_by_name(self):
        # given
        musician_service = self.__generate_musician_service()

        # when
        musician = musician_service.get_musician_by_name("ed")

        # then
        self.assertIsNotNone(musician)
        self.assertEqual(musician.name, 'ed')
        self.assertEqual(musician.surname, 'sherran')
        self.assertEqual(musician.age, 31)
        self.assertEqual(musician.instrument, 'guitar')

    def test_get_all_musicians(self):
        # given
        musician_service = self.__generate_musician_service()

        # when
        musicians = musician_service.get_all_musicians()

        # then
        self.assertIsNotNone(musicians)
        self.assertEqual(len(musicians), 2)

        self.assertEqual(musicians[0].name, 'ed')
        self.assertEqual(musicians[0].surname, 'sherran')
        self.assertEqual(musicians[0].age, 31)
        self.assertEqual(musicians[0].instrument, 'guitar')

        self.assertEqual(musicians[1].name, 'harry')
        self.assertEqual(musicians[1].surname, 'styles')
        self.assertEqual(musicians[1].age, 28)
        self.assertEqual(musicians[1].instrument, 'vocal')


    
    def test_save_musician(self):
        # given
        name = "adele"
        surname = "adkins"
        age = 34
        instrument = 'vocal'

        musician_service = self.__generate_musician_service()

        # when
        musician_service.save(name=name,
                              surname=surname,
                              age=age,
                              instrument=instrument)

        # then
        connection = self.create_connection()
        query = f"select * from test.musician where name = '{name}' " \
                f"and surname = '{surname}' " \
                f"and age = '{age}' " \
                f"and instrument = '{instrument}' "

        musician_fetched = pd.read_sql(query, con=connection)

        self.assertEqual(len(musician_fetched), 1)
        self.assertEqual(musician_fetched.iloc[0]['name'], name)
        self.assertEqual(musician_fetched.iloc[0]['surname'], surname)
        self.assertEqual(musician_fetched.iloc[0]['age'], age)
        self.assertEqual(musician_fetched.iloc[0]['instrument'], instrument)