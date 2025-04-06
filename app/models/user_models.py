from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from flask_login import UserMixin
import uuid
from datetime import datetime, UTC


mutual_friend_association = db.Table(
    'mutual_friend_association',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id')),
    db.Column('friend_id', UUID(as_uuid=True), db.ForeignKey('users.id'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    registration_date = db.Column(db.Date, nullable=False, default=datetime.now(UTC).date)
    last_online = db.Column(db.DateTime, nullable=False)
    admin_role = db.Column(db.Boolean, nullable=False)

    friends = db.relationship(
        'User', secondary=mutual_friend_association,
        primaryjoin=id==mutual_friend_association.c.user_id,
        secondaryjoin=id==mutual_friend_association.c.friend_id,
        backref='friends_back'
    )


    game_accounts = db.relationship('GameAccount', backref='user', lazy=True)
    connections = db.relationship('Connection', backref='user', lazy=True)
    created_tournaments = db.relationship('Tournament', backref='creator', lazy=True)
    achievements = db.relationship('Achievement', secondary='user_achievements', backref='users')
    participated_tournaments = db.relationship('Tournament', secondary='tournament_participants', backref='participants')
    support_tokens = db.relationship('SupportToken', backref='user', lazy=True)


class GameAccount(db.Model):
    __tablename__ = 'game_accounts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    connection_id = db.Column(UUID(as_uuid=True), db.ForeignKey('connections.id'), nullable=False)


class Connection(db.Model):
    __tablename__ = 'connections'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = db.Column(db.String(64), nullable=False)
    external_user_url = db.Column(db.String(256), nullable=True, unique=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)


class SupportToken(db.Model):
    __tablename__ = 'support_tokens'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(64), nullable=False)
    text = db.Column(db.String(512))
    status = db.Column(db.String(32), nullable=False, default='Not answered')
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))


class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(32), nullable=False)