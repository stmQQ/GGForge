import uuid
import pytest
from datetime import datetime, UTC
from app import create_app
from app.extensions import db
from app.models import User, Team, Tournament, Group, GroupStage, GroupRow
from app.services.group_stage import make_group, make_group_stage


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user_data():
    return [
        {"name": f"user{i}", "email": f"user{i}@example.com",
         "password_hash": "hashedpassword", "admin_role": False, "last_online": datetime.now(UTC)}
        for i in range(1, 17)
    ]


@pytest.fixture
def users(app, user_data):
    users = [User(**data) for data in user_data]
    db.session.add_all(users)
    db.session.commit()
    return users


@pytest.fixture
def team_data(users):
    return [
        {"title": f"team{i}", "description": f"Description of team {i}",
         "leader_id": users[i].id}  # Связь с реальными пользователями
        for i in range(8)
    ]


@pytest.fixture
def teams(app, team_data, users):
    teams = []
    for i, data in enumerate(team_data):
        team = Team(**data)
        team.players = users[i*2:i*2+2]  # Каждой команде по 2 игрока
        db.session.add(team)
        teams.append(team)
    db.session.commit()
    return teams


@pytest.fixture
def tournament(app, users):
    tournament = Tournament(
        id=uuid.uuid4(),
        title="Test Tournament",
        type="solo",
        max_players=16,
        status="scheduled",
        game_id=uuid.uuid4(),  # UUID, а не строка
        creator_id=users[0].id
    )
    db.session.add(tournament)
    db.session.commit()
    return tournament


def test_make_group_stage_with_users(app, tournament, users):
    group_stage = make_group_stage(
        tournament.id, participants_per_group=4, num_groups=4, qual_to_winners=2, qual_to_losers=2)

    assert group_stage is not None
    assert len(group_stage.groups) == 4

    for group in group_stage.groups:
        assert len(group.participants) == 4


def test_make_group_stage_with_teams(app, tournament, teams):
    tournament.type = 'team'
    db.session.commit()

    group_stage = make_group_stage(
        tournament.id, participants_per_group=2, num_groups=4, qual_to_winners=2, qual_to_losers=2)

    assert group_stage is not None
    assert len(group_stage.groups) == 4

    for group in group_stage.groups:
        assert len(group.teams) == 2


def test_make_group_with_users(app, tournament, users):
    group = make_group(
        groupstage_id=uuid.uuid4(),  # UUID вместо строки
        participants=users[:4],
        max_participants=4,
        letter="A"
    )
    assert group is not None
    assert group.letter == "A"
    assert len(group.participants) == 4
    assert len(group.rows) == 4


def test_make_group_with_teams(app, tournament, teams):
    group = make_group(
        groupstage_id=uuid.uuid4(),
        participants=teams[:2],
        max_participants=2,
        letter="A"
    )

    assert group is not None
    assert group.letter == "A"
    assert len(group.teams) == 2
    assert len(group.rows) == 2


def test_make_group_stage_no_participants(app, tournament):
    # Предполагаем, что участников в турнире нет
    group_stage = make_group_stage(
        tournament.id, participants_per_group=4, num_groups=4, qual_to_winners=2, qual_to_losers=2)
    assert group_stage is None


def test_group_stage_with_invalid_tournament_id(app):
    invalid_tournament_id = uuid.uuid4()
    group_stage = make_group_stage(
        invalid_tournament_id, participants_per_group=4, num_groups=4, qual_to_winners=2, qual_to_losers=2)
    assert group_stage is None


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
