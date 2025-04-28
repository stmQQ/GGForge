# from app.models.user_models import User, FriendRequest, Friendship, SupportTicket
import random
from app.models import *
from app.extensions import db
from datetime import datetime
import math
from sqlalchemy.orm import joinedload

from app.services.group_stage import make_group_stage
from app.services.user_service import save_avatar


def get_upcoming_tournaments(user_id):
    """Получение списка предстоящих турниров, в которых зарегистрирован пользователь"""
    return Tournament.query.filter(
        Tournament.start_time > datetime.now(UTC),
        Tournament.participants.any(User.id == user_id)
    ).all()


def get_tournaments_by_game(game_id, status='all'):
    if status not in ['all', 'scheduled', 'active', 'completed']:
        return None
    if status == 'all':
        return Tournament.query.filter(
            Tournament.game_id == game_id
        ).all()
    else:
        return Tournament.query.filter(
            Tournament.game_id == game_id,
            Tournament.status == status
        ).all()


def register_for_tournament(id, tournament_id):
    """Добавляет пользователя в список участников турнира"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "scheduled":
        return None  # Турнир не найден или уже начался

    if tournament.tournament_type in ['solo', 'battle_royal']:
        if id in tournament.participants:
            return None  # Турнир не найден или пользователь не зарегистрирован
        tournament.participants.append(id)
    elif tournament.tournament_type == 'team':
        team: Team = Team.query.get(id)
        team_members = team.players

        if id in tournament.teams or any(m in tournament.participants for m in team_members):
            return None
        tournament.teams.append(id)
        for m in team_members:
            tournament.participants.append(m)

    db.session.commit()
    return tournament


def unregister_from_tournament(id, tournament_id):
    """Удаляет пользователя или команду из списка участников турнира"""
    tournament: Tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None
    if tournament.tournament_type in ['solo', 'battle_royal']:
        if id not in tournament.participants:
            return None  # Турнир не найден или пользователь не зарегистрирован
        tournament.participants.remove(id)
    elif tournament.tournament_type == 'team':
        if id not in tournament.teams:
            return None
        team: Team = Team.query.get(id)
        team_members = team.players
        for m in team_members:
            tournament.participants.remove(m)
        tournament.teams.remove(id)

    db.session.commit()
    return tournament

# TODO: Исправить сущность


def create_tournament(
    title,
    creator_id,
    game_id,
    max_players,
    type,
    start_time_str,
    prize_pool='0',
    banner_file=None,
    has_group_stage=True,
    elimination_type='single',
    num_groups=2,
    qual_to_winners=2,
    qual_to_losers=2
):
    """Создает новый турнир без привязки к Flask"""

    if not all([title, game_id, max_players, type, start_time_str]):
        raise ValueError('Заполните все обязательные поля')

    try:
        start_time = datetime.strptime(
            start_time_str, "%d.%m.%Y | %H:%M").replace(tzinfo=UTC)
    except ValueError:
        raise ValueError(
            'Неверный формат времени. Используйте DD.MM.YYYY | HH:MM')

    banner_url = None
    if banner_file:
        filename = save_avatar(banner_file, folder='tournament_banners')
        banner_url = f"/static/tournament_banners/{filename}"

    tournament = Tournament(
        title=title,
        start_time=start_time,
        creator_id=creator_id,
        game_id=game_id,
        prize_pool=prize_pool,
        max_players=max_players,
        type=type,
        status="scheduled",
        banner_url=banner_url,
    )

    db.session.add(tournament)
    db.session.flush()  # чтобы получить id турнира до коммита

    if has_group_stage:
        group_stage = make_group_stage(
            tournament_id=tournament.id, num_groups=num_groups, qual_to_winners=qual_to_winners, qual_to_losers=qual_to_losers)
        db.session.add(group_stage)

    db.session.commit()

    return tournament


def update_tournament(tournament_id, new_data):
    """Обновляет информацию о турнире"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament:
        return None  # Турнир не найден

    for key, value in new_data.items():
        setattr(tournament, key, value)  # Обновляем поля

    db.session.commit()
    return tournament


