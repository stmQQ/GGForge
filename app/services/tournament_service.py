#from app.models.user_models import User, FriendRequest, Friendship, SupportTicket
from app.models.tournament_models import Tournament, TournamentRegistration
from app.extensions import db
from datetime import datetime, timedelta


def get_upcoming_tournaments(user_id):
    """Получение списка предстоящих турниров"""
    return Tournament.query.join(TournamentRegistration).filter(
        TournamentRegistration.user_id == user_id,
        Tournament.start_date > datetime.now(datetime.timezone.utc)
    ).all()
