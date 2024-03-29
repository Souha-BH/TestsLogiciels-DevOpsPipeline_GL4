import uvicorn
from fastapi import FastAPI
from client.external_musician_client import ExternalMusicianClient
from client.postgres_client import PostgresClient
from config.external_musicians_client_config import ExternalMusicianClientConfig
from config.postgres_client_config import PostgresClientConfig
from repository.musician_repository import MusicianRepository
from rest_api.musician_rest_api import MusicianRestApi
from service.musician_service import MusicianService
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def start_application():
    postgres_url = "localhost"
    postgres_port = 8080
    postgres_database = "musicians"
    postgres_user_name = "postgres"
    postgres_password = "postgres"
    external_client_url = "http://localhost"
    external_client_port = 8080

    postgres_client_config = PostgresClientConfig(url=postgres_url,
                                                  port=postgres_port,
                                                  database=postgres_database,
                                                  user_name=postgres_user_name,
                                                  password=postgres_password)
    postgres_client = PostgresClient(postgres_client_config)
    musician_repository = MusicianRepository(postgres_client=postgres_client)

    external_musician_client_config = ExternalMusicianClientConfig(url=external_client_url, port=external_client_port)
    external_musician_client = ExternalMusicianClient(external_musician_client_config)

    musician_service = MusicianService(musician_repository=musician_repository,
                                       external_musician_client=external_musician_client)
    musician_rest_api = MusicianRestApi(musician_service=musician_service)
    return musician_rest_api
    #data = jsonable_encoder({"data": "Hello World"})
    #return JSONResponse(content=data)

if __name__ == "__main__":
    uvicorn.run(app=start_application())
