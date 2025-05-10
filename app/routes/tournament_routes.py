from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Tournament, User, Game
from app.models.team_models import Team
from app.services.tournament_service import (
    complete_map, complete_match, complete_tournament, get_tournaments_by_game, get_tournaments_by_participant,
    get_tournaments_by_creator, get_tournament, get_tournament_group_stage,
    get_tournament_playoff_stage, get_tournament_prize_table,
    get_group_stage_matches, get_playoff_stage_matches, get_all_tournament_matches,
    get_match, create_match, register_for_tournament, reset_tournament, start_match, start_tournament, unregister_for_tournament, update_match_results, create_tournament
)
from app.schemas import (
    TournamentSchema, GroupStageSchema, PlayoffStageSchema, PrizeTableSchema,
    MatchSchema, MapSchema
)

import traceback

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
    """Create a new tournament with automatic stage generation."""
    creator_id = get_jwt_identity()
    try:
        creator_id_uuid = UUID(creator_id) if isinstance(
            creator_id, str) else creator_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат creator_id'}), 400

    creator = User.query.get(creator_id_uuid)
    if not creator:
        return jsonify({'msg': 'Пользователь не найден'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Отсутствуют данные'}), 400

    required_fields = ['title', 'game_id', 'start_time',
                       'type', 'format_', 'final_format_']
    missing_fields = [
        field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return jsonify({'msg': f'Необходимо указать: {", ".join(missing_fields)}'}), 400

    try:
        game_id_uuid = UUID(data['game_id']) if isinstance(
            data['game_id'], str) else data['game_id']
    except ValueError:
        return jsonify({'msg': 'Некорректный формат game_id'}), 400

    game = Game.query.get(game_id_uuid)
    if not game:
        return jsonify({'msg': 'Игра не найдена'}), 404

    if data['type'] not in ['solo', 'team']:
        return jsonify({'msg': 'Тип турнира должен быть "solo" или "team"'}), 400

    try:
        start_time = datetime.fromisoformat(
            data['start_time'].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return jsonify({'msg': 'Неверный формат start_time (ожидается ISO, например: 2024-05-20T15:00:00Z)'}), 400

    status = data.get('status', 'open')
    if status not in ['open', 'active', 'completed', 'canceled']:
        return jsonify({'msg': 'Недопустимый статус турнира'}), 400

    has_group_stage = data.get('has_group_stage', False)
    if has_group_stage:
        required_group_fields = [
            'num_groups', 'max_participants_per_group', 'playoff_participants_count_per_group']
        missing_group_fields = [
            field for field in required_group_fields if field not in data or data[field] is None]
        if missing_group_fields:
            return jsonify({'msg': f'Для группового этапа укажите: {", ".join(missing_group_fields)}'}), 400

    try:
        tournament = create_tournament(
            title=data['title'],
            game_id=game_id_uuid,
            creator_id=creator_id_uuid,
            start_time=start_time,
            type_=data['type'],
            max_participants=data.get('max_participants', 32),
            prize_fund=data.get('prize_fund'),
            status=status,
            has_group_stage=has_group_stage,
            has_playoff=data.get('has_playoff', True),
            num_groups=data.get('num_groups'),
            max_participants_per_group=data.get('max_participants_per_group'),
            playoff_participants_count_per_group=data.get(
                'playoff_participants_count_per_group'),
            format_=data.get('format_'),
            final_format_=data.get('final_format_')
        )
        db.session.commit()
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Турнир с таким названием уже существует'}), 409

    tournament_schema = TournamentSchema(
        only=('id', 'title', 'game_id', 'start_time', 'type', 'status')
    )
    return jsonify({
        'msg': 'Турнир успешно создан',
        'tournament': tournament_schema.dump(tournament)
    }), 201


@tournament_bp.route('/game/<uuid:game_id>', methods=['GET'])
def get_tournaments_by_game_route(game_id: UUID):
    """Retrieve all tournaments for a specific game."""
    try:
        tournaments = get_tournaments_by_game(game_id)
        tournament_schema = TournamentSchema(
            many=True,
            only=('id', 'title', 'start_time',
                  'status', 'creator_id', 'max_players', 'prize_fund', 'participants', 'teams', 'group_stage.id')
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
                  'start_time', 'status')
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
                  'start_time', 'status')
        )
        return tournament_schema.dump(tournaments), 200
    except ValueError:
        return jsonify({'msg': 'Пользователь не найден'}), 404


@tournament_bp.route('/<uuid:tournament_id>', methods=['GET'])
def get_tournament_route(tournament_id: UUID):
    """Retrieve detailed information about a single tournament."""
    try:
        tournament = get_tournament(tournament_id)
        tournament_schema = TournamentSchema(
            only=(
                'id', 'title', 'game.title', 'creator.name', 'start_time',
                'max_players', 'prize_fund', 'status', 'participants', 'teams', 'group_stage'
            )
        )
        return tournament_schema.dump(tournament), 200
    except ValueError:
        return jsonify({'msg': 'Турнир не найден'}), 404


@tournament_bp.route('/<uuid:tournament_id>/group-stage', methods=['GET'])
def get_tournament_group_stage_route(tournament_id: UUID):
    """Retrieve the group stage of a tournament."""
    group_stage = get_tournament_group_stage(tournament_id)
    if not group_stage:
        return jsonify({'msg': 'Групповой этап не найден'}), 404
    group_stage_schema = GroupStageSchema(
        only=('id', 'groups', 'tournament_id'))
    return group_stage_schema.dump(group_stage), 200


@tournament_bp.route('/<uuid:tournament_id>/playoff-stage', methods=['GET'])
def get_tournament_playoff_stage_route(tournament_id: UUID):
    """Retrieve the playoff stage of a tournament."""
    playoff_stage = get_tournament_playoff_stage(tournament_id)
    if not playoff_stage:
        return jsonify({'msg': 'Этап плей-офф не найден'}), 404
    playoff_stage_schema = PlayoffStageSchema(
        only=('id', 'playoff_matches', 'tournament_id'))
    return playoff_stage_schema.dump(playoff_stage), 200


@tournament_bp.route('/<uuid:tournament_id>/prize-table', methods=['GET'])
def get_tournament_prize_table_route(tournament_id: UUID):
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
        db.session.commit()
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


@tournament_bp.route('/<uuid:tournament_id>/start', methods=['POST'])
@jwt_required()
def start_tournament_route(tournament_id: UUID):
    """Manually start a tournament (creator/admin only)."""
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    try:
        tournament = start_tournament(tournament_id)
        db.session.commit()
        tournament_schema = TournamentSchema(
            only=('id', 'title', 'start_time', 'status')
        )
        return jsonify({
            'msg': 'Турнир успешно начат',
            'tournament': tournament_schema.dump(tournament)
        }), 200
    except ValueError as e:
        trace = traceback.format_exc()
        return jsonify({'msg': str(e), 'traceback': trace}), 400


@tournament_bp.route('/<uuid:tournament_id>/complete', methods=['POST'])
@jwt_required()
def complete_tournament_route(tournament_id: UUID):
    """Manually complete a tournament (creator/admin only)."""
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    try:
        tournament = complete_tournament(tournament_id)
        db.session.commit()
        tournament_schema = TournamentSchema(
            only=('id', 'title', 'status', 'prize_table')
        )
        return jsonify({
            'msg': 'Турнир успешно завершён',
            'tournament': tournament_schema.dump(tournament)
        }), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/register', methods=['POST'])
@jwt_required()
def register_for_tournament_route(tournament_id: UUID):
    """Register a user or team for a tournament."""
    user_id = get_jwt_identity()
    try:
        user_id_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат user_id'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Отсутствуют данные'}), 400

    is_team = data.get('is_team', False)
    participant_id = data.get('participant_id', user_id)

    try:
        participant_id_uuid = UUID(participant_id) if isinstance(
            participant_id, str) else participant_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат participant_id'}), 400

    # Ensure the user is registering themselves or a team they own
    if is_team:
        team = Team.query.get(participant_id_uuid)
        if not team:
            return jsonify({'msg': 'Команда не найдена'}), 404
        # Optionally, check if the user is a member/owner of the team
        # Example: if user_id_uuid not in [member.id for member in team.members]:
        #     return jsonify({'msg': 'Вы не являетесь членом этой команды'}), 403
    else:
        if participant_id_uuid != user_id_uuid:
            return jsonify({'msg': 'Вы можете регистрировать только себя как пользователя'}), 403

    try:
        tournament = register_for_tournament(
            tournament_id, participant_id_uuid, is_team)
        db.session.commit()
        tournament_schema = TournamentSchema(
            only=('id', 'title', 'status', 'participants', 'teams')
        )
        return jsonify({
            'msg': 'Успешно зарегистрирован на турнир',
            'tournament': tournament_schema.dump(tournament)
        }), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/unregister', methods=['POST'])
