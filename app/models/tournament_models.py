from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from flask_login import UserMixin
import uuid
from datetime import datetime


class Tournament(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(64), unique=True, nullable=False)
    creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
    group_stage = db.relationship('GroupStage', backref='tournament', uselist=False)
    playoff_stage = db.relationship('PlayOffStage', backref='tournament', uselist=False)
    participants = db.relationship('User', secondary='tournament_participants', backref='tournaments_participated')
    teams = db.relationship('Team', secondary='tournament_teams', backref='tournaments_participated')
    matches = db.relationship('Match', backref='tournament', lazy=True)


class GroupStage(db.Model):
    __tablename__ = 'group_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'))
    groups = db.relationship('Group', backref='group_stage', cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='group_stage', lazy=True)


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    letter = db.Column(db.String(4), nullable=False)
    groupstage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=False)
    teams = db.relationship('Team', secondary='group_teams', backref='groups')
    matches = db.relationship('Match', backref='group', lazy=True)


class PlayOffStage(db.Model):
    __tablename__ = 'playoff_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'), nullable=False)
    structure = db.Column(JSONB)
    matches = db.relationship('Match', backref='group', lazy=True)


class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_type = db.Column(db.String(32), nullable=False)  # solo / team / battle_royal
    group_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=True)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=True)
    playoff_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stages.id'), nullable=True)

    team1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
    team2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)

    user1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    user2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)

    scheduled_time = db.Column(db.DateTime)
    result = db.Column(db.String(128))
    # team
    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])
    # solo
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    # battle_royal
    participants = db.relationship('User', secondary='match_participants', backref='matches')

    

