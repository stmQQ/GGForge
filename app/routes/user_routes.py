from flask import Blueprint, request, jsonify
from uuid import UUID
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)
from app.extensions import db
from app.models import User, Connection, UserRequest, GameAccount
from app.services.user_service import (
    create_support_ticket, get_user_profile, get_user_tickets, update_user,
    save_avatar, delete_avatar, create_game_account_if_absent, unlink_game_account
)
from app.schemas import (
    UserSchema, UserRequestSchema, GameAccountSchema, SupportTokenSchema
)  # Import necessary schemas
from datetime import datetime, UTC

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

# region Profiles


@user_bp.route('/profile/<uuid:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    user_schema = UserSchema(only=('id', 'name', 'avatar', 'last_online'))
    return user_schema.dump(user), 200


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    user_schema = UserSchema(
        only=('id', 'name', 'email', 'avatar', 'last_online', 'is_banned', 'ban_until'))
    return user_schema.dump(user), 200


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    avatar_file = request.files.get('avatar')

    avatar_url = None
    if avatar_file:
        try:
            delete_avatar(user.avatar)
            avatar_url = save_avatar(avatar_file, user_id=user_id)
        except ValueError as e:
            return jsonify({'msg': str(e)}), 400

    updated_user = update_user(
        user_id=user_id,
        name=name,
        email=email,
        password=password,
        avatar=avatar_url
    )

    user_schema = UserSchema(only=('id', 'name', 'email', 'avatar'))
    return {
        'msg': 'Профиль обновлен',
        'user': user_schema.dump(updated_user)
    }, 200


@user_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    db.session.delete(user)
    db.session.commit()

    return {'msg': 'Пользователь успешно удален'}, 200


@user_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'msg': 'Неверный текущий пароль'}), 401

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return {'msg': 'Пароль успешно изменен'}, 200


@user_bp.route('/me/avatar', methods=['PATCH'])
@jwt_required()
def change_avatar():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    avatar_file = request.files.get('avatar')

    if not avatar_file:
        return jsonify({'msg': 'Пожалуйста, загрузите новый аватар'}), 400

    try:
        delete_avatar(user.avatar)
        avatar_url = save_avatar(avatar_file, user_id=user_id)
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400

    user.avatar = avatar_url
    db.session.commit()

    return {'msg': 'Аватар успешно обновлен', 'avatar': avatar_url}, 200


@user_bp.route('/me/ping', methods=['POST'])
@jwt_required()
def user_ping():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    user.is_online = True
    user.last_online = datetime.now(UTC)
    db.session.commit()

    return {'msg': 'Пинг получен'}, 200

# endregion


@user_bp.route('/search', methods=['GET'])
def search_user():
    nickname = request.args.get('nickname')

    if not nickname:
        return jsonify({'msg': 'Пожалуйста, укажите никнейм для поиска'}), 400

    users = User.query.filter(User.name.ilike(f"%{nickname}%")).all()

    user_schema = UserSchema(many=True, only=('id', 'name', 'avatar'))
    return user_schema.dump(users), 200