@jwt_required()
def unregister_for_tournament_route(tournament_id: UUID):
    """Unregister a user or team from a tournament."""
    user_id = get_jwt_identity()
    try:
        user_id_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат user_id'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Отсутствуют данные'}), 400

    is_team = data.get('is_team', False)
    participant_id = data.get('participant_id', user_id)

    try:
        participant_id_uuid = UUID(participant_id) if isinstance(
            participant_id, str) else participant_id
    except ValueError:
        return jsonify({'msg': 'Некорректный формат participant_id'}), 400

    # Ensure the user is unregistering themselves or a team they own
    if is_team:
        team = Team.query.get(participant_id_uuid)
        if not team:
            return jsonify({'msg': 'Команда не найдена'}), 404
        if user_id_uuid not in [member.id for member in team.members]:
            return jsonify({'msg': 'Вы не являетесь членом этой команды'}), 403
    else:
        if participant_id_uuid != user_id_uuid:
            return jsonify({'msg': 'Вы можете отменять регистрацию только для себя как пользователя'}), 403

    try:
        tournament = unregister_for_tournament(
            tournament_id, participant_id_uuid, is_team)
        db.session.commit()
        tournament_schema = TournamentSchema(
            only=('id', 'title', 'status', 'participants', 'teams')
        )
        return jsonify({
            'msg': 'Регистрация на турнир успешно отменена',
            'tournament': tournament_schema.dump(tournament)
        }), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/reset', methods=['POST'])
