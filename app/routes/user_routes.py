from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)
from app.extensions import db
from app.models import User
from datetime import timedelta
from app.services.user_service import get_user_profile

client_bp = Blueprint('client', __name__, url_prefix='/api/client')


@client_bp.route('/profile/<uuid:user_id>', methods=['GET'])
def profile(user_id):
    user_data = get_user_profile(user_id=user_id)
    return jsonify(user_data)