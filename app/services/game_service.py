from app.models.game_models import Game, Achievement
from app.models.user_models import User
from app.extensions import db


def add_game(title, image_path, logo_path, service_name):
    game = Game(title=title, image_path=image_path, logo_path=logo_path, service_name=service_name)
    try:
        db.session.add(game)
        db.session.commit()
    except:
        raise Exception("Error while updating database")
    
    return game
    

def delete_game(id):
    game = Game.query.get(id)
    if not game:
        return None
    db.session.remove(game)
    db.session.commit()
    return True


def create_achievement(title, description, game_id):
    game = Game.query.get(game_id)
    achievement = Achievement(title=title, description=description, game=game)
    try: 
        db.session.add(achievement)
        db.session.commit()
    except:
        raise Exception("Error while updating database")
    
    return achievement


def grant_achievement(achievement_id, user_id):
    achievement = Achievement.query.get(achievement_id)
    user = User.query.get(user_id)

    if not user or not achievement:
        return None
    
    user.achievements.append(achievement)
    db.session.commit()

    return True


def get_user_achievements(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    return user.achievements



    

