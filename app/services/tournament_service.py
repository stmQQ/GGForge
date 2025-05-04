from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models import Tournament, User, Game, GroupStage, PlayoffStage, PrizeTable, Match, Map, Group, PlayoffStageMatch, Team, PrizeTableRow, GroupRow
from datetime import datetime, UTC
import math
import random
import uuid


def get_tournaments_by_game(game_id: UUID):
    """
    Retrieve all tournaments for a specific game.

    Args:
        game_id: The UUID of the game.

    Returns:
        list: List of Tournament objects.

    Raises:
        ValueError: If the game is not found.
    """
    game = Game.query.get(game_id)
    if not game:
        raise ValueError("Game not found")
    return Tournament.query.filter_by(game_id=game_id).all()


def get_tournaments_by_participant(user_id: UUID):
    """
    Retrieve all tournaments where the user is a participant.

    Args:
        user_id: The UUID of the user.

    Returns:
        list: List of Tournament objects.

    Raises:
        ValueError: If the user is not found.
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    return user.participated_tournaments


def get_tournaments_by_creator(user_id: UUID):
    """
    Retrieve all tournaments created by the user.

    Args:
        user_id: The UUID of the user.

    Returns:
        list: List of Tournament objects.

    Raises:
        ValueError: If the user is not found.
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    return user.created_tournaments


def get_tournament(tournament_id: UUID):
    """
    Retrieve a specific tournament by ID.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        Tournament: The tournament object.

    Raises:
        ValueError: If the tournament is not found.
    """
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        raise ValueError("Tournament not found")
    return tournament


def get_tournament_group_stage(tournament_id: UUID):
    """
    Retrieve the group stage of a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        GroupStage: The group stage object, or None if not found.

    Raises:
        ValueError: If the tournament is not found.
    """
    tournament = get_tournament(tournament_id)
    return tournament.group_stage


def get_tournament_playoff_stage(tournament_id: UUID):
    """
    Retrieve the playoff stage of a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        PlayoffStage: The playoff stage object, or None if not found.

    Raises:
        ValueError: If the tournament is not found.
    """
    tournament = get_tournament(tournament_id)
    return tournament.playoff_stage


def get_tournament_prize_table(tournament_id: UUID):
    """
    Retrieve the prize table of a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        PrizeTable: The prize table object, or None if not found.

    Raises:
        ValueError: If the tournament is not found.
    """
    tournament = get_tournament(tournament_id)
    return tournament.prize_table


def get_group_stage_matches(tournament_id: UUID):
    """
    Retrieve all matches in the group stage of a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        list: List of Match objects from the group stage.

    Raises:
        ValueError: If tournament or group stage is not found.
    """
    tournament = get_tournament(tournament_id)
    group_stage = tournament.group_stage
    if not group_stage:
        raise ValueError("Group stage not found")
    # Оптимизация: предварительная загрузка групп и матчей
    group_stage = GroupStage.query.options(
        joinedload(GroupStage.groups).joinedload(Group.matches)
    ).get(group_stage.id)
    matches = []
    for group in group_stage.groups:
        matches.extend(group.matches)
    return matches


def get_playoff_stage_matches(tournament_id: UUID):
    """
    Retrieve all matches in the playoff stage of a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        list: List of Match objects from the playoff stage.

    Raises:
        ValueError: If tournament or playoff stage is not found.
    """
    tournament = get_tournament(tournament_id)
    playoff_stage = tournament.playoff_stage
    if not playoff_stage:
        raise ValueError("Playoff stage not found")
    # Оптимизация: предварительная загрузка матчей
    playoff_stage = PlayoffStage.query.options(
        joinedload(PlayoffStage.playoff_matches).joinedload(
            PlayoffStageMatch.match)
    ).get(playoff_stage.id)
    matches = [pm.match for pm in playoff_stage.playoff_matches if pm.match]
    return matches


def get_all_tournament_matches(tournament_id: UUID):
    """
    Retrieve all matches in a tournament (group and playoff stages).

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        list: List of Match objects.

    Raises:
        ValueError: If the tournament is not found.
    """
    tournament = get_tournament(tournament_id)
    # Оптимизация: предварительная загрузка матчей
    tournament = Tournament.query.options(
        joinedload(Tournament.matches)).get(tournament_id)
    return tournament.matches


def get_match(tournament_id: UUID, match_id: UUID):
    """
    Retrieve a specific match by ID, ensuring it belongs to the tournament.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.

    Returns:
        Match: The match object.

    Raises:
        ValueError: If match is not found or doesn't belong to the tournament.
    """
    match = Match.query.get(match_id)
    if not match:
        raise ValueError("Match not found")
    if match.tournament_id != tournament_id:
        raise ValueError("Match does not belong to this tournament")
    return match