@user_bp.route('/me/friends', methods=['POST'])
@jwt_required()
def send_friend_request():
    user_id = UUID(get_jwt_identity())

    # Получаем JSON из запроса
    data = request.get_json()
    if not data or 'target_user_id' not in data:
        return jsonify({'msg': 'Не указан target_user_id'}), 400

    target_user_id_str = data['target_user_id']

    # Проверяем и преобразуем target_user_id в UUID
    try:
        target_user_id = UUID(target_user_id_str)
    except ValueError:
        return jsonify({'msg': 'Некорректный формат target_user_id'}), 400

    # Проверяем, что пользователь не отправляет заявку самому себе
    if user_id == target_user_id:
        return jsonify({'msg': 'Нельзя отправить заявку самому себе'}), 400

    # Проверяем существование целевого пользователя
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    # Проверяем, не отправлена ли уже заявка
    existing_request = UserRequest.query.filter_by(
        from_user_id=user_id, to_user_id=target_user_id).first()
    if existing_request:
        return jsonify({'msg': 'Заявка уже отправлена'}), 400

    # Создаём новую заявку
    friend_request = UserRequest(
        from_user_id=user_id,
        to_user_id=target_user_id,
        type='friend'
    )

    try:
        db.session.add(friend_request)
        db.session.commit()
        return jsonify({'msg': 'Заявка на дружбу отправлена'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Ошибка при сохранении заявки: {str(e)}'}), 500


@user_bp.route('/me/friends/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    user_id = get_jwt_identity()

    try:
        # Преобразуем user_id в UUID, если он строка
        user_id_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат user_id'}), 400

    # Получаем входящие и исходящие заявки
    incoming_requests = UserRequest.query.filter_by(
        to_user_id=user_id_uuid).all()
    outgoing_requests = UserRequest.query.filter_by(
        from_user_id=user_id_uuid).all()

    # Настраиваем схему для сериализации
    user_request_schema = UserRequestSchema(
        many=True,
        only=('id', 'from_user', 'to_user')
    )

    # Сериализуем заявки
    try:
        incoming_data = user_request_schema.dump(incoming_requests)
        outgoing_data = user_request_schema.dump(outgoing_requests)
    except Exception as e:
        return jsonify({'msg': f'Ошибка сериализации: {str(e)}'}), 500

    return jsonify({
        'incoming_requests': incoming_data,
        'outgoing_requests': outgoing_data
    }), 200


@user_bp.route('/me/friends/requests/<uuid:request_id>', methods=['POST'])
@jwt_required()
def respond_to_friend_request(request_id):
    user_id = UUID(get_jwt_identity())

    action = request.json.get('action')

    friend_request = UserRequest.query.get(request_id)
    if not friend_request:
        return jsonify({'msg': 'Заявка не найдена'}), 404
    if friend_request.to_user_id != user_id:
        return jsonify({'msg': 'Это не ваша заявка'}), 403

    if action == 'accept':
        user = User.query.get(user_id)
        user.friends.append(friend_request.from_user)
        friend_request.from_user.friends.append(user)
        db.session.delete(friend_request)
        db.session.commit()

        return {'msg': 'Заявка на дружбу принята'}, 200

    elif action == 'reject':
        db.session.delete(friend_request)
        db.session.commit()

        return {'msg': 'Заявка отклонена'}, 200

    return jsonify({'msg': 'Неверное действие'}), 400


@user_bp.route('/me/friends', methods=['GET'])
@jwt_required()
def get_friends():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    user_schema = UserSchema(only=('friends',))
    return user_schema.dump(user)['friends'], 200


@user_bp.route('/me/friends/<uuid:friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    friend = User.query.get(friend_id)

    if not user or not friend:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    if friend not in user.friends:
        return jsonify({'msg': 'Этот пользователь не в списке ваших друзей'}), 400

    user.friends.remove(friend)
    friend.friends.remove(user)
    db.session.commit()

    return {'msg': 'Друг удален'}, 200

# region GameAccounts


@user_bp.route('/me/game_accounts', methods=['POST'])
@jwt_required()
def add_game_account():
    user_id = get_jwt_identity()
    data = request.get_json()

    game_id = data.get('game_id')
    service_name = data.get('service_name')
    external_user_url = data.get('external_user_url')

    if not all([game_id, service_name, external_user_url]):
        return jsonify({'msg': 'Необходимо указать game_id, service_name и external_user_url'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    existing_connection = Connection.query.filter_by(
        service_name=service_name,
        external_user_url=external_user_url,
        user_id=user_id
    ).first()

    if existing_connection:
        existing_account = GameAccount.query.filter_by(
            user_id=user_id,
            connection_id=existing_connection.id
        ).first()

        if existing_account:
            return jsonify({'msg': 'Такой игровой аккаунт уже привязан'}), 409

    account = create_game_account_if_absent(
        user_id=user_id,
        connection_id=None,
        game_id=game_id,
        service_name=service_name,
        external_url=external_user_url
    )

    game_account_schema = GameAccountSchema(only=(
        'id', 'game_id', 'connection.service_name', 'connection.external_user_url'))
    return {
        'msg': 'Игровой аккаунт успешно добавлен',
        'account': game_account_schema.dump(account)
    }, 201


@user_bp.route('/me/game_accounts/<uuid:connection_id>', methods=['DELETE'])
@jwt_required()
def delete_game_account(connection_id):
    user_id = get_jwt_identity()

    unlink_game_account(user_id=user_id, connection_id=connection_id)

    return {'msg': 'Игровой аккаунт успешно удален'}, 200


@user_bp.route('/me/game_accounts', methods=['GET'])
@jwt_required()
def list_game_accounts():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    game_account_schema = GameAccountSchema(many=True, only=(
        'id', 'game_id', 'connection.service_name', 'connection.external_user_url'))
    return game_account_schema.dump(user.game_accounts), 200

# region SupportTickets


@user_bp.route('/me/support_tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    user_id = get_jwt_identity()
    data = request.get_json()

    theme = data.get('theme')
    text = data.get('text')

    if not theme or not text:
        return jsonify({'msg': 'Тема и текст обязательны'}), 400

    ticket = create_support_ticket(user_id=user_id, theme=theme, text=text)

    if ticket is None:
        return jsonify({'msg': 'Сообщение не может быть пустым'}), 400

    support_token_schema = SupportTokenSchema(
        only=('id', 'theme', 'text', 'status', 'created_at'))
    return {
        'msg': 'Тикет успешно создан',
        'ticket': support_token_schema.dump(ticket)
    }, 201


@user_bp.route('/me/support_tickets', methods=['GET'])
@jwt_required()
def get_my_tickets():
    user_id = get_jwt_identity()
    tickets = get_user_tickets(user_id=user_id)

    support_token_schema = SupportTokenSchema(
        many=True, only=('id', 'theme', 'text', 'status', 'created_at'))
    return support_token_schema.dump(tickets), 200

# endregion
