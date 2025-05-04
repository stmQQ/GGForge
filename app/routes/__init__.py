from .auth_routes import auth_bp
from .user_routes import user_bp
# from .match_routes import match_bp
from .tournament_routes import tournament_bp
# from .admin_routes import admin_bp
# from .common_routes import common_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    # app.register_blueprint(match_bp)
    app.register_blueprint(tournament_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(common_bp)
