from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Tournament, User, Game, Team
from app.services.tournament_service import (
    get_tournaments_by_game, get_tournaments_by_participant,
    get_tournaments_by_creator, get_tournament, get_tournament_group_stage,
    get_tournament_playoff_stage, get_tournament_prize_table,
    get_group_stage_matches, get_playoff_stage_matches, get_all_tournament_matches,
    get_match, create_match, update_match_results, update_map_results
)
from app.schemas import (
    TournamentSchema, GroupStageSchema, PlayoffStageSchema, PrizeTableSchema,
    MatchSchema, MapSchema
)

tournament_bp = Blueprint('tournament', __name__,
                          url_prefix='/api/tournaments')


def is_tournament_creator_or_admin(tournament_id: UUID):
    """Check if the current user is the tournament creator or an admin."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    tournament = Tournament.query.get(tournament_id)
    if not user or not tournament:
        return jsonify({'msg': 'Пользователь или турнир не найден'}), 404
    if not user.is_admin and str(tournament.creator_id) != user_id:
        return jsonify({'msg': 'Требуются права администратора или создателя турнира'}), 403
    return None


@tournament_bp.route('/', methods=['POST'])
@jwt_required()
def create_new_tournament():
    """Create a new tournament."""
    data = request.get_json()
    creator_id = get_jwt_identity()
    creator = User.query.get(creator_id)

    if not creator:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    title = data.get('title')
    game_id = data.get('game_id')
    start_time = data.get('start_time')
    format = data.get('format')
    max_participants = data.get('max_participants')
    prize_fund = data.get('prize_fund')
    status = data.get('status')

    if not all([title, game_id, start_time, format]):
        return jsonify({'msg': 'Необходимо указать title, game_id, start_time и format'}), 400

    game = Game.query.get(game_id)
    if not game:
        return jsonify({'msg': 'Игра не найдена'}), 404

    try:
        start_time = datetime.fromisoformat(start_time)
    except (ValueError, TypeError):
        return jsonify({'msg': 'Неверный формат start_time, ожидается ISO формат'}), 400

    tournament = Tournament(
        title=title,
        game_id=game_id,
        creator_id=creator_id,
        start_time=start_time,
        format=format,
        max_participants=max_participants,
        prize_fund=prize_fund,
        status=status
    )

    try:
        db.session.add(tournament)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Турнир с таким названием уже существует'}), 409

    tournament_schema = TournamentSchema(
        only=('id', 'title', 'game_id', 'start_time', 'format', 'status'))
    return {
        'msg': 'Турнир успешно создан',
        'tournament': tournament_schema.dump(tournament)
    }, 201


@tournament_bp.route('/game/<uuid:game_id>', methods=['GET'])
def get_tournaments_by_game(game_id: UUID):
    """Retrieve all tournaments for a specific game."""
    try:
        tournaments = get_tournaments_by_game(game_id)
        tournament_schema = TournamentSchema(
            many=True,
            only=('id', 'title', 'start_time', 'format',
                  'status', 'max_participants', 'prize_fund')
        )
        return tournament_schema.dump(tournaments), 200
    except ValueError:
        return jsonify({'msg': 'Игра не найдена'}), 404


@tournament_bp.route('/participant/me', methods=['GET'])
@jwt_required()
def get_participant_tournaments():
    """Retrieve all tournaments where the authenticated user is a participant."""
    user_id = get_jwt_identity()
    try:
        tournaments = get_tournaments_by_participant(user_id)
        tournament_schema = TournamentSchema(
            many=True,
            only=('id', 'title', 'game.title',
                  'start_time', 'format', 'status')
        )
        return tournament_schema.dump(tournaments), 200
    except ValueError:
        return jsonify({'msg': 'Пользователь не найден'}), 404


@tournament_bp.route('/creator/me', methods=['GET'])
@jwt_required()
def get_creator_tournaments():
    """Retrieve all tournaments created by the authenticated user."""
    user_id = get_jwt_identity()
    try:
        tournaments = get_tournaments_by_creator(user_id)
        tournament_schema = TournamentSchema(
            many=True,
            only=('id', 'title', 'game.title',
                  'start_time', 'format', 'status')
        )
        return tournament_schema.dump(tournaments), 200
    except ValueError:
        return jsonify({'msg': 'Пользователь не найден'}), 404


@tournament_bp.route('/<uuid:tournament_id>', methods=['GET'])
def get_tournament(tournament_id: UUID):
    """Retrieve detailed information about a single tournament."""
    tournament = get_tournament(tournament_id)
    tournament_schema = TournamentSchema(
        only=(
            'id', 'title', 'game.title', 'creator.name', 'start_time', 'format',
            'max_participants', 'prize_fund', 'status', 'participants', 'teams'
        )
    )
    return tournament_schema.dump(tournament), 200


@tournament_bp.route('/<uuid:tournament_id>/group-stage', methods=['GET'])
def get_tournament_group_stage(tournament_id: UUID):
    """Retrieve the group stage of a tournament."""
    group_stage = get_tournament_group_stage(tournament_id)
    if not group_stage:
        return jsonify({'msg': 'Групповой этап не найден'}), 404
    group_stage_schema = GroupStageSchema(
        only=('id', 'groups', 'tournament_id'))
    return group_stage_schema.dump(group_stage), 200


@tournament_bp.route('/<uuid:tournament_id>/playoff-stage', methods=['GET'])
def get_tournament_playoff_stage(tournament_id: UUID):
    """Retrieve the playoff stage of a tournament."""
    playoff_stage = get_tournament_playoff_stage(tournament_id)
    if not playoff_stage:
        return jsonify({'msg': 'Этап плей-офф не найден'}), 404
    playoff_stage_schema = PlayoffStageSchema(
        only=('id', 'playoff_matches', 'tournament_id'))
    return playoff_stage_schema.dump(playoff_stage), 200


@tournament_bp.route('/<uuid:tournament_id>/prize-table', methods=['GET'])
def get_tournament_prize_table(tournament_id: UUID):
    """Retrieve the prize table of a tournament."""
    prize_table = get_tournament_prize_table(tournament_id)
    if not prize_table:
        return jsonify({'msg': 'Призовая таблица не найдена'}), 404
    prize_table_schema = PrizeTableSchema(only=('id', 'rows', 'tournament_id'))
    return prize_table_schema.dump(prize_table), 200


@tournament_bp.route('/<uuid:tournament_id>/matches', methods=['GET'])
def get_all_tournament_matches_route(tournament_id: UUID):
    """Retrieve all matches in a tournament (group and playoff stages)."""
    matches = get_all_tournament_matches(tournament_id)
    match_schema = MatchSchema(
        many=True,
        only=(
            'id', 'tournament_id', 'participant1_id', 'participant2_id', 'winner_id',
            'status', 'type', 'format', 'maps', 'group.letter', 'playoff_match.round_number'
        )
    )
    return match_schema.dump(matches), 200


@tournament_bp.route('/<uuid:tournament_id>/group-stage/matches', methods=['GET'])
def get_group_stage_matches(tournament_id: UUID):
    """Retrieve all matches in the group stage of a tournament."""
    try:
        matches = get_group_stage_matches(tournament_id)
        match_schema = MatchSchema(
            many=True,
            only=(
                'id', 'tournament_id', 'participant1_id', 'participant2_id', 'winner_id',
                'status', 'type', 'format', 'maps', 'group.letter'
            )
        )
        return match_schema.dump(matches), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 404


@tournament_bp.route('/<uuid:tournament_id>/playoff-stage/matches', methods=['GET'])
def get_playoff_stage_matches(tournament_id: UUID):
    """Retrieve all matches in the playoff stage of a tournament."""
    try:
        matches = get_playoff_stage_matches(tournament_id)
        match_schema = MatchSchema(
            many=True,
            only=(
                'id', 'tournament_id', 'participant1_id', 'participant2_id', 'winner_id',
                'status', 'type', 'format', 'maps', 'playoff_match.round_number'
            )
        )
        return match_schema.dump(matches), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 404


@tournament_bp.route('/<uuid:tournament_id>/matches/<uuid:match_id>', methods=['GET'])
def get_match_route(tournament_id: UUID, match_id: UUID):
    """Retrieve detailed results of a specific match."""
    try:
        match = get_match(tournament_id, match_id)
        match_schema = MatchSchema(
            only=(
                'id', 'tournament_id', 'participant1_id', 'participant2_id', 'winner_id',
                'status', 'type', 'format', 'maps', 'group.letter', 'playoff_match.round_number'
            )
        )
        return match_schema.dump(match), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 404


@tournament_bp.route('/<uuid:tournament_id>/matches', methods=['POST'])
@jwt_required()
def create_match_route(tournament_id: UUID):
    """Create a new match in a tournament (creator/admin only)."""
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    data = request.get_json()
    participant1_id = data.get('participant1_id')
    participant2_id = data.get('participant2_id')
    group_id = data.get('group_id')
    playoff_match_id = data.get('playoff_match_id')
    type_ = data.get('type')
    format_ = data.get('format')

    try:
        match = create_match(
            tournament_id=tournament_id,
            participant1_id=participant1_id,
            participant2_id=participant2_id,
            group_id=group_id,
            playoff_match_id=playoff_match_id,
            type=type_,
            format=format_
        )
        match_schema = MatchSchema(
            only=(
                'id', 'tournament_id', 'participant1_id', 'participant2_id',
                'status', 'type', 'format', 'group.letter', 'playoff_match.round_number'
            )
        )
        return {
            'msg': 'Матч успешно создан',
            'match': match_schema.dump(match)
        }, 201
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/matches/<uuid:match_id>', methods=['PATCH'])
@jwt_required()
def update_match_results_route(tournament_id: UUID, match_id: UUID):
    """Update the results of a match (creator/admin only)."""
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    data = request.get_json()
    winner_id = data.get('winner_id')
    status = data.get('status')

    try:
        match = update_match_results(
            tournament_id, match_id, winner_id, status)
        match_schema = MatchSchema(
            only=(
                'id', 'tournament_id', 'participant1_id', 'participant2_id', 'winner_id',
                'status', 'type', 'format', 'maps', 'group.letter', 'playoff_match.round_number'
            )
        )
        return {
            'msg': 'Результаты матча обновлены',
            'match': match_schema.dump(match)
        }, 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/matches/<uuid:match_id>/maps/<uuid:map_id>', methods=['PATCH'])
@jwt_required()
def update_map_results_route(tournament_id: UUID, match_id: UUID, map_id: UUID):
    """Update the results of a specific map in a match (creator/admin only)."""
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    data = request.get_json()
    winner_id = data.get('winner_id')

    try:
        map_ = update_map_results(tournament_id, match_id, map_id, winner_id)
        map_schema = MapSchema(
            only=('id', 'external_id', 'winner_id', 'match_id'))
        return {
            'msg': 'Результаты карты обновлены',
            'map': map_schema.dump(map_)
        }, 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400
