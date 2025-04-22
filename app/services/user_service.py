from app.models.game_models import Game
from app.models.user_models import User, FriendRequest, Friendship, SupportTicket, Connection, GameAccount, UserRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


#region User operations

def create_user(name, email, password, avatar="default", role=False):
    """Создает нового пользователя"""
    user: User = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        avatar=avatar,
        admin_role=role,
        is_banned=False,
        ban_time=None
    )
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user_id, name, email, password, avatar="default"):
    """Обновляет данные пользователя"""
    user = User.query.get(user_id)
    if not user:
        return None  # Пользователь не найден
    
    if name:
        user.name = name
    if email:
        user.email = email
    if password:
        user.password_hash = generate_password_hash(password)
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
        "name": user.name,
        "email": user.email,
        "avatar": user.avatar,
        "admin_role": user.admin_role,
        "is_banned": user.is_banned,
        "ban_time": user.ban_time,
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


def ban_user(user_id, ban_hours=None):
    """Банит пользователя на определенное количество дней (если не указано, бан перманентный)"""
    user = User.query.get(user_id)
    if not user:
        return None  # Пользователь не найден
    
    user.is_banned = True
    user.ban_time = ban_hours if ban_hours else None 

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


def create_support_ticket(user_id, theme, text):
    """Создает запрос в поддержку"""
    if not theme.strip() or not text.strip():
        return None  # Сообщение не может быть пустым

    ticket = SupportTicket(user_id=user_id, theme=theme, text=text, status="open")
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
    sender = User.query.get(sender_id)
    receiver = User.query.get(receiver_id)
    request = UserRequest(from_user=sender, to_user=receiver, type='friend', status="pending")
    db.session.add(request)
    db.session.commit()
    return request


def accept_friend_request(request_id):
    """Принятие заявки в друзья"""
    friend_request = UserRequest.query.get(request_id)
    
    if not friend_request or friend_request.status != "pending":
        return None  # Запрос не найден или уже обработан

    # Обновляем статус запроса
    friend_request.status = "accepted"
    #TODO FIX METHOD
    # Добавляем запись в список друзей (если нужно)
    friendship1 = Friendship(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id)
    friendship2 = Friendship(user_id=friend_request.receiver_id, friend_id=friend_request.sender_id)
    
    db.session.add(friendship1)
    db.session.add(friendship2)
    db.session.commit()

    return friend_request


def reject_friend_request(request_id):
    """Отклонение заявки в друзья"""
    friend_request = UserRequest.query.get(request_id)

    if not friend_request or friend_request.status != "pending":
        return None  # Запрос не найден или уже обработан

    friend_request.status = "rejected"
    db.session.commit()

    return friend_request


def get_pending_friend_requests(user_id):
    """Получение списка входящих заявок"""
    return UserRequest.query.filter_by(to_user_id=user_id, status="pending").all()


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

def get_or_create_connection(service_name: str, profile_url: str, user: User):
    connection = Connection.query.filter_by(
        service_name=service_name,
        external_user_url=profile_url
    ).first()

    if connection is None:
        connection = Connection(
            service_name=service_name,
            external_user_url=profile_url,
            user=user
        )
        db.session.add(connection)
        db.session.flush()  # Чтобы получить connection.id

    return connection


def create_game_account_if_absent(user_id: UUID, connection_id: UUID, game_id: UUID, service_name: str, external_url):
    account = GameAccount.query.filter_by(
        user_id=user_id,
        connection_id=connection_id
    ).first()

    if account is None:
        user = User.query.get(user_id)
        game = Game.query.get(game_id)
        connection = get_or_create_connection(service_name=service_name, profile_url=external_url, user=user)
        account = GameAccount(
            user=user,
            game=game,
            connection=connection
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