def create_match(tournament_id: UUID, participant1_id: UUID = None, participant2_id: UUID = None, group_id: UUID = None, playoff_match_id: UUID = None, type: str = None, format: str = None):
    """
    Create a new match in a tournament.

    Args:
        tournament_id: The UUID of the tournament.
        participant1_id: The UUID of the first participant (User or Team).
        participant2_id: The UUID of the second participant (User or Team).
        group_id: The UUID of the group (for group stage matches).
        playoff_match_id: The UUID of the playoff match (for playoff stage matches).
        type: The match type (e.g., 'group', 'playoff').
        format: The match format (e.g., 'bo1', 'bo3').

    Returns:
        Match: The created match object.

    Raises:
        ValueError: If tournament, group, or playoff match is not found, or invalid participants.
    """
    tournament = get_tournament(tournament_id)

    if group_id and playoff_match_id:
        raise ValueError(
            "Match cannot belong to both group and playoff stages")

    if group_id:
        group = Group.query.get(group_id)
        if not group:
            raise ValueError("Group not found")
        if group.group_stage.tournament_id != tournament_id:
            raise ValueError("Group does not belong to this tournament")

    if playoff_match_id:
        playoff_match = PlayoffStageMatch.query.get(playoff_match_id)
        if not playoff_match:
            raise ValueError("Playoff match not found")
        if playoff_match.playoff_stage.tournament_id != tournament_id:
            raise ValueError(
                "Playoff match does not belong to this tournament")

    if participant1_id:
        participant1 = User.query.get(
            participant1_id) or Team.query.get(participant1_id)
        if not participant1:
            raise ValueError("Participant 1 not found")
    if participant2_id:
        participant2 = User.query.get(
            participant2_id) or Team.query.get(participant2_id)
        if not participant2:
            raise ValueError("Participant 2 not found")

    match = Match(
        tournament_id=tournament_id,
        participant1_id=participant1_id,
        participant2_id=participant2_id,
        group_id=group_id,
        playoff_match_id=playoff_match_id,
        type=type,
        format=format,
        status="scheduled",
        is_playoff=playoff_match_id is not None
    )

    try:
        with db.session.begin():
            db.session.add(match)
        return match
    except IntegrityError:
        raise ValueError("Failed to create match due to database constraints")


def update_match_results(tournament_id: UUID, match_id: UUID, winner_id: UUID = None, status: str = None):
    """
    Update the results of a match.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.
        winner_id: The UUID of the winner (User or Team).
        status: The new status of the match (e.g., 'completed', 'cancelled').

    Returns:
        Match: The updated match object.

    Raises:
        ValueError: If tournament, match, or winner is not found, or match doesn't belong to the tournament.
    """
    match = get_match(tournament_id, match_id)

    if winner_id:
        winner = User.query.get(winner_id) or Team.query.get(winner_id)
        if not winner:
            raise ValueError("Winner not found")
        if winner_id not in [match.participant1_id, match.participant2_id]:
            raise ValueError("Winner must be one of the participants")
        match.winner_id = winner_id

    if status:
        if status not in ["scheduled", "ongoing", "completed", "cancelled"]:
            raise ValueError("Invalid match status")
        match.status = status

    with db.session.begin():
        db.session.add(match)
    return match


def update_map_results(tournament_id: UUID, match_id: UUID, map_id: UUID, winner_id: UUID = None):
    """
    Update the results of a specific map in a match.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.
        map_id: The UUID of the map.
        winner_id: The UUID of the winner (User or Team).

    Returns:
        Map: The updated map object.

    Raises:
        ValueError: If tournament, match, map, or winner is not found, or map doesn't belong to the match.
    """
    match = get_match(tournament_id, match_id)
    map_ = Map.query.get(map_id)
    if not map_:
        raise ValueError("Map not found")
    if map_.match_id != match_id:
        raise ValueError("Map does not belong to this match")

    if winner_id:
        winner = User.query.get(winner_id) or Team.query.get(winner_id)
        if not winner:
            raise ValueError("Winner not found")
        if winner_id not in [match.participant1_id, match.participant2_id]:
            raise ValueError("Winner must be one of the participants")
        map_.winner_id = winner_id

    with db.session.begin():
        db.session.add(map_)
    return map_


