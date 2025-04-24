from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = db.Column(db.String(64), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=func.now())
    prize_pool = db.Column(db.String(8), default='0')
    max_players = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(16), nullable=False) # solo / team / battle_royal
    status = db.Column(db.String(16), nullable=False, default='scheduled') # scheduled, active, completed
    
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
    game = db.relationship('Game', back_populates='tournaments')

    group_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=False, unique=True)
    group_stage = db.relationship('GroupStage', back_populates='tournament', uselist=False, cascade='all, delete-orphan')

    playoff_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stages.id'), nullable=False, unique=True)
    playoff_stage = db.relationship('PlayOffStage', back_populates='tournament', uselist=False, cascade='all, delete-orphan')

    prize_table_id = db.Column(UUID(as_uuid=True), db.ForeignKey('prize_tables.id'), nullable=False, unique=True)
    prize_table = db.relationship('PrizeTable', back_populates='tournament', uselist=False, cascade='all, delete-orphan')

    creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship('User', back_populates='created_tournaments')

    participants = db.relationship('User', secondary='tournament_participants', back_populates='participated_tournaments')
    teams = db.relationship('Team', secondary='tournament_teams', backref='participated_tournaments')
    matches = db.relationship('Match', back_populates='tournament', lazy='selectin')


class GroupStage(db.Model):
    __tablename__ = 'group_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament = db.relationship('Tournament', back_populates='group_stage', uselist=False)

    groups = db.relationship('Group', back_populates='group_stage')

    winners_bracket_quaified = db.Column(db.Integer, nullable=False)
    losers_bracket_qualified = db.Column(db.Integer, nullable=True)


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    letter = db.Column(db.String(4), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)

    groupstage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=False)
    group_stage = db.relationship('GroupStage', back_populates='groups')

    participants = db.relationship('User', secondary='group_users', back_populates='groups', lazy='selectin')
    teams = db.relationship('Team', secondary='group_teams', back_populates='groups', lazy='selectin')
    matches = db.relationship('Match', back_populates='group', lazy='selectin')
    rows = db.relationship('GroupRow', back_populates='group', lazy='selectin')


class GroupRow(db.Model):
    __tablename__ = 'group_rows'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    place = db.Column(db.Integer, nullable=False)
    wins = db.Column(db.Integer, nullable=True, default=0)
    draws = db.Column(db.Integer, nullable=True, default=0)
    loses = db.Column(db.Integer, nullable=True, default=0)

    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=False)
    group = db.relationship('Group', back_populates='rows')

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', back_populates='rows')

    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
    team = db.relationship('Team', back_populates='rows')


class PlayoffStage(db.Model):
    __tablename__ = 'playoff_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament = db.relationship('Tournament', back_populates='playoff_stage', uselist=False)

    playoff_matches = db.relationship('PlayoffStageMatch', back_populates='playoff_stage', lazy='selectin')




class PrizeTable(db.Model):
    __tablename__ = 'prize_tables'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament = db.relationship('Tournament', back_populates='prize_table', uselist=False)

    rows = db.relationship('PrizeTableRow', back_populates='prize_table', lazy='selectin', cascade='all, delete-orphan')
    # Что здесь добавить???



class PrizeTableRow(db.Model):
    __tablename__ = 'prize_table_rows'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    place = db.Column(db.Integer, nullable=True)
    prize = db.Column(db.String(16))

    prize_table_id = db.Column(UUID(as_uuid=True), db.ForeignKey('prize_tables.id'), nullable=False)
    prize_table = db.relationship('PrizeTable', back_populates='rows')


    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', back_populates='prizetable_rows')

    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
    team = db.relationship('Team', back_populates='prizetable_rows')



