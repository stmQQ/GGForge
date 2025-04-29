from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity
)

from app.extensions import db
# TODO: Переместить функцию в другую папку и переименовать в save_file
from app.services.user_service import save_avatar
from app.services.tournament_service import create_tournament
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
    prize_pool = data.get('prize_pool', '0')
    max_players = data.get('max_players')
    tournament_type = data.get('tournament_type')
    start_time_str = data.get('start_time')

    has_group_stage = data.get('group_stage', 'false').lower() == 'true'
    elimination_type = data.get('elimination_type', 'single')
    num_groups = int(data.get('num_groups', 2))
    qual_to_winners = int(data.get('qual_to_winners', 2))
    qual_to_losers = int(data.get('qual_to_losers', 2))

    if not all([title, game_id, max_players, tournament_type, start_time_str]):
        return jsonify({'msg': 'Заполните все обязательные поля'}), 400

    banner_url = None
    if file:
        filename = save_avatar(file, folder='tournament_banners')
        banner_url = f"/static/tournament_banners/{filename}"

    tournament = create_tournament(title=title, creator_id=user_id, game_id=game_id,
                                   max_players=max_players, type=tournament_type,
                                   start_time_str=start_time_str, prize_pool=prize_pool,
                                   banner_file=banner_url, has_group_stage=has_group_stage,
                                   elimination_type=elimination_type, num_groups=num_groups,
                                   qual_to_winners=qual_to_winners, qual_to_losers=qual_to_losers)

    return jsonify({'msg': 'Турнир успешно создан', 'tournament_id': str(tournament.id)}), 201