def register_for_tournament(tournament_id: UUID, participant_id: UUID, is_team: bool = False):
    """
    Register a user or team for a tournament.

    Args:
        tournament_id: The UUID of the tournament.
        participant_id: The UUID of the user or team.
        is_team: Whether the participant is a team (True) or user (False).

    Returns:
        Tournament: The updated tournament object.

    Raises:
        ValueError: If tournament, participant, or registration conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament is not open for registration")

    if tournament.max_participants and len(tournament.participants) + len(tournament.teams) >= tournament.max_participants:
        raise ValueError("Tournament has reached maximum participants")

    if is_team:
        team = Team.query.get(participant_id)
        if not team:
            raise ValueError("Team not found")
        if team in tournament.teams:
            raise ValueError("Team is already registered")
        if team.members and not all(user in tournament.participants for user in team.members):
            raise ValueError(
                "All team members must be registered as participants")
        tournament.teams.append(team)
    else:
        user = User.query.get(participant_id)
        if not user:
            raise ValueError("User not found")
        if user.is_banned:
            raise ValueError("User is banned and cannot register")
        if user in tournament.participants:
            raise ValueError("User is already registered")
        tournament.participants.append(user)

    with db.session.begin():
        db.session.add(tournament)
    return tournament


def unregister_for_tournament(tournament_id: UUID, participant_id: UUID, is_team: bool = False):
    """
    Unregister a user or team from a tournament.

    Args:
        tournament_id: The UUID of the tournament.
        participant_id: The UUID of the user or team.
        is_team: Whether the participant is a team (True) or user (False).

    Returns:
        Tournament: The updated tournament object.

    Raises:
        ValueError: If tournament, participant, or unregistration conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament is not open for unregistration")

    if is_team:
        team = Team.query.get(participant_id)
        if not team:
            raise ValueError("Team not found")
        if team not in tournament.teams:
            raise ValueError("Team is not registered")
        if any(match for match in tournament.matches if match.participant1_id == participant_id or match.participant2_id == participant_id):
            raise ValueError("Cannot unregister team with scheduled matches")
        tournament.teams.remove(team)
    else:
        user = User.query.get(participant_id)
        if not user:
            raise ValueError("User not found")
        if user not in tournament.participants:
            raise ValueError("User is not registered")
        if any(match for match in tournament.matches if match.participant1_id == participant_id or match.participant2_id == participant_id):
            raise ValueError("Cannot unregister user with scheduled matches")
        tournament.participants.remove(user)

    with db.session.begin():
        db.session.add(tournament)
    return tournament


def start_tournament(tournament_id: UUID):
    """
    Start a tournament, transitioning it to 'ongoing' and ensuring stages are set.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        Tournament: The updated tournament object.

    Raises:
        ValueError: If tournament or conditions for starting are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament is not in open status")

    total_participants = len(tournament.participants) + len(tournament.teams)
    if total_participants < 2:
        raise ValueError("Tournament requires at least 2 participants")

    if not tournament.group_stage and not tournament.playoff_stage:
        raise ValueError(
            "Tournament requires at least one stage (group or playoff)")

    tournament.status = "ongoing"
    tournament.start_time = datetime.now(UTC)

    with db.session.begin():
        db.session.add(tournament)
    return tournament


def complete_tournament(tournament_id: UUID):
    """
    Complete a tournament, marking it as 'completed' and assigning prizes based on playoff results.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        Tournament: The updated tournament object.

    Raises:
        ValueError: If tournament, matches, or prize table conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "ongoing":
        raise ValueError("Tournament is not ongoing")

    if any(match.status != "completed" for match in tournament.matches):
        raise ValueError("Not all matches are completed")

    if not tournament.playoff_stage:
        raise ValueError(
            "Tournament requires a playoff stage to determine winners")

    if not tournament.prize_table:
        raise ValueError("Prize table is not set")

    # Find the grand final match (highest round number, bracket 'final')
    grand_final = PlayoffStageMatch.query.filter_by(
        playoff_stage_id=tournament.playoff_stage.id,
        bracket="final"
    ).order_by(PlayoffStageMatch.round_number.desc()).first()

    if not grand_final or not grand_final.match or not grand_final.match.winner_id:
        raise ValueError("Grand final match is not completed or has no winner")

    # Assign prizes
    prize_fund = tournament.prize_fund or 0
    winner_id = grand_final.match.winner_id
    loser_id = grand_final.match.participant1_id if grand_final.match.participant2_id == winner_id else grand_final.match.participant2_id

    # 1st place
    if not PrizeTableRow.query.filter_by(prize_table_id=tournament.prize_table.id, place=1).first():
        create_prizetable_row(
            tournament_id,
            place=1,
            user_id=winner_id if User.query.get(winner_id) else None,
            team_id=winner_id if Team.query.get(winner_id) else None,
            prize=prize_fund * 0.5
        )

    # 2nd place
    if not PrizeTableRow.query.filter_by(prize_table_id=tournament.prize_table.id, place=2).first():
        create_prizetable_row(
            tournament_id,
            place=2,
            user_id=loser_id if User.query.get(loser_id) else None,
            team_id=loser_id if Team.query.get(loser_id) else None,
            prize=prize_fund * 0.3
        )

    # 3rd place (winner of the last loser bracket match)
    loser_final = PlayoffStageMatch.query.filter_by(
        playoff_stage_id=tournament.playoff_stage.id,
        bracket="loser"
    ).order_by(PlayoffStageMatch.round_number.desc()).first()

    if loser_final and loser_final.match and loser_final.match.winner_id and not PrizeTableRow.query.filter_by(prize_table_id=tournament.prize_table.id, place=3).first():
        create_prizetable_row(
            tournament_id,
            place=3,
            user_id=loser_final.match.winner_id if User.query.get(
                loser_final.match.winner_id) else None,
            team_id=loser_final.match.winner_id if Team.query.get(
                loser_final.match.winner_id) else None,
            prize=prize_fund * 0.2
        )

    tournament.status = "completed"

    with db.session.begin():
        db.session.add(tournament)
    return tournament


