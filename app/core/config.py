import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis do .env

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Limite de tamanho da imagem em bytes (5MB)
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # extra = "ignore" # Ignora campos extras no .env, se houver

settings = Settings()