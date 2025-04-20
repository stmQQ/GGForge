from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, UTC


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String(16), nullable=False)  # solo/team
    format = db.Column(db.String(8), nullable=False)  # bo1/bo3...
    status = db.Column(db.String(16), nullable=False)  # upcoming/ongoing/concluded
    scheduled_time = db.Column(db.DateTime)
    is_playoff = db.Column(db.Boolean, default=False, nullable=False)

    participant1_id = db.Column(UUID(as_uuid=True), nullable=False)
    participant2_id = db.Column(UUID(as_uuid=True), nullable=False)
    participant1_score = db.Column(db.Integer, default=0)
    participant2_score = db.Column(db.Integer, default=0)
    winner_id = db.Column(UUID(as_uuid=True), nullable=True)


    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'), nullable=False)
    tournament = db.relationship('Tournament', back_populates='matches', uselist=False)

    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=True)
    group = db.relationship('Group', back_populates='matches', uselist=False)

    playoff_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stages.id'), nullable=True)
    playoff_stage = db.relationship('PlayOffStage', back_populates='matches', uselist=False)

    playoff_match_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stage_matches.id'), nullable=True, unique=True)
    playoff_match = db.relationship('PlayoffStageMatch', back_populates='match', uselist=False)

    maps = db.relationship('Map', back_populates='match', lazy=True)


class PlayoffStageMatch(db.Model):
    __tablename__ = 'playoff_stage_matches'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_number = db.Column(db.String(8), nullable=False)  # W1, L2 и т.д.

    winner_to_match_id = db.Column(UUID(as_uuid=True), nullable=True)
    loser_to_match_id = db.Column(UUID(as_uuid=True), nullable=True)
    depends_on_match_1_id = db.Column(UUID(as_uuid=True), nullable=True)
    depends_on_match_2_id = db.Column(UUID(as_uuid=True), nullable=True)

    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey('matches.id'), nullable=False, unique=True)
    match = db.relationship('Match', back_populates='playoff_match', uselist=False)


class Map(db.Model):
    __tablename__ = 'maps'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    external_id = db.Column(db.String(128), nullable=True)
    winner_id = db.Column(UUID(as_uuid=True), nullable=False)
    
    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey('matches.id'), nullable=False)
    match = db.relationship('Match', back_populates='maps', uselist=False)