def create_group_row(group_id: UUID, participant_id: UUID, is_team: bool):
    """
    Create a GroupRow entry for a participant in a group, using user_id or team_id based on is_team.

    Args:
        group_id: The UUID of the group.
        participant_id: The UUID of the participant (User or Team).
        is_team: Whether the participant is a team (True) or user (False).

    Returns:
        GroupRow: The created group row object.

    Raises:
        ValueError: If group or participant is not found, or row already exists.
    """
    group = Group.query.get(group_id)
    if not group:
        raise ValueError("Group not found")

    # Check if GroupRow already exists for this participant in the group
    existing_row = GroupRow.query.filter_by(
        group_id=group_id,
        user_id=participant_id if not is_team else None,
        team_id=participant_id if is_team else None
    ).first()
    if existing_row:
        raise ValueError(
            f"GroupRow for participant {participant_id} in group {group_id} already exists")

    # Verify participant exists
    participant = Team.query.get(
        participant_id) if is_team else User.query.get(participant_id)
    if not participant:
        raise ValueError(f"Participant {participant_id} not found")

    # Create GroupRow with initial values
    group_row = GroupRow(
        id=uuid.uuid4(),
        group_id=group_id,
        user_id=participant_id if not is_team else None,
        team_id=participant_id if is_team else None,
        place=0,  # Initial place, to be updated after matches
        wins=0,
        draws=0,
        loses=0
    )

    with db.session.begin():
        db.session.add(group_row)
    return group_row


