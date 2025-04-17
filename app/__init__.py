from flask import Flask
from .extensions import db, migrate, cors, jwt, login
from .config import config_by_name
from .models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(config_by_name['dev'])

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
    login.init_app(app)

    return app
