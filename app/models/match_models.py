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

    participant1_id = db.Column(UUID(as_uuid=True), nullable=False)
    participant2_id = db.Column(UUID(as_uuid=True), nullable=False)
    participant1_score = db.Column(db.Integer, default=0)
    participant2_score = db.Column(db.Integer, default=0)
    winner_id = db.Column(UUID(as_uuid=True), nullable=True)

    scheduled_time = db.Column(db.DateTime)

    is_playoff = db.Column(db.Boolean, default=False, nullable=False)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=True)
    playoff_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playoff_stages.id'), nullable=True)

    # relationships
    group = db.relationship('Group', backref='matches')
    playoff_stage = db.relationship('PlayOffStage', backref='matches')


class PlayoffStageMatch(db.Model):
    __tablename__ = 'playoff_stage_matches'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey('matches.id'), nullable=False, unique=True)
    round_number = db.Column(db.String(8), nullable=False)  # W1, L2 и т.д.

    winner_to_match_id = db.Column(UUID(as_uuid=True), nullable=True)
    loser_to_match_id = db.Column(UUID(as_uuid=True), nullable=True)

    depends_on_match_1_id = db.Column(UUID(as_uuid=True), nullable=True)
    depends_on_match_2_id = db.Column(UUID(as_uuid=True), nullable=True)

    match = db.relationship('Match', backref=db.backref('playoff_meta', uselist=False))


class Map(db.Model):
    __tablename__ = 'maps'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey('matches.id'), nullable=False)
    external_id = db.Column(db.String(128), nullable=True)
    winner_id = db.Column(UUID(as_uuid=True), nullable=False)

    match = db.relationship('Match', backref='maps')
