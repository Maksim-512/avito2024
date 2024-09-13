import os


class Config:
    SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    POSTGRES_JDBC_URL = f'jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

