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
    return Tournament.query.filter(
        Tournament.start_time > datetime.now(UTC),
        Tournament.participants.any(User.id == user_id)
    ).all()


def get_tournaments_by_game(game_id, status='all'):
    if status not in ['all', 'scheduled', 'active', 'completed']:
        return None
    query = Tournament.query.filter(Tournament.game_id == game_id)
    if status != 'all':
        query = query.filter(Tournament.status == status)
    return query.all()


def register_for_tournament(id, tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament or tournament.status != "scheduled":
        return None

    if tournament.tournament_type in ['solo', 'battle_royal']:
        if id in tournament.participants:
            return None
        tournament.participants.append(id)
    elif tournament.tournament_type == 'team':
        team = Team.query.get(id)
        if not team or id in tournament.teams:
            return None
        for member in team.players:
            if member in tournament.participants:
                return None
        tournament.teams.append(id)
        tournament.participants.extend(team.players)

    db.session.commit()
    return tournament


def unregister_from_tournament(id, tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None

    if tournament.tournament_type in ['solo', 'battle_royal']:
        if id not in tournament.participants:
            return None
        tournament.participants.remove(id)
    elif tournament.tournament_type == 'team':
        if id not in tournament.teams:
            return None
        team = Team.query.get(id)
        tournament.teams.remove(id)
        for member in team.players:
            if member in tournament.participants:
                tournament.participants.remove(member)

    db.session.commit()
    return tournament
# TODO: Исправить сущность


def create_tournament(
    title, creator_id, game_id, max_players, type, start_time_str,
    prize_pool='0', banner_file=None, has_group_stage=True,
    elimination_type='single', num_groups=2, qual_to_winners=2, qual_to_losers=2
):
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
        banner_url=banner_url
    )

    db.session.add(tournament)
    db.session.flush()

    if has_group_stage:
        group_stage = make_group_stage(
            tournament=tournament,
            num_groups=num_groups,
            qual_to_winners=qual_to_winners,
            qual_to_losers=qual_to_losers
        )
        db.session.add(group_stage)
    else:
        playoff_stage = PlayoffStage(tournament=tournament)
        db.session.add(playoff_stage)
        db.session.flush()
        if elimination_type == 'single':
            generate_single_elimination_bracket(tournament)
        else:
            generate_double_elimination_bracket(tournament)

    db.session.commit()
    return tournament


def update_tournament(tournament_id, new_data):
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None
    for key, value in new_data.items():
        setattr(tournament, key, value)
    db.session.commit()
    return tournament


def delete_tournament(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None
    db.session.delete(tournament)
    db.session.commit()
    return True


def start_tournament(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament or tournament.status != "scheduled":
        return None

    tournament.status = "active"

    return tournament


def complete_tournament(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if not tournament or tournament.status == 'completed':
        return
    tournament.status = 'completed'
    db.session.add(tournament)
    for match in tournament.matches:
        if match.status != 'concluded':
            match.status = 'concluded'
            db.session.add(match)
    create_prizetable(tournament_id)
    db.session.commit()

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


def complete_map(map_id, winner_id):
    from app.models import Map, db

    game_map = db.session.get(Map, map_id)
    if not game_map:
        raise ValueError("Карта не найдена")

    game_map.winner_id = winner_id
    db.session.commit()

    match = game_map.match

    # Проверка, завершены ли все карты
    if all(m.winner_id for m in match.maps):
        complete_match(match.id)


def complete_match(match_id):
    from app.models import Match, db

    match = db.session.get(Match, match_id)
    if not match:
        raise ValueError("Матч не найден")

    participant1_score = sum(
        1 for m in match.maps if m.winner_id == match.participant1_id)
    participant2_score = sum(
        1 for m in match.maps if m.winner_id == match.participant2_id)

    match.participant1_score = participant1_score
    match.participant2_score = participant2_score

    if participant1_score > participant2_score:
        match.winner_id = match.participant1_id
    elif participant2_score > participant1_score:
        match.winner_id = match.participant2_id
    else:
        raise ValueError("Невозможно определить победителя: ничья")

    match.status = 'concluded'
    db.session.commit()

    # Обновляем следующую стадию, если это матч плейоффа
    if match.playoff_match:
        update_next_match_participants(match.playoff_match)


def update_next_match_participants(playoff_match):
    from app.models import db

    winner_id = playoff_match.match.winner_id

    # Обновляем следующий матч для победителя
    if playoff_match.winner_to_match:
        next_match = playoff_match.winner_to_match.match
        if not next_match.participant1_id:
            next_match.participant1_id = winner_id
        elif not next_match.participant2_id:
            next_match.participant2_id = winner_id
        db.session.commit()

    # Обновляем следующий матч для проигравшего
    loser_id = (
        playoff_match.match.participant2_id
        if playoff_match.match.winner_id == playoff_match.match.participant1_id
        else playoff_match.match.participant1_id
    )

    if playoff_match.loser_to_match:
        next_loser_match = playoff_match.loser_to_match.match
        if not next_loser_match.participant1_id:
            next_loser_match.participant1_id = loser_id
        elif not next_loser_match.participant2_id:
            next_loser_match.participant2_id = loser_id
        db.session.commit()


def create_prizetable(tournament_id):
    tournament: Tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None

    table = PrizeTable(tournament=tournament)
    db.session.add(table)
    db.session.flush()

    is_team = tournament.type == 'team'
    prize_pool = int(tournament.prize_pool or 0)

    # Получаем все завершённые матчи турнира
    concluded_matches = [
        m for m in tournament.matches if m.status == 'concluded']

    # Вычисляем рейтинг на основе количества побед
    win_counter = {}

    for match in concluded_matches:
        winner_id = match.winner_id
        if not winner_id:
            continue

        key = winner_id if is_team else match.get_user_id_from_participant(
            winner_id)
        win_counter[key] = win_counter.get(key, 0) + 1

    # Сортируем по количеству побед
    placement = sorted(win_counter.items(),
                       key=lambda item: item[1], reverse=True)
    top_entities = [entity_id for entity_id, _ in placement[:6]]

    prize_distribution = {
        1: 0.45,
        2: 0.25,
        3: 0.10,
        4: 0.10,
        5: 0.05,
        6: 0.05
    }

    for i, entity_id in enumerate(top_entities, start=1):
        prize_amount = round(prize_pool * prize_distribution.get(i, 0))
        if is_team:
            team = next((t for t in tournament.teams if str(
                t.id) == str(entity_id)), None)
            create_prizetable_row(table.id, i, prize=prize_amount, team=team)
        else:
            user = next((u for u in tournament.participants if str(
                u.id) == str(entity_id)), None)
            create_prizetable_row(table.id, i, prize=prize_amount, user=user)

    db.session.commit()
    return table


def create_prizetable_row(prize_table_id, place, prize='-', team=None, user=None):
    row = PrizeTableRow(
        prize_table_id=prize_table_id,
        place=place,
        prize=str(prize),
        team=team,
        user=user
    )
    db.session.add(row)
    db.session.flush()
    return row
