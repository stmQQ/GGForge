from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from flask_login import UserMixin
import uuid
from datetime import datetime, UTC


# class Tournament(db.Model):
#     __tablename__ = 'tournaments'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     title = db.Column(db.String(64), unique=True, nullable=False)
#     creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
#     game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
#     prize_pool = db.Column(db.String(8), default='0')
#     max_players = db.Column(db.Integer, nullable=False)
#     tournament_type = db.Column(db.String(16), nullable=False) # solo / team / battle_royal
#     status = db.Column(db.String(16), nullable=False, default='scheduled') # scheduled, active, completed
#     group_stage = db.relationship('GroupStage', backref='tournament', uselist=False)
#     playoff_stage = db.relationship('PlayOffStage', backref='tournament', uselist=False)
#     result_table = db.relationship('ResultTable', backref='tournament', uselist=False, cascade='all, delete-orphan')
#     participants = db.relationship('User', secondary='tournament_participants', backref='tournaments_participated')
#     teams = db.relationship('Team', secondary='tournament_teams', backref='tournaments_participated')
#     matches = db.relationship('Match', backref='tournament', lazy=True)


# class GroupStage(db.Model):
#     __tablename__ = 'group_stages'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'))
#     winners_bracket_quaified = db.Column(db.Integer, nullable=False)
#     losers_bracket_qualified = db.Column(db.Integer, nullable=True)
#     groups = db.relationship('Group', backref='group_stage', cascade='all, delete-orphan')
#     matches = db.relationship('Match', backref='group_stage', lazy=True)


# class Group(db.Model):
#     __tablename__ = 'groups'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     letter = db.Column(db.String(4), nullable=False)
#     max_participants = db.Column(db.Integer, nullable=False)
#     groupstage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=False)
#     participants = db.relationship('User', secondary='group_users', bacref='groups')
#     teams = db.relationship('Team', secondary='group_teams', backref='groups')
#     matches = db.relationship('Match', backref='group', lazy=True)


# class PlayOffStage(db.Model):
#     __tablename__ = 'playoff_stages'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'), nullable=False)
#     structure = db.Column(JSONB)
#     matches = db.relationship('Match', backref='group', lazy=True)


# class Match(db.Model):
#     __tablename__ = 'matches'
    
#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     match_type = db.Column(db.String(32), nullable=False)  # solo / team / battle_royal
#     group_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=True)
#     group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=True)
#     playoff_stage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stages.id'), nullable=True)

#     team1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
#     team2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)

#     user1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
#     user2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
#     #TODO: Добавить победителя
#     winner_id = db.Column(UUID(as_uuid=True))
#     scheduled_time = db.Column(db.DateTime)
#     result = db.Column(db.String(128))
#     # team
#     team1 = db.relationship('Team', foreign_keys=[team1_id])
#     team2 = db.relationship('Team', foreign_keys=[team2_id])
#     # solo
#     user1 = db.relationship('User', foreign_keys=[user1_id])
#     user2 = db.relationship('User', foreign_keys=[user2_id])
#     # battle_royal
#     participants = db.relationship('User', secondary='match_participants', backref='matches')

    
# class ResultTable(db.Model):
#     __tablename__ = 'result_tables'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     tournament_id = db.Column(
#         UUID(as_uuid=True),
#         db.ForeignKey('tournaments.id'),
#         nullable=False,
#         unique=True  # гарантирует, что 1:1
#     )

#     # Список призовых мест
#     results = db.relationship('ResultRow', backref='result_table', cascade="all, delete-orphan")


# class ResultRow(db.Model):
#     __tablename__ = 'result_rows'

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     result_table_id = db.Column(UUID(as_uuid=True), db.ForeignKey('result_tables.id'), nullable=False)

#     place = db.Column(db.Integer, nullable=False)
#     prize = db.Column(db.String(16), default='0')

#     team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
#     user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)

#     team = db.relationship('Team')
#     user = db.relationship('User')

#     @property
#     def participant(self):
#         return self.team if self.team_id else self.user


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(64), unique=True, nullable=False)
    creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    prize_pool = db.Column(db.String(8), default='0')
    max_players = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(16), nullable=False) # solo / team / battle_royal
    status = db.Column(db.String(16), nullable=False, default='scheduled') # scheduled, active, completed
    group_stage = db.relationship('GroupStage', backref='tournament', uselist=False, cascade='all, delete-orphan')
    playoff_stage = db.relationship('PlayOffStage', backref='tournament', uselist=False, cascade='all, delete-orphan')
    result_table = db.relationship('ResultTable', backref='tournament', uselist=False, cascade='all, delete-orphan')
    participants = db.relationship('User', secondary='tournament_participants', backref='tournaments_participated')
    teams = db.relationship('Team', secondary='tournament_teams', backref='tournaments_participated')
    matches = db.relationship('Match', backref='tournament', lazy=True)


class GroupStage(db.Model):
    __tablename__ = 'group_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'))
    winners_bracket_quaified = db.Column(db.Integer, nullable=False)
    losers_bracket_qualified = db.Column(db.Integer, nullable=True)
    groups = db.relationship('Group', backref='group_stage', cascade='all, delete-orphan')


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    letter = db.Column(db.String(4), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    groupstage_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_stages.id'), nullable=False)
    participants = db.relationship('User', secondary='group_users', bacref='groups')
    teams = db.relationship('Team', secondary='group_teams', backref='groups')
    matches = db.relationship('Match', backref='group', lazy=True)
    rows = db.relationship('GroupRow', backref='group', lazy=True)


class GroupRow(db.Model):
    __tablename__ = 'group_rows'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
    place = db.Column(db.Integer, nullable=False)
    wins = db.Column(db.Integer, nullable=True, default=0)
    draws = db.Column(db.Integer, nullable=True, default=0)
    loses = db.Column(db.Integer, nullable=True, default=0)


class PlayoffStage(db.Model):
    __tablename__ = 'playoff_stages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'))



class PrizeTable(db.Model):
    __tablename__ = 'prize_tables'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'))
    rows = db.relationship('PrizeTableRow', backref='result_table', lazy=True, cascade='all, delete-orphan')
    # Что здесь добавить???



class PrizeTableRow(db.Model):
    __tablename__ = 'prize_table_rows'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prize_table_id = db.Column(UUID(as_uuid=True), db.Foreignkey('prize_tables.id'), nullable=False)
    place = db.Column(db.Integer, nullable=True)
    prize = db.Column(db.String(16))

    user_id = db.Column(UUID(as_uuid=True), db.Foreignkey('users.id'), nullable=True)
    team_id = db.Column(UUID(as_uuid=True), db.Foreignkey('teams.id'), nullable=True)



