#from app.models.user_models import User, FriendRequest, Friendship, SupportTicket
from app.models.tournament_models import Tournament
from app.extensions import db
from datetime import datetime

def get_upcoming_tournaments(user_id):
    """Получение списка предстоящих турниров, в которых зарегистрирован пользователь"""
    return Tournament.query.filter(
        Tournament.start_date > datetime.now(datetime.timezone.utc),
        Tournament.players.contains(user_id)  # Проверяем, есть ли user_id в списке игроков
    ).all()


def register_for_tournament(user_id, tournament_id):
    """Добавляет пользователя в список участников турнира"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "pending":
        return None  # Турнир не найден или уже начался

    if user_id in tournament.players:
        return None  # Пользователь уже зарегистрирован

    tournament.players.append(user_id)  # Добавляем пользователя в список
    db.session.commit()
    
    return tournament


def unregister_from_tournament(user_id, tournament_id):
    """Удаляет пользователя из списка участников турнира"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or user_id not in tournament.players:
        return None  # Турнир не найден или пользователь не зарегистрирован

    tournament.players.remove(user_id)
    db.session.commit()
    
    return tournament

#TODO: Исправить сущность
def create_tournament(name, game, start_date, max_players, creator_id):
    """Создает новый турнир"""
    tournament = Tournament(
        name=name,
        game=game,
        start_date=start_date,
        max_players=max_players,
        creator_id=creator_id,
        status="pending"  # По умолчанию турнир еще не начался
    )
    db.session.add(tournament)
    db.session.commit()
    
    return tournament


def update_tournament(tournament_id, new_data):
    """Обновляет информацию о турнире"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament:
        return None  # Турнир не найден

    for key, value in new_data.items():
        setattr(tournament, key, value)  # Обновляем поля

    db.session.commit()
    return tournament


def delete_tournament(tournament_id):
    """Удаляет турнир"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament:
        return None  # Турнир не найден

    db.session.delete(tournament)
    db.session.commit()
    return True


def start_tournament(tournament_id):
    """Переводит турнир в статус 'active' (запущен)"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "pending":
        return None  # Турнир не найден или уже активен

    tournament.status = "active"
    db.session.commit()
    return tournament


def end_tournament(tournament_id, winner_id):
    """Завершает турнир и объявляет победителя"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "active":
        return None  # Турнир не найден или неактивен

    tournament.status = "completed"
    tournament.winner_id = winner_id
    db.session.commit()
    return tournament



