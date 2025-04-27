from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)

from app.extensions import db
# TODO: Переместить функцию в другую папку и переименовать в save_file
from app.services.user_service import save_avatar
from app.models import Tournament, GroupStage, Group, PlayoffStage, PrizeTable, PrizeTableRow, Match, PlayoffStageMatch

from datetime import datetime, UTC


tournament_bp = Blueprint('tournament', __name__,
                          url_prefix='/api/tournaments')


@tournament_bp.route('/', methods=['POST'])
@jwt_required()
def create_new_tournament():
    user_id = get_jwt_identity()
    data = request.form
    file = request.files.get('banner')

    title = data.get('title')
    game_id = data.get('game_id')
    prize_pool = data.get('prize_pool')
    max_players = data.get('max_players')
    tournament_type = data.get('tournament_type')
    start_time_str = data.get('start_time')
    has_group_stage = data.get('group_stage', 'false').lower() == 'true'
    elimination_type = data.get(
        'elimination_type', 'single')  # 'single' или 'double'

    if not all([title, game_id, max_players, tournament_type, start_time_str]):
        return jsonify({'msg': 'Заполните все обязательные поля'}), 400

    try:
        start_time = datetime.strptime(
            start_time_str, "%d.%m.%Y | %H:%M").replace(tzinfo=UTC)
    except ValueError:
        return jsonify({'msg': 'Неверный формат времени. Используйте DD.MM.YYYY | HH:MM'}), 400

    banner_url = None
    if file:
        filename = save_avatar(file, folder='tournament_banners')
        banner_url = f"/static/tournament_banners/{filename}"

    tournament = Tournament(
        title=title,
        start_time=start_time,
        creator_id=user_id,
        game_id=game_id,
        prize_pool=prize_pool,
        max_players=max_players,
        type=tournament_type,
        status="scheduled",
        banner_url=banner_url,
    )

    db.session.add(tournament)
    db.session.flush()

    if has_group_stage:
        group_stage = make_group_stage()

    return jsonify({'msg': 'Турнир успешно создан', 'tournament_id': str(tournament.id)}), 201