@jwt_required()
def reset_tournament_route(tournament_id: UUID):
    """
    Reset a tournament to 'open' status, deleting all stages, matches, and prize table.
    Only accessible to the tournament creator or admin.
    """
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    try:
        tournament = reset_tournament(tournament_id)
        tournament_schema = TournamentSchema(
            only=('id', 'title', 'status', 'participants', 'teams')
        )
        return jsonify({
            'msg': 'Турнир успешно сброшен',
            'tournament': tournament_schema.dump(tournament)
        }), 200
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400


@tournament_bp.route('/<uuid:tournament_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id: UUID):
    """
    Delete a tournament and all its related data (stages, matches, prize table, participants, teams).
    Only accessible to the tournament creator or admin.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        JSON response with a success message or error.
    """
    # Check if user is creator or admin
    auth_check = is_tournament_creator_or_admin(tournament_id)
    if auth_check:
        return auth_check

    try:
        # Get tournament
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            return jsonify({'msg': 'Tournament not found'}), 404

        # Delete participant and team associations
        # db.session.execute(tournament.participants.delete().where(
        #     tournament.participants.c.tournament_id == tournament_id))
        # db.session.execute(tournament.teams.delete().where(
        #     tournament.teams.c.tournament_id == tournament_id))

        # Delete tournament (cascades to GroupStage, PlayoffStage, PrizeTable, Matches, etc.)
        db.session.delete(tournament)

        # Remove scheduled task
        try:
            from app.ascheduler_tasks import scheduler
            from apscheduler.jobstores.base import JobLookupError
            scheduler.remove_job(f"tournament_start_{tournament_id}")
        except JobLookupError:
            pass

        db.session.commit()

        return jsonify({'msg': 'Турнир успешно удалён'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f"Failed to delete tournament: {str(e)}"}), 400


@tournament_bp.route('/<tournament_id>/matches/<match_id>/maps/<map_id>/complete', methods=['POST'])
@jwt_required()
def complete_map_route(tournament_id, match_id, map_id):
    try:
        tournament_id = UUID(tournament_id)
        match_id = UUID(match_id)
        map_id = UUID(map_id)
        data = request.get_json()
        if not data or "winner_id" not in data:
            return jsonify({"msg": "winner_id is required"}), 400
        winner_id = UUID(data["winner_id"])
        updated_map = complete_map(tournament_id, match_id, map_id, winner_id)
        updated_match = get_match(tournament_id, match_id)
        if updated_match.status == "completed":
            return jsonify({
                "msg": "Map and match completed",
                "map": {
                    "id": str(updated_map.id),
                    "match_id": str(updated_map.match_id),
                    "winner_id": str(updated_map.winner_id)
                },
                "match": {
                    "id": str(updated_match.id),
                    "status": updated_match.status,
                    "winner_id": str(updated_match.winner_id) if updated_match.winner_id else None,
                    "score1": updated_match.participant1_score,
                    "score2": updated_match.participant2_score
                }
            }), 200
        return jsonify({
            "msg": "Map updated",
            "map": {
                "id": str(updated_map.id),
                "match_id": str(updated_map.match_id),
                "winner_id": str(updated_map.winner_id)
            },
            "match": {
                "id": str(updated_match.id),
                "status": updated_match.status,
                "score1": updated_match.participant1_score,
                "score2": updated_match.participant2_score
            }
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 422
    except IntegrityError as e:
        return jsonify({"msg": "Database error"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


@tournament_bp.route('/<tournament_id>/matches/<match_id>/complete', methods=['POST'])
@jwt_required()
def complete_match_route(tournament_id, match_id):
    """
    Manually complete a match by setting its winner and status to 'completed' or 'tech_win'.

    Args:
        tournament_id (str): UUID of the tournament.
        match_id (str): UUID of the match.

    Request Body:
        {
            "winner_id": "<UUID of the winner (User or Team)>"
        }

    Returns:
        JSON: Updated match data serialized with MatchSchema.

    Raises:
        400: Invalid UUID format or missing winner_id.
        403: User is not authorized to complete the match.
        422: Match cannot be completed (e.g., already completed or invalid winner).
        500: Database or server error.
    """
    try:
        tournament_id = UUID(tournament_id)
        match_id = UUID(match_id)
        current_user_id = get_jwt_identity()
        current_user_id_uuid = UUID(current_user_id) if isinstance(
            current_user_id, str) else current_user_id
        current_user = User.query.get(current_user_id_uuid)
        if not current_user:
            return jsonify({"msg": "User not found"}), 403
        tournament = get_tournament(tournament_id)
        match = get_match(tournament_id, match_id)
        if tournament.creator_id != current_user_id_uuid and not current_user.is_admin:
            return jsonify({"msg": "Unauthorized to complete match"}), 403
        if match.status == "completed" or match.status == "tech_win":
            return jsonify({"msg": "Match is already completed or has tech_win status"}), 422
        data = request.get_json()
        if not data or "winner_id" not in data:
            return jsonify({"msg": "winner_id is required"}), 400
        winner_id = UUID(data["winner_id"])
        updated_match = complete_match(tournament_id, match_id, winner_id)
        match_schema = MatchSchema()
        match_data = match_schema.dump(updated_match)
        return jsonify({
            "msg": "Match completed",
            "match": match_data
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 422
    except IntegrityError as e:
        return jsonify({"msg": "Database error"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


@tournament_bp.route('/<tournament_id>/matches/<match_id>/start', methods=['POST'])
@jwt_required()
def start_match_route(tournament_id, match_id):
    """
    Start a match by setting its status to 'ongoing' and creating maps based on the match format.

    Args:
        tournament_id (str): UUID of the tournament.
        match_id (str): UUID of the match.

    Returns:
        JSON: Updated match data with status and created maps, serialized using MatchSchema.

    Raises:
        400: Invalid UUID format.
        403: User is not authorized to start the match.
        422: Match cannot be started (e.g., wrong status or missing participants).
        500: Database or server error.
    """
    try:
        # Validate UUIDs
        tournament_id = UUID(tournament_id)
        match_id = UUID(match_id)

        # Get current user
        current_user_id = get_jwt_identity()
        current_user_id_uuid = UUID(current_user_id) if isinstance(
            current_user_id, str) else current_user_id
        current_user = User.query.get(current_user_id_uuid)
        if not current_user:
            return jsonify({"msg": "User not found"}), 403

        # Check if tournament and match exist
        tournament = get_tournament(tournament_id)
        match = get_match(tournament_id, match_id)

        # Authorization check (only tournament creator or admin)
        if tournament.creator_id != current_user_id_uuid and not current_user.is_admin:
            return jsonify({"msg": "Unauthorized to start match"}), 403

        # Start the match
        updated_match = start_match(tournament_id, match_id)

        # Serialize match using MatchSchema
        match_schema = MatchSchema()
        match_data = match_schema.dump(updated_match)

        return jsonify({
            "msg": "Match started",
            "match": match_data
        }), 200

    except ValueError as e:
        return jsonify({"msg": str(e)}), 422
    except IntegrityError as e:
        return jsonify({"msg": "Database error"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
