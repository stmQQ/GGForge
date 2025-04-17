from app.models import *
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import joinedload
from flask_login import current_user


def create_team(title, desc, logo_path):
    """Создает команду"""
    if not current_user.is_authenticated:
        return False

    team = Team(title=title, description=desc, logo_path=logo_path)
    
    db.session.add(team)
    db.session.flush()  # Чтобы получить ID до коммита

    team.players.append(current_user)
    team.leader = current_user
    db.session.commit()
    
    return team


def update_team(team_id, title=None, desc=None, logo_path=None) -> Team:
    """Обновляет данные команды"""
    team = Team.query.get(team_id)
    if not team:
        return None
    
    if title:
        team.title = title
    if desc:
        team.description = desc
    if logo_path:
        team.logo_path = logo_path

    db.session.commit()

    return team


def invite_user_to_team(from_user_id, to_user_id, team_id):
    """Создает приглашение в команду"""
    # Проверка — только капитан или участник команды
    team = Team.query.get(team_id)
    if not team or from_user_id not in [p.id for p in team.players]:
        raise PermissionError("Недостаточно прав")

    existing = UserRequest.query.filter_by(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        type='team',
        team_id=team_id,
        status='pending'
    ).first()

    if existing:
        raise ValueError("Приглашение уже отправлено")

    request = UserRequest(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        type='team',
        team_id=team_id,
        status='pending'
    )
    db.session.add(request)
    db.session.commit()
    return request


def accept_team_invite(request_id, user_id):
    """Принимает приглашение в команду"""
    request = UserRequest.query.get(request_id)
    if not request or request.to_user_id != user_id or request.type != 'team':
        raise ValueError("Некорректный запрос на вступление")

    team = Team.query.get(request.team_id)
    if not team:
        raise ValueError("Команда не найдена")

    user = User.query.get(user_id)
    if user in team.players:
        raise ValueError("Пользователь уже в команде")

    team.players.append(user)
    request.status = 'accepted'
    db.session.commit()


def decline_team_invite(request_id, user_id):
    """Отклоняет приглашение в команду"""
    request = UserRequest.query.get(request_id)
    if not request or request.to_user_id != user_id or request.type != 'team':
        raise ValueError("Некорректный запрос")

    request.status = 'declined'
    db.session.commit()


def leave_team(team_id, user_id):
    """Выходит из команды"""
    team = Team.query.get(team_id)
    if not team:
        raise ValueError("Команда не найдена")

    user = User.query.get(user_id)
    if user not in team.players:
        raise ValueError("Пользователь не состоит в команде")

    team.players.remove(user)

    # Капитан уходит — ищем нового
    if team.leader_id == user_id:
        if team.players:
            team.leader_id = team.players[0].id  # любой другой участник
        else:
            db.session.delete(team)  # команда опустела

    db.session.commit()


def kick_member(team_id, captain_id, user_to_kick_id):
    """Исключает участника из команды"""
    team = Team.query.get(team_id)
    if not team:
        raise ValueError("Команда не найдена")

    if team.leader_id != captain_id:
        raise PermissionError("Только капитан может исключать участников")

    if team.leader_id == user_to_kick_id:
        raise ValueError("Капитан не может исключить сам себя")

    user_to_kick = User.query.get(user_to_kick_id)
    if not user_to_kick:
        raise ValueError("Пользователь не найден")

    if user_to_kick not in team.players:
        raise ValueError("Пользователь не состоит в команде")

    team.players.remove(user_to_kick)
    db.session.commit()




    
    
    
