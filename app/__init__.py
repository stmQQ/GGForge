from flask import Flask
from .extensions import db, migrate, cors, jwt, login
from .config import config_by_name
from .models import *
from ascheduler_tasks import register_scheduler

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static')
    app.config.from_object(config_by_name['dev'])

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
    login.init_app(app)

    register_scheduler(app)

    return app
