from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(32), unique=True, nullable=False)
    players = db.relationship('User', secondary='team_members', backref='teams')
    tournaments = db.relationship('Tournament', secondary='tournament_teams', backref='teams')

    team_members = db.Table(
    'team_members',
    db.Column('team_id', UUID(as_uuid=True), db.ForeignKey('teams.id')),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'))
    )

