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
    avatar = db.Column(db.String(128))
    registration_date = db.Column(db.Date, nullable=False, default=datetime.now(UTC).date)
    last_online = db.Column(db.DateTime, nullable=False)
    admin_role = db.Column(db.Boolean, nullable=False)

    friends = db.relationship(
        'User', secondary=mutual_friend_association,
        primaryjoin=id==mutual_friend_association.c.user_id,
        secondaryjoin=id==mutual_friend_association.c.friend_id,
        backref='friends_back'
    )


    game_accounts = db.relationship('GameAccount', back_populates='user', lazy=True)
    connections = db.relationship('Connection', back_populates='user', lazy=True)
    created_tournaments = db.relationship('Tournament', back_populates='creator', lazy=True)
    achievements = db.relationship('Achievement', secondary='user_achievements', back_populates='users')
    participated_tournaments = db.relationship('Tournament', secondary='tournament_participants', back_populates='participants')
    groups = db.relationship('Group', secondary='group_users', back_populates='participants')
    rows = db.relationship('GroupRow', back_populates='user')
    support_tokens = db.relationship('SupportToken', back_populates='user', lazy=True)
    sent_requests = db.relationship('UserRequest', 
                                    back_populates='from_user', 
                                    foreign_keys='UserRequest.from_user_id',
                                     lazy=True)
    received_requests = db.relationship('UserRequest', 
                                        back_populates='to_user', 
                                        foreign_keys='UserRequest.from_user_id',
                                        lazy=True)


class GameAccount(db.Model):
    __tablename__ = 'game_accounts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='game_accounts', uselist=False)

    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
    game = db.relationship('Game', back_populates='game_account', uselist=False)

    connection_id = db.Column(UUID(as_uuid=True), db.ForeignKey('connections.id'), nullable=False)
    connection = db.relationship('Connection', back_populates='game_account', uselist=False)



class Connection(db.Model):
    __tablename__ = 'connections'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_name = db.Column(db.String(64), nullable=False)
    external_user_url = db.Column(db.String(256), nullable=True, unique=True)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='connections', uselist=False)

    game_account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('game_accounts.id'), nullable=False)
    game_account = db.relationship('GameAccount', back_populates='connection', uselist=False)

 


class SupportToken(db.Model):
    __tablename__ = 'support_tokens'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    theme = db.Column(db.String(64), nullable=False)
    text = db.Column(db.String(512))
    status = db.Column(db.String(32), nullable=False, default='Not answered')
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='support_tokens', uselist=False)


class UserRequest(db.Model):
    __tablename__ = 'user_requests'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    type = db.Column(db.String(32), nullable=False)  # 'friend', 'team'
    status = db.Column(db.String(32), nullable=False, default='pending')  # pending, accepted, declined

    # Только для приглашения в команду
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    from_user = db.relationship('User', back_populates='sent_requests', foreign_keys=[from_user_id], uselist=False)
    to_user = db.relationship('User', back_populates='received_requests', foreign_keys=[to_user_id], uselist=False)
    team = db.relationship('Team', back_populates='requests', foreign_keys=[team_id], uselist=False)
