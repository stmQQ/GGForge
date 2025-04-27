from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)
from app.extensions import db
from app.models import User, Connection, UserRequest, GameAccount
from app.services.user_service import create_support_ticket, get_user_profile, get_user_tickets, update_user, save_avatar, delete_avatar, create_game_account_if_absent, unlink_game_account

from datetime import timedelta

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


#region Profiles

@user_bp.route('/profile/<uuid:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    return jsonify({
        'id': str(user.id),
        'name': user.name,
        'avatar': user.avatar,
        'last_online': user.last_online.isoformat() if user.last_online else None
    }), 200


# Просмотр своего профиля
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    return jsonify({
        'id': str(user.id),
        'name': user.name,
        'email': user.email,
        'avatar': user.avatar,
        'last_online': user.last_online.isoformat() if user.last_online else None,
        'is_banned': str(user.is_banned),
        'ban_time': user.ban_time.isoformat() if user.ban_time else None,
    }), 200

# Обновление своего профиля
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
            # Удаляем старый аватар
            delete_avatar(user.avatar)

            # Пытаемся сохранить новый аватар
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

    return jsonify({
        'msg': 'Профиль обновлен',
        'user': {
            'id': str(updated_user.id),
            'name': updated_user.name,
            'email': updated_user.email,
            'avatar': updated_user.avatar
        }
    }), 200


# Удаление своего аккаунта
@user_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'msg': 'Пользователь успешно удален'}), 200


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

    # Проверяем текущий пароль
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'msg': 'Неверный текущий пароль'}), 401

    # Обновляем пароль
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'msg': 'Пароль успешно изменен'}), 200


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
        # Удаляем старый аватар
        delete_avatar(user.avatar)

        # Сохраняем новый аватар
        avatar_url = save_avatar(avatar_file, user_id=user_id)
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400

    user.avatar = avatar_url
    db.session.commit()

    return jsonify({'msg': 'Аватар успешно обновлен', 'avatar': avatar_url}), 200


@user_bp.route('/me/ping', methods=['POST'])
@jwt_required()
def user_ping():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    user.is_online = True
    user.last_online = datetime.utcnow()
    db.session.commit()

    return jsonify({'msg': 'Пинг получен'}), 200

#endregion


@user_bp.route('/search', methods=['GET'])
def search_user():
    nickname = request.args.get('nickname')

    if not nickname:
        return jsonify({'msg': 'Пожалуйста, укажите никнейм для поиска'}), 400

    users = User.query.filter(User.name.ilike(f"%{nickname}%")).all()

    if not users:
        return jsonify({'msg': 'Пользователи не найдены'}), 404

    return jsonify([
        {
            'id': str(user.id),
            'name': user.name,
            'avatar': user.avatar
        } for user in users
    ]), 200


@user_bp.route('/me/friends', methods=['POST'])
@jwt_required()
def send_friend_request():
    user_id = get_jwt_identity()
    target_user_id = request.json.get('target_user_id')

    if user_id == target_user_id:
        return jsonify({'msg': 'Нельзя отправить заявку самому себе'}), 400

    target_user = User.query.get(target_user_id)

    if not target_user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    # Проверка на уже существующие заявки
    existing_request = UserRequest.query.filter_by(from_user_id=user_id, to_user_id=target_user_id).first()
    if existing_request:
        return jsonify({'msg': 'Заявка уже отправлена'}), 400

    # Создаем новую заявку
    friend_request = UserRequest(from_user_id=user_id, to_user_id=target_user_id)
    db.session.add(friend_request)
    db.session.commit()

    return jsonify({'msg': 'Заявка на дружбу отправлена'}), 200


@user_bp.route('/me/friends/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    user_id = get_jwt_identity()

    incoming_requests = UserRequest.query.filter_by(to_user_id=user_id).all()
    outgoing_requests = UserRequest.query.filter_by(from_user_id=user_id).all()

    return jsonify({
        'incoming_requests': [{'id': str(req.from_user.id), 'name': req.from_user.name} for req in incoming_requests],
        'outgoing_requests': [{'id': str(req.to_user.id), 'name': req.to_user.name} for req in outgoing_requests]
    }), 200


@user_bp.route('/me/friends/requests/<uuid:request_id>', methods=['POST'])
@jwt_required()
def respond_to_friend_request(request_id):
    user_id = get_jwt_identity()
    action = request.json.get('action')  # 'accept' или 'reject'

    friend_request = UserRequest.query.get(request_id)

    if not friend_request:
        return jsonify({'msg': 'Заявка не найдена'}), 404

    if friend_request.to_user_id != user_id:
        return jsonify({'msg': 'Это не ваша заявка'}), 403

    if action == 'accept':
        # Добавляем пользователя в друзья
        user = User.query.get(user_id)
        user.friends.append(friend_request.from_user)
        db.session.delete(friend_request)
        db.session.commit()

        return jsonify({'msg': 'Заявка на дружбу принята'}), 200

    elif action == 'reject':
        db.session.delete(friend_request)
        db.session.commit()

        return jsonify({'msg': 'Заявка отклонена'}), 200

    return jsonify({'msg': 'Неверное действие'}), 400


@user_bp.route('/me/friends', methods=['GET'])
@jwt_required()
def get_friends():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    friends = [
        {
            'id': str(friend.id),
            'name': friend.name,
            'avatar': friend.avatar
        }
        for friend in user.friends
    ]

    return jsonify(friends), 200


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

    # Удаляем дружбу в обе стороны
    user.friends.remove(friend)
    friend.friends.remove(user)
    db.session.commit()

    return jsonify({'msg': 'Друг удален'}), 200


#region GameAccounts

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

    # Проверка: есть ли уже у этого пользователя такой connection
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

    # Создаем аккаунт, если всё чисто
    account = create_game_account_if_absent(
        user_id=user_id,
        connection_id=None,
        game_id=game_id,
        service_name=service_name,
        external_url=external_user_url
    )

    return jsonify({
        'msg': 'Игровой аккаунт успешно добавлен',
        'account': {
            'id': str(account.id),
            'game_id': str(account.game_id),
            'service_name': account.connection.service_name,
            'external_user_url': account.connection.external_user_url
        }
    }), 201


@user_bp.route('/me/game_accounts/<uuid:connection_id>', methods=['DELETE'])
@jwt_required()
def delete_game_account(connection_id):
    user_id = get_jwt_identity()

    # Разрываем связь
    unlink_game_account(user_id=user_id, connection_id=connection_id)

    return jsonify({'msg': 'Игровой аккаунт успешно удален'}), 200


@user_bp.route('/me/game_accounts', methods=['GET'])
@jwt_required()
def list_game_accounts():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    accounts = [
        {
            'id': str(acc.id),
            'game_id': str(acc.game_id),
            'service_name': acc.connection.service_name,
            'external_user_url': acc.connection.external_user_url
        }
        for acc in user.game_accounts
    ]

    return jsonify(accounts), 200

#endregion


#region SupportTickets

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

    return jsonify({
        'msg': 'Тикет успешно создан',
        'ticket': {
            'id': str(ticket.id),
            'theme': ticket.theme,
            'text': ticket.text,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat() if hasattr(ticket, 'created_at') else None
        }
    }), 201


@user_bp.route('/me/support_tickets', methods=['GET'])
@jwt_required()
def get_my_tickets():
    user_id = get_jwt_identity()
    tickets = get_user_tickets(user_id=user_id)

    return jsonify([
        {
            'id': str(ticket.id),
            'theme': ticket.theme,
            'text': ticket.text,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat() if hasattr(ticket, 'created_at') else None
        }
        for ticket in tickets
    ]), 200

#endregion