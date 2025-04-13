from app.models.user_models import User, FriendRequest, Friendship, SupportTicket, Connection, GameAccount
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


#region User operations

def create_user(username, email, password, steam_id=None, battlenet_id=None, battlenet_region=None, avatar="default", role="player"):
    """Создает нового пользователя"""
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        steam_id=steam_id,
        battlenet_id=battlenet_id,
        battlenet_region=battlenet_region,
        role=role,
        avatar=avatar,
        is_banned=False,
        ban_time=None
    )
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user_id, username=None, email=None, password=None, steam_id=None, battlenet_id=None, battlenet_region=None, avatar=None):
    """Обновляет данные пользователя"""
    user = User.query.get(user_id)
    if not user:
        return None  # Пользователь не найден
    
    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.password_hash = generate_password_hash(password)
    if steam_id:
        user.steam_id = steam_id
    if battlenet_id:
        user.battlenet_id = battlenet_id
    if battlenet_region:
        user.battlenet_region = battlenet_region
    if avatar:
        user.avatar = avatar
    
    db.session.commit()
    return user  # Возвращаем обновленного пользователя


def delete_user(user_id):
    """Удаляет пользователя"""
    user = User.query.get(user_id)
    if not user:
        return None
    db.session.delete(user)
    db.session.commit()
    return True


def get_user_profile(user_id):
    """Возвращает информацию о пользователе (без пароля)"""
    user = User.query.get(user_id)
    
    if not user:
        return None  # Пользователь не найден
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "steam_id": user.steam_id,
        "battlenet_id": user.battlenet_id,
        "battlenet_region": user.battlenet_region,
        "admin_role": user.admin_role,
        "is_banned": user.is_banned,
        "ban_time": user.ban_time,
        "avatar": user.avatar
    }


def reset_password(email, new_password):
    """Позволяет пользователю установить новый пароль, если email найден"""
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return None  # Пользователь не найден
    
    user.password_hash = generate_password_hash(new_password)  # Хешируем новый пароль
    db.session.commit()

    return True



#endregion

#region Administrating and support

def get_all_users():
    """Возвращает список всех пользователей"""
    return User.query.all()


def ban_user(user_id, ban_days=None):
    """Банит пользователя на определенное количество дней (если не указано, бан перманентный)"""
    user = User.query.get(user_id)
    if not user:
        return None  # Пользователь не найден
    
    user.is_banned = True
    user.ban_time = datetime.now(datetime.timezone.utc) + timedelta(days=ban_days) if ban_days else None  # Если ban_days не указано – бан навсегда

    db.session.commit()
    return user  # Возвращаем обновленного пользователя


def unban_user(user_id):
    """Разбанивает пользователя"""
    user = User.query.get(user_id)
    if not user:
        return None  # Пользователь не найден
    
    user.is_banned = False
    user.ban_time = None  # Обнуляем время бана

    db.session.commit()
    return user  # Возвращаем обновленного пользователя


def create_support_ticket(user_id, message):
    """Создает запрос в поддержку"""
    if not message.strip():
        return None  # Сообщение не может быть пустым

    ticket = SupportTicket(user_id=user_id, message=message, status="open")
    db.session.add(ticket)
    db.session.commit()
    
    return ticket


def get_all_tickets():
    """Возвращает список всех тикетов"""
    return SupportTicket.query.all()


def get_user_tickets(user_id):
    """Возвращает список тикетов пользователя"""
    return SupportTicket.query.filter_by(user_id=user_id).all()


def update_ticket_status(ticket_id, status):
    """Обновляет статус тикета в поддержку (open, in_progress, closed)"""
    ticket = SupportTicket.query.get(ticket_id)
    
    if not ticket:
        return None  # Тикет не найден
    
    if status not in ["open", "in_progress", "closed"]:
        return None  # Некорректный статус
    
    ticket.status = status
    db.session.commit()

    return ticket


def respond_to_ticket(ticket_id, response):
    """Добавляет ответ администратора в тикет"""
    ticket = SupportTicket.query.get(ticket_id)
    
    if not ticket or ticket.status == "closed":
        return None  # Тикет не найден или уже закрыт
    
    ticket.response = response
    ticket.status = "in_progress"  # Меняем статус, если он еще открыт
    db.session.commit()

    return ticket

#endregion

#region Friendship system

def send_friend_request(sender_id, receiver_id):
    """Отправка запроса в друзья"""
    request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status="pending")
    db.session.add(request)
    db.session.commit()
    return request


def accept_friend_request(request_id):
    """Принятие заявки в друзья"""
    friend_request = FriendRequest.query.get(request_id)
    
    if not friend_request or friend_request.status != "pending":
        return None  # Запрос не найден или уже обработан

    # Обновляем статус запроса
    friend_request.status = "accepted"

    # Добавляем запись в список друзей (если нужно)
    friendship1 = Friendship(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id)
    friendship2 = Friendship(user_id=friend_request.receiver_id, friend_id=friend_request.sender_id)
    
    db.session.add(friendship1)
    db.session.add(friendship2)
    db.session.commit()

    return friend_request


def reject_friend_request(request_id):
    """Отклонение заявки в друзья"""
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request or friend_request.status != "pending":
        return None  # Запрос не найден или уже обработан

    friend_request.status = "rejected"
    db.session.commit()

    return friend_request


def get_pending_friend_requests(user_id):
    """Получение списка входящих заявок"""
    return FriendRequest.query.filter_by(receiver_id=user_id, status="pending").all()


def remove_friend(user_id, friend_id):
    """Удаляет пользователя из списка друзей"""
    friendship1 = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    friendship2 = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id).first()

    if not friendship1 or not friendship2:
        return None  # Дружбы нет

    db.session.delete(friendship1)
    db.session.delete(friendship2)
    db.session.commit()

    return True


def get_friends(user_id):
    """Возвращает список друзей пользователя"""
    friendships = Friendship.query.filter_by(user_id=user_id).all()
    friend_ids = [friendship.friend_id for friendship in friendships]

    friends = User.query.filter(User.id.in_(friend_ids)).all()
    return friends

#endregion

#region Connections to external API

def get_or_create_connection(service_name: str, profile_url: str, user_id: UUID):
    connection = Connection.query.filter_by(
        service_name=service_name,
        external_user_url=profile_url
    ).first()

    if connection is None:
        connection = Connection(
            service_name=service_name,
            external_user_url=profile_url,
            user_id=user_id
        )
        db.session.add(connection)
        db.session.flush()  # Чтобы получить connection.id

    return connection


def create_game_account_if_absent(user_id: UUID, connection_id: UUID):
    account = GameAccount.query.filter_by(
        user_id=user_id,
        connection_id=connection_id
    ).first()

    if account is None:
        account = GameAccount(
            user_id=user_id,
            connection_id=connection_id
        )
        db.session.add(account)
        db.session.commit()

    return account


def unlink_game_account(user_id, connection_id):
    account = GameAccount.query.filter_by(
        user_id=user_id,
        connection_id=connection_id
    ).first()

    if account:
        db.session.delete(account)

        # Удалим connection, если он больше нигде не используется
        count = GameAccount.query.filter_by(connection_id=connection_id).count()
        if count == 0:
            conn = Connection.query.get(connection_id)
            if conn:
                db.session.delete(conn)

        db.session.commit()