def delete_tournament(tournament_id):
    """Удаляет турнир"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament:
        return None  # Турнир не найден

    db.session.delete(tournament)
    db.session.commit()
    return True


def start_tournament(tournament_id):
    """Переводит турнир в статус 'active' (запущен)"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "scheduled":
        return None  # Турнир не найден или уже активен

    tournament.status = "active"
    db.session.commit()
    return tournament


def end_tournament(tournament_id, winner):
    """Завершает турнир и объявляет победителя"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "active":
        return None  # Турнир не найден или неактивен

    tournament.status = "completed"
    tournament.winner = winner
    create_prizetable(tournament_id)
    db.session.commit()
    return tournament


# region Group stage

def make_group_stage(tournament, num_groups, qual_to_winners, qual_to_losers):

    if not tournament:
        return None

    group_stage: GroupStage = GroupStage(
        tournament=tournament, winners_bracket_qualified=qual_to_winners, losers_bracket_qualified=qual_to_losers)

    db.session.add(group_stage)
    db.session.flush()

    if tournament.type == 'team':
        entities = tournament.teams
    else:
        entities = tournament.participants

    total = len(entities)

    if total == 0:
        return None

    group_size = math.ceil(total / num_groups)

    chunks = [entities[i: i + group_size] for i in range(0, total, group_size)]

    for i, group_entities in enumerate(chunks):
        letter = chr(65 + i)
        group = make_group(groupstage=group_stage, participants=group_entities,
                           max_participants=len(group_entities), letter=letter)
        group_stage.groups.append(group)

    db.session.commit()

    return group_stage


def make_group(groupstage, participants, max_participants, letter):
    group = Group(groupstage=groupstage,
                  max_participants=max_participants, letter=letter)

    db.session.add(group)
    db.session.flush()

    if isinstance(participants[0], User):
        group.participants.extend(participants)
        for p in group.participants:
            row = GroupRow(place=0, group=group, user=p)
            db.session.add(row)
    else:
        group.teams.extend(participants)
        for t in group.teams:
            row = GroupRow(place=0, group=group, team=t)
            db.session.add(row)

    return group


def generate_single_elimination_bracket(tournament):
    if tournament.type == 'solo':
        participants = sorted(tournament.participants,
                              key=lambda u: random.random())
    else:
        participants = sorted(tournament.teams, key=lambda t: random.random())

    total = len(participants)
    bracket_size = 2 ** math.floor(math.log2(total))
    cutoff = total - bracket_size

    if cutoff > 0:
        for _ in range(cutoff):
            if tournament.type == 'solo':
                tournament.participants.remove(participants[-1])
            else:
                tournament.teams.remove(participants[-1])
            participants.pop()

    rounds_count = int(math.log2(bracket_size))
    playoff_stage = tournament.playoff_stage

    matches_by_round = {}

    # Создаем матчи первого раунда
    first_round = []
    for i in range(0, len(participants), 2):
        match = Match(
            tournament_id=tournament.id,
            type=tournament.type,
            format='bo1',  # можно передавать отдельно формат
            status='upcoming',
            participant1_id=participants[i].id,
            participant2_id=participants[i+1].id,
            is_playoff=True
        )
        db.session.add(match)
        db.session.flush()

        playoff_match = PlayoffStageMatch(
            round_number=f"W1",
            match_id=match.id,
            playoff_stage=playoff_stage
        )
        db.session.add(playoff_match)
        first_round.append(playoff_match)
    matches_by_round[1] = first_round

    db.session.flush()

    # Создаем матчи для остальных раундов
    for round_num in range(2, rounds_count + 1):
        previous_round = matches_by_round[round_num - 1]
        current_round = []

        for i in range(0, len(previous_round), 2):
            match = Match(
                tournament_id=tournament.id,
                type=tournament.type,
                format='bo1',
                status='upcoming',
                is_playoff=True
            )
            db.session.add(match)
            db.session.flush()

            playoff_match = PlayoffStageMatch(
                round_number=f"W{round_num}",
                match_id=match.id,
                playoff_stage=playoff_stage,
                depends_on_match_1_id=previous_round[i].id,
                depends_on_match_2_id=previous_round[i+1].id
            )
            db.session.add(playoff_match)

            # Установить победные связи предыдущим матчам
            previous_round[i].winner_to_match_id = playoff_match.id
            previous_round[i+1].winner_to_match_id = playoff_match.id

            current_round.append(playoff_match)

        matches_by_round[round_num] = current_round

    db.session.commit()


def generate_double_elimination_bracket(tournament):
    if tournament.type == 'solo':
        participants = sorted(tournament.participants,
                              key=lambda u: random.random())
    else:
        participants = sorted(tournament.teams, key=lambda t: random.random())

    total = len(participants)
    bracket_size = 2 ** math.floor(math.log2(total))
    cutoff = total - bracket_size

    if cutoff > 0:
        for _ in range(cutoff):
            if tournament.type == 'solo':
                tournament.participants.remove(participants[-1])
            else:
                tournament.teams.remove(participants[-1])
            participants.pop()

    rounds_count = int(math.log2(bracket_size))
    playoff_stage = tournament.playoff_stage

    upper_bracket = {}
    lower_bracket = {}
    match_id_map = {}

    # Создаем первый раунд верхней сетки
    first_round_upper = []
    for i in range(0, len(participants), 2):
        match = Match(
            tournament_id=tournament.id,
            type=tournament.type,
            format='bo1',
            status='upcoming',
            participant1_id=participants[i].id,
            participant2_id=participants[i+1].id,
            is_playoff=True
        )
        db.session.add(match)
        db.session.flush()

        playoff_match = PlayoffStageMatch(
            round_number=f"W1",
            match_id=match.id,
            playoff_stage=playoff_stage
        )
        db.session.add(playoff_match)
        first_round_upper.append(playoff_match)
        match_id_map[playoff_match.id] = playoff_match
    upper_bracket[1] = first_round_upper

    db.session.flush()

    # Строим верхнюю сетку
    for round_num in range(2, rounds_count + 1):
        previous_round = upper_bracket[round_num - 1]
        current_round = []

        for i in range(0, len(previous_round), 2):
            match = Match(
                tournament_id=tournament.id,
                type=tournament.type,
                format='bo1',
                status='upcoming',
                is_playoff=True
            )
            db.session.add(match)
            db.session.flush()

            playoff_match = PlayoffStageMatch(
                round_number=f"W{round_num}",
                match_id=match.id,
                playoff_stage=playoff_stage,
                depends_on_match_1_id=previous_round[i].id,
                depends_on_match_2_id=previous_round[i+1].id
            )
            db.session.add(playoff_match)

            # Победители идут дальше по верхней сетке
            previous_round[i].winner_to_match_id = playoff_match.id
            previous_round[i+1].winner_to_match_id = playoff_match.id

            # Проигравшие пойдут в нижнюю сетку (создадим позже)
            current_round.append(playoff_match)
            match_id_map[playoff_match.id] = playoff_match

        upper_bracket[round_num] = current_round

    db.session.flush()

    # Строим нижнюю сетку
    lower_round_counter = 1
    previous_lower_round = []

    for upper_round_num in range(1, rounds_count):
        losers = upper_bracket[upper_round_num]

        for i, loser in enumerate(losers):
            match = Match(
                tournament_id=tournament.id,
                type=tournament.type,
                format='bo1',
                status='upcoming',
                is_playoff=True
            )
            db.session.add(match)
            db.session.flush()

            playoff_match = PlayoffStageMatch(
                round_number=f"L{lower_round_counter}",
                match_id=match.id,
                playoff_stage=playoff_stage
            )
            db.session.add(playoff_match)

            if previous_lower_round:
                # Проигравший с прошлого раунда нижней сетки
                prev = previous_lower_round.pop(0)
                playoff_match.depends_on_match_1_id = prev.id
                prev.winner_to_match_id = playoff_match.id

            playoff_match.depends_on_match_2_id = loser.id
            loser.loser_to_match_id = playoff_match.id

            previous_lower_round.append(playoff_match)
            match_id_map[playoff_match.id] = playoff_match

            lower_bracket[lower_round_counter] = lower_bracket.get(
                lower_round_counter, []) + [playoff_match]

        lower_round_counter += 1

    db.session.flush()

    # Финалисты
    # Победитель верхней сетки vs Победитель нижней сетки
    final_match = Match(
        tournament_id=tournament.id,
        type=tournament.type,
        format='bo3',  # финал может быть bo3
        status='upcoming',
        is_playoff=True
    )
    db.session.add(final_match)
    db.session.flush()

    final_playoff = PlayoffStageMatch(
        round_number="GF",  # Grand Final
        match_id=final_match.id,
        playoff_stage=playoff_stage
    )
    db.session.add(final_playoff)

    # Связываем победителей верхней и нижней сетки
    upper_finalist = upper_bracket[rounds_count][0]
    lower_finalist = previous_lower_round.pop(0)

    final_playoff.depends_on_match_1_id = upper_finalist.id
    final_playoff.depends_on_match_2_id = lower_finalist.id

    upper_finalist.winner_to_match_id = final_playoff.id
    lower_finalist.winner_to_match_id = final_playoff.id

    db.session.commit()


def report_match_result(match_id, winner_id):
    match = Match.query.get(match_id)
    if not match:
        return

    is_team = match.match_type != 'solo'

    winner = (
        match.team1 if is_team and str(match.team1.id) == str(winner_id) else
        match.team2 if is_team and str(match.team2.id) == str(winner_id) else
        match.user1 if not is_team and str(match.user1.id) == str(winner_id) else
        match.user2 if not is_team else None
    )

    if not winner:
        raise ValueError("Неверный победитель")

    # Определяем проигравшего
    loser = (
        match.team2 if is_team and winner == match.team1 else
        match.team1 if is_team else
        match.user2 if winner == match.user1 else
        match.user1
    )

    match.winner_id = winner.id
    db.session.commit()

    # === Обновление статистики ===
    if match.group_id:
        group = Group.query.get(match.group_id)
        stats = group.stats or {}

        win_id = str(winner.id)
        lose_id = str(loser.id)

        for pid in [win_id, lose_id]:
            if pid not in stats:
                stats[pid] = {
                    'points': 0,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'matches_played': 0,
                    'round_difference': 0
                }

        stats[win_id]['points'] += 3
        stats[win_id]['wins'] += 1
        stats[win_id]['matches_played'] += 1

        stats[lose_id]['losses'] += 1
        stats[lose_id]['matches_played'] += 1

        group.stats = stats
        db.session.commit()

    # === Обновление плей-офф структуры ===
    playoff = PlayoffStage.query.filter_by(
        tournament_id=match.tournament_id).first()
    if playoff:
        structure = playoff.structure
        match_id_str = str(match.id)

        def propagate_winner(rounds):
            for r in rounds:
                for m in r['matches']:
                    if m.get('id') == match_id_str:
                        m['winner'] = winner.name
                        return True
            return False

        updated = False
        if 'winners_bracket' in structure:
            updated = propagate_winner(structure['winners_bracket']) or updated
        if 'losers_bracket' in structure:
            updated = propagate_winner(structure['losers_bracket']) or updated
        if 'rounds' in structure:
            updated = propagate_winner(structure['rounds']) or updated
        if 'final' in structure and structure['final'].get('match', {}).get('id') == match_id_str:
            structure['final']['match']['winner'] = winner.name
            updated = True

        if updated:
            db.session.commit()


def create_match(tournament, match_type, team1=None, team2=None, user1=None, user2=None):
    match = Match(
        id=uuid.uuid4(),
        match_type=match_type,
        tournament=tournament,
        team1=team1,
        team2=team2,
        user1=user1,
        user2=user2,
        result=None
    )
    db.session.add(match)
    return match


def create_prizetable(tournament_id):
    """Создает таблицу результатов после завершения турнира"""
    tournament: Tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None
    table = PrizeTable(tournament_id=tournament_id)
    db.session.add(table)
    db.session.flush()

    if tournament.type == 'team':
        entities = tournament.teams
    else:
        entities = tournament.participants

    data = tournament.playoff_stage.structure
    for e in entities:
        row = create_prizetable_row(table.id, )


def create_prizetable_row(prize_table, place, prize='-', team=None, user=None):
    result_row: PrizeTableRow = PrizeTableRow(
        prize_table=prize_table,
        place=place,
        prize=prize,
        team=team,
        user=user
    )
    db.session.add(result_row)
    db.session.flush()

    return result_row
