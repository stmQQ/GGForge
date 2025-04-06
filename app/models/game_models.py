from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(64), nullable=False, unique=True)
    tournaments = db.relationship('Tournament', backref='game', lazy=True)
    achievements = db.relationship('Achievement', backref='game', lazy=True)


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(256))
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)




