from .base import BaseConfig

class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@host/prod_db'
