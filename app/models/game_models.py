from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(64), nullable=False, unique=True)
    image_path = db.Column(db.String(256), nullable=False, unique=True)
    logo_path = db.Column(db.String(256), nullable=False, unique=True)
    service_name = db.Column(db.String(32), nullable=False)
    tournaments = db.relationship('Tournament', back_populates='game', lazy='selectin')
    achievements = db.relationship('Achievement', back_populates='game', lazy='selectin')


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(256))

    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
    game = db.relationship('Game', back_populates='achievements', lazy='selectin')

    users = db.relationship('User', secondary='user_achievements', back_populates='achievements', lazy='selectin')




