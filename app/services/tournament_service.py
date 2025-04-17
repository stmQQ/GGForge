#from app.models.user_models import User, FriendRequest, Friendship, SupportTicket
from app.models import *
from app.extensions import db
from datetime import datetime
import math
from sqlalchemy.orm import joinedload


def get_upcoming_tournaments(user_id):
    """Получение списка предстоящих турниров, в которых зарегистрирован пользователь"""
    return Tournament.query.filter(
        Tournament.start_time > datetime.now(UTC),
        Tournament.participants.contains(user_id)  # Проверяем, есть ли user_id в списке игроков
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

#TODO: Исправить сущность
def create_tournament(title, creator_id, game_id, prize_pool, max_players, tournament_type):
    """Создает новый турнир"""
    tournament = Tournament(
        title=title,
        game_id=game_id,
        creator_id=creator_id,
        prize_pool=prize_pool,
        max_players=max_players,
        tournament_type=tournament_type
        status="scheduled"  # По умолчанию турнир еще не начался
    )
    db.session.add(tournament)
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


def end_tournament(tournament_id, winner_id):
    """Завершает турнир и объявляет победителя"""
    tournament = Tournament.query.get(tournament_id)

    if not tournament or tournament.status != "active":
        return None  # Турнир не найден или неактивен

    tournament.status = "completed"
    tournament.winner_id = winner_id
    create_resulttable(tournament_id)
    db.session.commit()
    return tournament


#region Group stage

def make_groupstage(tournament_id, participants_per_group, num_groups=None):
    """Создание группового этапа и равномерное распределение участников по группам."""
    tournament = Tournament.query.options(
        joinedload(Tournament.participants),
        joinedload(Tournament.teams)
    ).get(tournament_id)

    if not tournament:
        raise ValueError("Турнир не найден")

    # Создание GroupStage
    group_stage = GroupStage(tournament_id=tournament.id)
    db.session.add(group_stage)
    db.session.flush()  # Получаем ID до коммита

    if tournament.tournament_type == 'solo':
        entities = tournament.participants
    else:
        entities = tournament.teams

    total = len(entities)
    if total == 0:
        raise ValueError("Нет участников в турнире")

    # Вычисление количества групп
    if not num_groups:
        num_groups = math.ceil(total / participants_per_group)

    # Равномерное распределение
    group_size = math.ceil(total / num_groups)
    chunks = [
        entities[i:i + group_size]
        for i in range(0, total, group_size)
    ]

    if len(chunks) > 26:
        raise ValueError("Превышен лимит: поддерживается не более 26 групп (A-Z)")

    for i, group_entities in enumerate(chunks):
        letter = chr(65 + i)  # 'A', 'B', 'C', ...
        make_group(
            groupstage_id=group_stage.id,
            participants=group_entities,
            max_participants=len(group_entities),
            letter=letter
        )

    db.session.commit()
    return group_stage
            


def make_group(groupstage_id, participants, max_participants, letter):
    """Создаёт группу и добавляет в неё участников (пользователей или команды)."""
    group = Group(
        groupstage_id=groupstage_id,
        letter=letter,
        max_participants=max_participants
    )
    db.session.add(group)
    db.session.flush()  # Получаем ID до коммита

    if isinstance(participants[0], User):
        group.participants.extend(participants)
    else:
        group.teams.extend(participants)

    return group


def generate_single_elimination_bracket(tournament_id):
    tournament = Tournament.query.options(
        joinedload(Tournament.participants),
        joinedload(Tournament.teams)
    ).get(tournament_id)

    if tournament.tournament_type == 'solo':
        participants = sorted(tournament.participants, key=lambda u: u.registration_date)
    else:
        participants = sorted(tournament.teams, key=lambda t: t.id)  # Замени при необходимости на поле с датой регистрации

    total = len(participants)
    bracket_size = 2 ** math.floor(math.log2(total))
    cutoff = total - bracket_size

    if cutoff > 0:
        for i in range(cutoff):
            tournament.participants.remove(participants[-1]) if tournament.tournament_type == 'solo' else tournament.teams.remove(participants[-1])
            participants.pop()
        db.session.commit()

    seeds = participants
    rounds = []
    current_round = [{'team1': seeds[i], 'team2': seeds[i + 1]} for i in range(0, bracket_size, 2)]
    round_num = 1

    while current_round:
        round_data = {
            'name': f'Round {round_num}',
            'matches': []
        }
        next_round = []
        for match in current_round:
            match_id = uuid.uuid4()
            round_data['matches'].append({
                'id': str(match_id),
                'team1': match['team1'].name,
                'team2': match['team2'].name,
                'winner': None
            })

            db_match = Match(
                id=match_id,
                match_type=tournament.tournament_type,
                tournament=tournament
            )

            if tournament.tournament_type == 'solo':
                db_match.user1 = match['team1']
                db_match.user2 = match['team2']
            else:
                db_match.team1 = match['team1']
                db_match.team2 = match['team2']

            db.session.add(db_match)
            next_round.append({'team1': 'TBD', 'team2': 'TBD'})

        rounds.append(round_data)
        current_round = next_round if len(next_round) > 1 else None
        round_num += 1

    structure = {
        'type': 'single',
        'rounds': rounds
    }

    playoff = PlayOffStage(
        tournament=tournament,
        structure=structure
    )
    db.session.add(playoff)
    db.session.commit()
    return structure


def generate_double_elimination_bracket(tournament_id):
    tournament = Tournament.query.options(
        joinedload(Tournament.participants),
        joinedload(Tournament.teams)
    ).get(tournament_id)

    if tournament.tournament_type == 'solo':
        participants = sorted(tournament.participants, key=lambda u: u.registration_date)
    else:
        participants = sorted(tournament.teams, key=lambda t: t.id)

    total = len(participants)
    bracket_size = 2 ** math.floor(math.log2(total))
    cutoff = total - bracket_size

    if cutoff > 0:
        for i in range(cutoff):
            tournament.participants.remove(participants[-1]) if tournament.tournament_type == 'solo' else tournament.teams.remove(participants[-1])
            participants.pop()
        db.session.commit()

    seeds = participants
    rounds = math.log2(bracket_size)

    structure = {
        'type': 'double',
        'winners_bracket': [],
        'losers_bracket': [],
        'final': {
            'match': {
                'id': str(uuid.uuid4()),
                'team1': 'TBD',
                'team2': 'TBD',
                'winner': None
            }
        }
    }

    # Winners Bracket
    current_round = [{'team1': seeds[i], 'team2': seeds[i + 1]} for i in range(0, bracket_size, 2)]
    for i in range(int(rounds)):
        round_data = {
            'name': f'Winners Round {i + 1}',
            'matches': []
        }
        next_round = []
        for match in current_round:
            match_id = uuid.uuid4()
            round_data['matches'].append({
                'id': str(match_id),
                'team1': match['team1'].name,
                'team2': match['team2'].name,
                'winner': None
            })

            db_match = Match(
                id=match_id,
                match_type=tournament.tournament_type,
                tournament=tournament
            )

            if tournament.tournament_type == 'solo':
                db_match.user1 = match['team1']
                db_match.user2 = match['team2']
            else:
                db_match.team1 = match['team1']
                db_match.team2 = match['team2']

            db.session.add(db_match)
            next_round.append({'team1': 'TBD', 'team2': 'TBD'})

        structure['winners_bracket'].append(round_data)
        current_round = next_round

    # Losers Bracket (placeholder)
    for i in range(int(rounds)):
        structure['losers_bracket'].append({
            'name': f'Losers Round {i + 1}',
            'matches': [{
                'id': str(uuid.uuid4()),
                'team1': 'TBD',
                'team2': 'TBD',
                'winner': None
            } for _ in range(2**(i))]
        })

    # Гранд-финал матч
    final_match = Match(
        id=uuid.UUID(structure['final']['match']['id']),
        match_type=tournament.tournament_type,
        tournament=tournament
    )
    db.session.add(final_match)

    playoff = PlayOffStage(
        tournament=tournament,
        structure=structure
    )
    db.session.add(playoff)
    db.session.commit()

    return structure


def report_match_result(match_id, winner_id):
    match = Match.query.get(match_id)
    if not match:
        raise ValueError("Матч не найден")

    is_team = match.match_type != 'solo'
    winner = match.team1 if is_team and str(match.team1.id) == str(winner_id) else \
             match.team2 if is_team else \
             match.user1 if str(match.user1.id) == str(winner_id) else match.user2

    if not winner:
        raise ValueError("Неверный победитель")

    match.result = winner.name
    db.session.commit()

    # Найдём турнир и плей-офф
    playoff = PlayOffStage.query.filter_by(tournament_id=match.tournament_id).first()
    if not playoff:
        return

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


def create_resulttable(tournament_id):
    """Создает таблицу результатов после завершения турнира"""
    tournament: Tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return None
    table = ResultTable(tournament_id=tournament_id)
    db.session.add(table)
    db.session.flush()

    if tournament.tournament_type == 'team':
        entities = tournament.teams
    else:
        entities = tournament.participants

    data = tournament.playoff_stage.structure
    for e in entities:
        row = create_resultrow(table.id, )


def find_participant_in_structure(structure, p):
    

def create_resultrow(result_table_id, place, prize='-', team_id=None, user_id=None):
    result_row = ResultRow(
        result_table_id=result_table_id, 
        place=place, 
        prize=prize, 
        team_id=team_id, 
        user_id=user_id
        )
    db.session.add(result_row)
    db.session.flush()

    return result_row

    