def make_group_stage(tournament_id: UUID, num_groups: int, max_participants_per_group: int):
    """
    Create a group stage for a tournament with specified groups, using either participants or teams exclusively,
    distributing remaining participants evenly.

    Args:
        tournament_id: The UUID of the tournament.
        num_groups: Number of groups to create.
        max_participants_per_group: Maximum participants per group.

    Returns:
        GroupStage: The created group stage object.

    Raises:
        ValueError: If tournament, group parameters, or participant conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament must be open to create group stage")

    if tournament.group_stage:
        raise ValueError("Group stage already exists")

    # Check that tournament has either participants or teams, but not both
    has_participants = len(tournament.participants) > 0
    has_teams = len(tournament.teams) > 0
    if has_participants and has_teams:
        raise ValueError(
            "Tournament must contain either participants or teams, not both")
    if not has_participants and not has_teams:
        raise ValueError("Tournament has no participants or teams")

    # Determine total participants based on type
    total_participants = len(
        tournament.participants) if has_participants else len(tournament.teams)
    if total_participants < num_groups * 2:
        raise ValueError("Not enough participants for the number of groups")

    if num_groups < 1 or max_participants_per_group < 2:
        raise ValueError("Invalid number of groups or participants per group")

    group_stage = GroupStage(tournament_id=tournament_id)

    try:
        with db.session.begin():
            db.session.add(group_stage)
            # Create list of participant/team IDs
            all_participants = [p.id for p in tournament.participants] if has_participants else [
                t.id for t in tournament.teams]
            random.shuffle(all_participants)

            # Distribute participants with remainder
            participants_per_group = total_participants // num_groups
            remainder = total_participants % num_groups
            if participants_per_group > max_participants_per_group:
                raise ValueError(
                    "Too many participants for the specified group size")

            for i in range(num_groups):
                group_letter = chr(65 + i)  # A, B, C, ...
                start = i * participants_per_group
                end = start + participants_per_group + \
                    (1 if i < remainder else 0)
                group_participants = all_participants[start:end]
                make_group(group_stage.id, group_letter, max_participants_per_group,
                           group_participants, is_team=has_teams)
        return group_stage
    except IntegrityError:
        raise ValueError(
            "Failed to create group stage due to database constraints")


def make_group(group_stage_id: UUID, letter: str, max_participants: int, participants: list = None, is_team: bool = False):
    """
    Create a group within a group stage, generate matches, and create GroupRow entries for participants.

    Args:
        group_stage_id: The UUID of the group stage.
        letter: The group letter (e.g., 'A', 'B').
        max_participants: Maximum participants in the group.
        participants: List of participant/team UUIDs to add to the group.
        is_team: Whether the participants are teams (True) or users (False).

    Returns:
        Group: The created group object.

    Raises:
        ValueError: If group stage, letter, participants, or conditions are invalid.
    """
    group_stage = GroupStage.query.get(group_stage_id)
    if not group_stage:
        raise ValueError("Group stage not found")

    if Group.query.filter_by(group_stage_id=group_stage_id, letter=letter).first():
        raise ValueError(f"Group {letter} already exists in this group stage")

    if max_participants < 2:
        raise ValueError("Group must allow at least 2 participants")

    group = Group(
        group_stage_id=group_stage_id,
        letter=letter,
        max_participants=max_participants
    )

    try:
        with db.session.begin():
            db.session.add(group)
            # Add participants to the group
            if participants:
                for participant_id in participants:
                    participant = Team.query.get(
                        participant_id) if is_team else User.query.get(participant_id)
                    if not participant:
                        raise ValueError(
                            f"Participant {participant_id} not found")
                    group.participants.append(participant)
                    # Create GroupRow for the participant
                    create_group_row(group.id, participant_id, is_team)

            # Generate matches for all pairs of participants (each vs. each)
            if participants and len(participants) >= 2:
                tournament_id = group_stage.tournament_id
                for i, p1_id in enumerate(participants):
                    for p2_id in participants[i+1:]:
                        match = Match(
                            tournament_id=tournament_id,
                            participant1_id=p1_id,
                            participant2_id=p2_id,
                            group_id=group.id,
                            type="group",
                            format="bo1",
                            status="scheduled"
                        )
                        db.session.add(match)
        return group
    except IntegrityError:
        raise ValueError(
            "Failed to create group, matches, or group rows due to database constraints")


def generate_single_elimination_bracket(tournament_id: UUID, participants: list[UUID]):
    """
    Generate a single-elimination playoff bracket for a tournament with specified participants.

    Args:
        tournament_id: The UUID of the tournament.
        participants: List of UUIDs for participants (User or Team) to include in the playoff.

    Returns:
        PlayoffStage: The created playoff stage object.

    Raises:
        ValueError: If tournament, participants, or conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament must be open to create playoff stage")

    if tournament.playoff_stage:
        raise ValueError("Playoff stage already exists")

    # Validate participants list
    if not participants or len(participants) < 2:
        raise ValueError(
            "At least 2 participants are required for playoff stage")

    # Check if all participants are either Users or Teams, and verify existence
    is_team = None
    for participant_id in participants:
        participant = User.query.get(
            participant_id) or Team.query.get(participant_id)
        if not participant:
            raise ValueError(f"Participant {participant_id} not found")
        current_is_team = isinstance(participant, Team)
        if is_team is None:
            is_team = current_is_team
        elif is_team != current_is_team:
            raise ValueError(
                "All participants must be either Users or Teams, not mixed")

    # Calculate rounds needed (next power of 2)
    total_participants = len(participants)
    num_slots = 2 ** math.ceil(math.log2(total_participants))
    num_byes = num_slots - total_participants
    rounds = int(math.log2(num_slots))

    playoff_stage = PlayoffStage(tournament_id=tournament_id)

    try:
        with db.session.begin():
            db.session.add(playoff_stage)
            # Shuffle participants
            random.shuffle(participants)

            matches = []
            # First round
            for i in range(num_slots // 2):
                p1_id = participants[i * 2] if i * \
                    2 < len(participants) else None
                p2_id = participants[i * 2 + 1] if i * \
                    2 + 1 < len(participants) else None
                match = Match(
                    tournament_id=tournament_id,
                    participant1_id=p1_id,
                    participant2_id=p2_id,
                    type="playoff",
                    format="bo3",
                    status="scheduled"
                )
                db.session.add(match)
                db.session.flush()  # Ensure match.id is available
                playoff_match = PlayoffStageMatch(
                    playoff_stage_id=playoff_stage.id,
                    match_id=match.id,
                    round_number=1,
                    bracket="winner"
                )
                db.session.add(playoff_match)
                matches.append(playoff_match)

            # Create subsequent rounds
            for round_num in range(2, rounds + 1):
                num_matches_in_round = num_slots // (2 ** round_num)
                for i in range(num_matches_in_round):
                    match = Match(
                        tournament_id=tournament_id,
                        type="playoff",
                        format="bo3" if round_num < rounds else "bo5",
                        status="scheduled"
                    )
                    db.session.add(match)
                    db.session.flush()  # Ensure match.id is available
                    playoff_match = PlayoffStageMatch(
                        playoff_stage_id=playoff_stage.id,
                        match_id=match.id,
                        round_number=round_num,
                        bracket="winner"
                    )
                    db.session.add(playoff_match)
                    matches.append(playoff_match)

            # Set dependencies
            for round_num in range(1, rounds):
                matches_in_round = [
                    m for m in matches if m.round_number == round_num]
                next_round_matches = [
                    m for m in matches if m.round_number == round_num + 1]
                for i, match in enumerate(matches_in_round):
                    next_match = next_round_matches[i // 2]
                    # Pair winners from previous matches
                    if i % 2 == 0:
                        next_match.previous_winner_match_id = match.id
                    else:
                        next_match.previous_winner_match_id = match.id
        return playoff_stage
    except IntegrityError:
        raise ValueError(
            "Failed to create playoff stage due to database constraints")


def generate_double_elimination_bracket(tournament_id: UUID, participants: list[UUID]):
    """
    Generate a double-elimination playoff bracket for a tournament with specified participants.

    Args:
        tournament_id: The UUID of the tournament.
        participants: List of UUIDs for participants (User or Team) to include in the playoff.

    Returns:
        PlayoffStage: The created playoff stage object.

    Raises:
        ValueError: If tournament, participants, or conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.status != "open":
        raise ValueError("Tournament must be open to create playoff stage")

    if tournament.playoff_stage:
        raise ValueError("Playoff stage already exists")

    # Validate participants list
    if not participants or len(participants) < 2:
        raise ValueError(
            "At least 2 participants are required for playoff stage")

    # Check if all participants are either Users or Teams, and verify existence
    is_team = None
    for participant_id in participants:
        participant = User.query.get(
            participant_id) or Team.query.get(participant_id)
        if not participant:
            raise ValueError(f"Participant {participant_id} not found")
        current_is_team = isinstance(participant, Team)
        if is_team is None:
            is_team = current_is_team
        elif is_team != current_is_team:
            raise ValueError(
                "All participants must be either Users or Teams, not mixed")

    # Calculate structure: round up to power of 2
    total_participants = len(participants)
    num_slots = 2 ** math.ceil(math.log2(total_participants))
    num_byes = num_slots - total_participants
    winner_rounds = int(math.log2(num_slots))
    loser_rounds = winner_rounds * 2 - 1  # Loser bracket has more rounds

    playoff_stage = PlayoffStage(tournament_id=tournament_id)

    try:
        with db.session.begin():
            db.session.add(playoff_stage)
            # Shuffle participants
            random.shuffle(participants)

            winner_matches = []
            loser_matches = []

            # Create winner's bracket first round
            for i in range(num_slots // 2):
                p1_id = participants[i * 2] if i * \
                    2 < len(participants) else None
                p2_id = participants[i * 2 + 1] if i * \
                    2 + 1 < len(participants) else None
                match = Match(
                    tournament_id=tournament_id,
                    participant1_id=p1_id,
                    participant2_id=p2_id,
                    type="playoff",
                    format="bo3",
                    status="scheduled"
                )
                db.session.add(match)
                db.session.flush()  # Ensure match.id is available
                playoff_match = PlayoffStageMatch(
                    playoff_stage_id=playoff_stage.id,
                    match_id=match.id,
                    round_number=1,
                    bracket="winner"
                )
                db.session.add(playoff_match)
                winner_matches.append(playoff_match)

            # Create winner's bracket subsequent rounds
            for round_num in range(2, winner_rounds + 1):
                num_matches_in_round = num_slots // (2 ** round_num)
                for i in range(num_matches_in_round):
                    match = Match(
                        tournament_id=tournament_id,
                        type="playoff",
                        format="bo3",
                        status="scheduled"
                    )
                    db.session.add(match)
                    db.session.flush()  # Ensure match.id is available
                    playoff_match = PlayoffStageMatch(
                        playoff_stage_id=playoff_stage.id,
                        match_id=match.id,
                        round_number=round_num,
                        bracket="winner"
                    )
                    db.session.add(playoff_match)
                    winner_matches.append(playoff_match)

            # Create loser's bracket
            for round_num in range(1, loser_rounds + 1):
                if round_num == 1:
                    # Initial loser matches (from winner's round 1 losers)
                    num_matches = num_slots // 4
                elif round_num % 2 == 0:
                    # Matches combining loser bracket winners
                    num_matches = num_slots // (2 ** (round_num // 2 + 1))
                else:
                    # Matches with winner bracket losers
                    num_matches = num_slots // (2 ** ((round_num + 1) // 2))
                for i in range(num_matches):
                    match = Match(
                        tournament_id=tournament_id,
                        type="playoff",
                        format="bo3",
                        status="scheduled"
                    )
                    db.session.add(match)
                    db.session.flush()  # Ensure match.id is available
                    playoff_match = PlayoffStageMatch(
                        playoff_stage_id=playoff_stage.id,
                        match_id=match.id,
                        round_number=round_num,
                        bracket="loser"
                    )
                    db.session.add(playoff_match)
                    loser_matches.append(playoff_match)

            # Create grand final
            grand_final = Match(
                tournament_id=tournament_id,
                type="playoff",
                format="bo5",
                status="scheduled"
            )
            db.session.add(grand_final)
            db.session.flush()  # Ensure grand_final.id is available
            grand_final_pm = PlayoffStageMatch(
                playoff_stage_id=playoff_stage.id,
                match_id=grand_final.id,
                round_number=loser_rounds + 1,
                bracket="final"
            )
            db.session.add(grand_final_pm)

            # Set dependencies for winner's bracket
            for round_num in range(1, winner_rounds):
                matches_in_round = [
                    m for m in winner_matches if m.round_number == round_num]
                next_round_matches = [
                    m for m in winner_matches if m.round_number == round_num + 1]
                for i, match in enumerate(matches_in_round):
                    next_match = next_round_matches[i // 2]
                    # Winners from previous matches feed into the next match
                    if i % 2 == 0:
                        next_match.previous_winner_match_id = match.id
                    else:
                        next_match.previous_winner_match_id = match.id

            # Set dependencies for loser's bracket
            for round_num in range(1, loser_rounds):
                matches_in_round = [
                    m for m in loser_matches if m.round_number == round_num]
                next_round_matches = [
                    m for m in loser_matches if m.round_number == round_num + 1]
                if round_num % 2 == 1:
                    # Odd rounds: losers from winner bracket + winners from previous loser round
                    winner_round = (round_num + 1) // 2
                    winner_matches_in_round = [
                        m for m in winner_matches if m.round_number == winner_round]
                    for i, match in enumerate(matches_in_round):
                        next_match = next_round_matches[i // 2]
                        if i % 2 == 0:
                            # Loser from winner bracket
                            winner_match = winner_matches_in_round[i // 2]
                            next_match.previous_loser_match_id = winner_match.id
                        else:
                            # Winner from previous loser match
                            prev_loser_match = matches_in_round[i - 1]
                            next_match.previous_winner_match_id = prev_loser_match.id
                else:
                    # Even rounds: winners from previous loser round
                    for i, match in enumerate(matches_in_round):
                        next_match = next_round_matches[i // 2]
                        if i % 2 == 0:
                            next_match.previous_winner_match_id = match.id
                        else:
                            next_match.previous_winner_match_id = match.id

            # Grand final dependencies
            final_winner_match = [
                m for m in winner_matches if m.round_number == winner_rounds][0]
            final_loser_match = [
                m for m in loser_matches if m.round_number == loser_rounds][0]
            grand_final_pm.previous_winner_match_id = final_winner_match.id
            grand_final_pm.previous_loser_match_id = final_loser_match.id
        return playoff_stage
    except IntegrityError:
        raise ValueError(
            "Failed to create playoff stage due to database constraints")


def complete_map(tournament_id: UUID, match_id: UUID, map_id: UUID, winner_id: UUID):
    """
    Complete a map by setting its winner.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.
        map_id: The UUID of the map.
        winner_id: The UUID of the winner (User or Team).

    Returns:
        Map: The updated map object.

    Raises:
        ValueError: If tournament, match, map, or winner is invalid.
    """
    map_ = update_map_results(tournament_id, match_id, map_id, winner_id)

    # Check if match should be completed based on map results
    match = get_match(tournament_id, match_id)
    if match.format.startswith("bo"):
        num_maps = int(match.format[2:])
        map_wins = {}
        for map_ in match.maps:
            if map_.winner_id:
                map_wins[map_.winner_id] = map_wins.get(map_.winner_id, 0) + 1
        for participant_id, wins in map_wins.items():
            if wins > num_maps // 2:
                with db.session.begin():
                    match.winner_id = participant_id
                    match.status = "completed"
                    db.session.add(match)
                update_next_match_participants(
                    tournament_id, match_id, participant_id)
                break

    return map_


def complete_match(tournament_id: UUID, match_id: UUID, winner_id: UUID):
    """
    Complete a match by setting its winner and updating next matches.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.
        winner_id: The UUID of the winner (User or Team).

    Returns:
        Match: The updated match object.

    Raises:
        ValueError: If tournament, match, or winner is invalid.
    """
    match = update_match_results(
        tournament_id, match_id, winner_id, "completed")

    # Update next match participants
    update_next_match_participants(tournament_id, match_id, winner_id)

    return match


def update_next_match_participants(tournament_id: UUID, match_id: UUID, winner_id: UUID):
    """
    Update the participants of the next match based on the current match's winner.

    Args:
        tournament_id: The UUID of the tournament.
        match_id: The UUID of the match.
        winner_id: The UUID of the winner (User or Team).

    Returns:
        None

    Raises:
        ValueError: If tournament, match, or next match is invalid.
    """
    match = get_match(tournament_id, match_id)

    if not match.playoff_match_id:
        return  # No next match for group stage or non-playoff matches

    playoff_match = PlayoffStageMatch.query.get(match.playoff_match_id)
    if not playoff_match:
        raise ValueError("Playoff match not found")

    # Find next matches (winner and loser brackets)
    next_winner_match = PlayoffStageMatch.query.filter_by(
        playoff_stage_id=playoff_match.playoff_stage_id,
        previous_winner_match_id=playoff_match.id
    ).first()
    next_loser_match = PlayoffStageMatch.query.filter_by(
        playoff_stage_id=playoff_match.playoff_stage_id,
        previous_loser_match_id=playoff_match.id
    ).first()

    try:
        with db.session.begin():
            if next_winner_match and next_winner_match.match:
                next_match = next_winner_match.match
                if not next_match.participant1_id:
                    next_match.participant1_id = winner_id
                elif not next_match.participant2_id:
                    next_match.participant2_id = winner_id
                else:
                    raise ValueError(
                        "Next winner match already has both participants")
                db.session.add(next_match)

            if next_loser_match and next_loser_match.match:
                loser_id = match.participant1_id if match.participant2_id == winner_id else match.participant2_id
                next_match = next_loser_match.match
                if not next_match.participant1_id:
                    next_match.participant1_id = loser_id
                elif not next_match.participant2_id:
                    next_match.participant2_id = loser_id
                else:
                    raise ValueError(
                        "Next loser match already has both participants")
                db.session.add(next_match)
    except IntegrityError:
        raise ValueError(
            "Failed to update next match participants due to database constraints")


def create_prizetable(tournament_id: UUID):
    """
    Create a prize table for a tournament.

    Args:
        tournament_id: The UUID of the tournament.

    Returns:
        PrizeTable: The created prize table object.

    Raises:
        ValueError: If tournament or conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    if tournament.prize_table:
        raise ValueError("Prize table already exists")

    if tournament.status == "completed":
        raise ValueError("Cannot create prize table for completed tournament")

    prize_table = PrizeTable(tournament_id=tournament_id)

    try:
        with db.session.begin():
            db.session.add(prize_table)
        return prize_table
    except IntegrityError:
        raise ValueError(
            "Failed to create prize table due to database constraints")


def create_prizetable_row(tournament_id: UUID, place: int, user_id: UUID = None, team_id: UUID = None, prize: float = 0.0):
    """
    Create a row in a tournament's prize table.

    Args:
        tournament_id: The UUID of the tournament.
        place: The place (e.g., 1 for 1st place).
        user_id: The UUID of the user (optional).
        team_id: The UUID of the team (optional).
        prize: The prize amount.

    Returns:
        PrizeTableRow: The created prize table row object.

    Raises:
        ValueError: If tournament, prize table, or conditions are invalid.
    """
    tournament = get_tournament(tournament_id)

    prize_table = tournament.prize_table
    if not prize_table:
        raise ValueError("Prize table does not exist")

    if PrizeTableRow.query.filter_by(prize_table_id=prize_table.id, place=place).first():
        raise ValueError(f"Prize table row for place {place} already exists")

    if user_id and team_id:
        raise ValueError("Cannot assign both user and team to prize table row")

    if user_id:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        if user not in tournament.participants:
            raise ValueError("User is not a participant in the tournament")
    if team_id:
        team = Team.query.get(team_id)
        if not team:
            raise ValueError("Team not found")
        if team not in tournament.teams:
            raise ValueError("Team is not a participant in the tournament")

    if prize < 0 or (tournament.prize_fund and prize > tournament.prize_fund):
        raise ValueError("Invalid prize amount")

    row = PrizeTableRow(
        prize_table_id=prize_table.id,
        place=place,
        user_id=user_id,
        team_id=team_id,
        prize=prize
    )

    try:
        with db.session.begin():
            db.session.add(row)
        return row
    except IntegrityError:
        raise ValueError(
            "Failed to create prize table row due to database constraints")
