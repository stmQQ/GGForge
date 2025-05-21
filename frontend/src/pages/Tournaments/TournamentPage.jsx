import { useParams, Link } from "react-router-dom";
import { useState, useEffect, useNavigate, useContext } from "react";
import "./tournamentPage.scss";
import TabSwitch from "../../components/TabSwitch/TabSwitch.jsx";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import MatchCard from "../../components/Card/MatchCard.jsx";
import SubmitButton from "../../components/Button/SubmitButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import { API_URL } from "../../constants";
import {
  getTournament,
  getTournamentGroupStage,
  getTournamentPlayoffStage,
  getTournamentPrizeTable,
  getAllTournamentMatches,
  registerForTournament,
  unregisterForTournament,
} from "../../api/tournaments";
import { getTeam, getUserTeams } from "../../api/teams";
import { getProfile } from "../../api/users.js";
import { AuthContext } from "../../context/AuthContext.jsx";

export default function TournamentPage() {
  const { id } = useParams();
  const { user } = useContext(AuthContext); // Получаем user из AuthContext

  const currentUserId = user?.id || null;
  const [tournament, setTournament] = useState(null);
  const [groupStage, setGroupStage] = useState(null);
  const [playoffStage, setPlayoffStage] = useState(null);
  const [prizeTable, setPrizeTable] = useState(null);
  const [matches, setMatches] = useState([]);
  const [teams, setTeams] = useState([]);
  const [isCreator, setCreator] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [activeStage, setActiveStage] = useState("playoff");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const tabs = [
    { id: "overview", label: "Обзор" },
    { id: "bracket", label: "Сетка" },
    { id: "matches", label: "Матчи" },
    { id: "participants", label: "Участники" },
    { id: "prizes", label: "Призы" },
  ];

  const stageFilters = [
    ...(tournament?.has_groupstage ? [{ id: "group", label: "Групповой" }] : []),
    { id: "playoff", label: "Плей-офф" },
    { id: "final", label: "Финал" },
  ];

  const defaultParticipant = {
    id: null,
    name: "TBD",
    avatar: `${API_URL}/static/avatars/default.png`,
  };

  const getParticipantUser = async (id) => {
    if (!id || id === "undefined") return defaultParticipant;
    const participant = await getProfile(id).catch(() => defaultParticipant);
    return participant.data && participant.data.avatar
      ? { ...participant.data, avatar: `${API_URL}/${participant.data.avatar}` }
      : participant.data || defaultParticipant;
  };

  const getParticipantTeam = async (id) => {
    if (!id || id === "undefined") return defaultParticipant;
    const team = await getTeam(id).catch(() => defaultParticipant);
    return team.data && team.data.avatar
      ? { ...team.data, avatar: `${API_URL}/${team.data.avatar}` }
      : team.data || defaultParticipant;
  };

  const handleMatchFinish = async (matchId, updatedMatch) => {
    try {
      // Обновляем состояние матчей
      setMatches((prevMatches) =>
        prevMatches.map((match) =>
          match.id === matchId
            ? {
              ...match,
              status: updatedMatch.status,
              participant1_score: updatedMatch.participant1_score || 0,
              participant2_score: updatedMatch.participant2_score || 0,
              maps: updatedMatch.maps.map((map) => ({
                id: map.id,
                external_url: map.external_url,
                winner_id: map.winner_id,
              })),
            }
            : match
        )
      );

      // Если матч завершён, обновляем данные плей-офф или группового этапа
      if (updatedMatch.status === "completed") {
        const matchesResponse = await getAllTournamentMatches(id);
        setMatches(
          matchesResponse.data.map((m) => ({
            id: m.id,
            number: m.number,
            participant1: m.participant1 || m.team1 || defaultParticipant,
            participant2: m.participant2 || m.team2 || defaultParticipant,
            participant1_score: m.participant1_score || 0,
            participant2_score: m.participant2_score || 0,
            status: m.status,
            creator: tournament.manager.id,
            format: m.format || "BO1",
            maps: m.maps.map((map) => ({
              id: map.id,
              external_url: map.external_url,
              winner_id: map.winner_id,
            })),
            group: m.group ? { letter: m.group.letter } : null,
            playoff_match: m.playoff_match ? { round_number: m.playoff_match.round_number } : null,
          }))
        );

        // Обновляем плей-офф, если матч был в плей-офф
        const playoffStageResponse = await getTournamentPlayoffStage(id);
        const playoffMatches = playoffStageResponse.data.playoff_matches;
        const finalMatch = playoffMatches.length > 0 ? playoffMatches[playoffMatches.length - 1] : null;

        const rounds = await playoffMatches
          .slice(0, -1)
          .reduce(async (accPromise, m) => {
            const acc = await accPromise;
            const round = acc.find((r) => r.letter === m.round_number);

            const [participant1Data, participant2Data] = await Promise.all([m.match.participant1_id && m.match.participant1_id !== "undefined" ? getParticipantUser(m.match.participant1_id) : m.match.team1_id && m.match.team1_id !== "undefined" ? getParticipantTeam(m.match.team1_id) : defaultParticipant, m.match.participant2_id && m.match.participant2_id !== "undefined" ? getParticipantUser(m.match.participant2_id) : m.match.team2_id && m.match.team2_id !== "undefined" ? getParticipantTeam(m.match.team2_id) : defaultParticipant,]);
            console.log(participant1Data)
            if (participant1Data.user) participant1Data.user.avatar = `${API_URL}/${participant1Data.user.avatar}`
            if (participant2Data.user) participant2Data.user.avatar = `${API_URL}/${participant2Data.user.avatar}`
            console.log(participant1Data)
            const match = {
              id: m.match.id,
              tournament_id: tournament.id,
              number: m.match.number,
              participant1: participant1Data.user || participant1Data,
              participant2: participant2Data.user || participant2Data,
              participant1_score: m.match.participant1_score || 0,
              participant2_score: m.match.participant2_score || 0,
              status: m.match.status,
              creator: tournament.manager.id,
              user_id: currentUserId,
              format: m.match.format || "BO1",
              maps: m.match.maps.map((map) => ({
                id: map.id,
                external_url: map.external_url,
                winner_id: map.winner_id,
              })),
            };

            if (round) {
              round.matches.push(match);
            } else {
              acc.push({ id: m.id, letter: m.round_number, matches: [match] });
            }

            return acc;
          }, Promise.resolve([]));

        let final = {
          id: "final",
          number: "final",
          participant1: defaultParticipant,
          participant2: defaultParticipant,
          participant1_score: 0,
          participant2_score: 0,
          status: "scheduled",
          creator: tournament.manager.id,
          user_id: currentUserId,
          format: "BO1",
          maps: [],
        };

        if (finalMatch) {
          const [finalParticipant1, finalParticipant2] = await Promise.all([finalMatch.match.participant1_id && finalMatch.match.participant1_id !== "undefined" ? getParticipantUser(finalMatch.match.participant1_id) : finalMatch.match.team1_id && finalMatch.match.team1_id !== "undefined" ? getParticipantTeam(finalMatch.match.team1_id) : defaultParticipant, finalMatch.match.participant2_id && finalMatch.match.participant2_id !== "undefined" ? getParticipantUser(finalMatch.match.participant2_id) : finalMatch.match.team2_id && finalMatch.match.team2_id !== "undefined" ? getParticipantTeam(finalMatch.match.team2_id) : defaultParticipant,]);

          final = {
            id: finalMatch.match.id,
            tournament_id: tournament.id,
            number: finalMatch.match.number || finalMatch.match.id,
            participant1: finalParticipant1,
            participant2: finalParticipant2,
            participant1_score: finalMatch.match.participant1_score || 0,
            participant2_score: finalMatch.match.participant2_score || 0,
            status: finalMatch.match.status,
            creator: tournament.manager.id,
            user_id: currentUserId,
            format: finalMatch.match.format || "BO1",
            maps: finalMatch.match.maps.map((map) => ({
              id: map.id,
              external_url: map.external_url,
              winner_id: map.winner_id,
            })),
          };
        }

        setPlayoffStage({
          rounds,
          final,
        });
      }
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    async function fetchData() {
      try {
        // Турнир
        const tournamentResponse = await getTournament(id);
        const tournamentData = tournamentResponse.data;
        // console.log(tournamentData)
        setTournament({
          id: tournamentData.id,
          title: tournamentData.title,
          img: tournamentData.banner_url ? `${API_URL}/${tournamentData.banner_url}` : "/src/images/default-image.png",
          date: tournamentData.start_time,
          status: tournamentData.status,
          description: tournamentData.description || "Описание отсутствует",
          prize_fund: tournamentData.prize_fund || "0",
          game: { title: tournamentData.game.title || "undefined" },
          manager: {
            id: tournamentData.creator.id,
            name: tournamentData.creator.name,
            avatar: tournamentData.creator.avatar
              ? `${API_URL}/${tournamentData.creator.avatar}`
              : `${API_URL}/static/avatars/default.png`,
          },
          contact: tournamentData.contact || "@Organizer",
          has_groupstage: !!tournamentData.group_stage,
          team: tournamentData.type === "team",
          participants: tournamentData.participants.map((p) => ({
            id: p.id,
            name: p.name,
            avatar: p.avatar ? `${API_URL}/${p.avatar}` : `${API_URL}/static/avatars/default.png`,
          })),
          teams: tournamentData.teams.map((t) => ({
            id: t.id,
            name: t.title,
            avatar: t.avatar ? `${API_URL}/${t.avatar}` : `${API_URL}/static/avatars/default.png`,
          })),
        });
        console.log(tournamentData)

        // Проверка статуса заявки
        setIsApplied(
          tournamentData.type === "team"
            ? tournamentData.teams.some((t) => teams.some((userTeam) => userTeam.id === t.id))
            : tournamentData.participants.some((p) => p.id === currentUserId)
        );

        // console.log(currentUserId, tournament.manager.id);
        // Групповой этап
        if (tournamentData.group_stage) {
          const groupStageResponse = await getTournamentGroupStage(id);

          const groups = await Promise.all(
            groupStageResponse.data.groups.map(async (g) => {
              const groupRows = await Promise.all(
                g.rows.map(async (r) => {
                  const userData = r.user_id && r.user_id !== "undefined"
                    ? await getParticipantUser(r.user_id)
                    : null;
                  const teamData = r.team_id && r.team_id !== "undefined"
                    ? await getParticipantTeam(r.team_id)
                    : null;
                  // console.log(r)
                  // console.log(defaultParticipant)
                  return {
                    id: r.id,
                    place: r.place,
                    wins: r.wins,
                    draws: r.draws,
                    loses: r.loses,
                    user: userData?.user || userData || null,
                    team: teamData || (r.team_id ? defaultParticipant : null),
                  };
                })
              );

              const matches = await Promise.all(
                g.matches.map(async (m) => {

                  const [participant1Data, participant2Data] = await Promise.all([
                    m.participant1_id && m.participant1_id !== "undefined"
                      ? getParticipantUser(m.participant1_id)
                      : m.team1_id && m.team1_id !== "undefined"
                        ? getParticipantTeam(m.team1_id)
                        : defaultParticipant,
                    m.participant2_id && m.participant2_id !== "undefined"
                      ? getParticipantUser(m.participant2_id)
                      : m.team2_id && m.team2_id !== "undefined"
                        ? getParticipantTeam(m.team2_id)
                        : defaultParticipant,
                  ]);
                  // console.log(participant1Data)

                  if (participant1Data.user) participant1Data.user.avatar = `${API_URL}/${participant1Data.user.avatar}`;
                  if (participant2Data.user) participant2Data.user.avatar = `${API_URL}/${participant2Data.user.avatar}`;

                  return {
                    id: m.id,
                    tournament_id: m.tournament_id,
                    winner_id: m.winner_id,
                    number: m.number || m.id,
                    participant1: participant1Data.user || participant1Data,
                    participant2: participant2Data.user || participant2Data,
                    participant1_score: m.participant1_score || 0,
                    participant2_score: m.participant2_score || 0,
                    status: m.status,
                    creator: tournamentData.creator.id,
                    user_id: currentUserId,
                    format: m.format || "BO1",
                    maps: m.maps.map((map) => ({
                      id: map.id,
                      external_url: map.external_url,
                      winner_id: map.winner_id,
                    })),
                  };
                })
              );

              return {
                id: g.id,
                letter: g.letter,
                group_rows: groupRows,
                matches,
              };
            })
          );

          setGroupStage({ groups });
        }

        // Плей-офф
        const playoffStageResponse = await getTournamentPlayoffStage(id);
        const playoffMatches = playoffStageResponse.data.playoff_matches;
        const finalMatch = playoffMatches.length > 0 ? playoffMatches[playoffMatches.length - 1] : null;

        const rounds = await playoffMatches
          .slice(0, -1)
          .reduce(async (accPromise, m) => {
            const acc = await accPromise;
            const round = acc.find((r) => r.letter === m.round_number);

            const [participant1Data, participant2Data] = await Promise.all([
              m.match.participant1_id && m.match.participant1_id !== "undefined"
                ? getParticipantUser(m.match.participant1_id)
                : m.match.team1_id && m.match.team1_id !== "undefined"
                  ? getParticipantTeam(m.match.team1_id)
                  : defaultParticipant,
              m.match.participant2_id && m.match.participant2_id !== "undefined"
                ? getParticipantUser(m.match.participant2_id)
                : m.match.team2_id && m.match.team2_id !== "undefined"
                  ? getParticipantTeam(m.match.team2_id)
                  : defaultParticipant,
            ]);

            if (participant1Data.user) participant1Data.user.avatar = `${API_URL}/${participant1Data.user.avatar}`;
            if (participant2Data.user) participant2Data.user.avatar = `${API_URL}/${participant2Data.user.avatar}`;
            const match = {
              id: m.match.id,
              // winner_id: m.winner_id,
              tournament_id: tournamentData.id,
              number: m.match.number,
              participant1: participant1Data.user || participant1Data,
              participant2: participant2Data.user || participant2Data,
              participant1_score: m.match.participant1_score || 0,
              participant2_score: m.match.participant2_score || 0,
              status: m.match.status,
              creator: tournamentData.creator.id,
              user_id: currentUserId,
              format: m.match.format || "BO1",
              maps: m.match.maps.map((map) => ({
                id: map.id,
                external_url: map.external_url,
                winner_id: map.winner_id,
              })),
            };
            // console.log(match);

            if (round) {
              round.matches.push(match);
            } else {
              acc.push({ id: m.id, letter: m.round_number, matches: [match] });
            }

            return acc;
          }, Promise.resolve([]));
        // console.log(playoffStageResponse)
        let final = {
          id: "final",
          // winner_id: null,
          number: "final",
          participant1: defaultParticipant,
          participant2: defaultParticipant,
          participant1_score: 0,
          participant2_score: 0,
          status: "scheduled",
          creator: tournamentData.creator.id,
          user_id: currentUserId,
          format: "BO1",
          maps: [],
        };
        // console.log(final)
        if (finalMatch) {
          const [finalParticipant1, finalParticipant2] = await Promise.all([
            finalMatch.match.participant1_id && finalMatch.match.participant1_id !== "undefined"
              ? getParticipantUser(finalMatch.match.participant1_id)
              : finalMatch.match.team1_id && finalMatch.match.team1_id !== "undefined"
                ? getParticipantTeam(finalMatch.match.team1_id)
                : defaultParticipant,
            finalMatch.match.participant2_id && finalMatch.match.participant2_id !== "undefined"
              ? getParticipantUser(finalMatch.match.participant2_id)
              : finalMatch.match.team2_id && finalMatch.match.team2_id !== "undefined"
                ? getParticipantTeam(finalMatch.match.team2_id)
                : defaultParticipant,
          ]);
          // console.log(finalMatch)
          final = {
            id: finalMatch.match.id,
            // winner_id: m.winner_id,
            tournament_id: tournamentData.id,
            number: finalMatch.match.number || finalMatch.match.id,
            participant1: finalParticipant1,
            participant2: finalParticipant2,
            participant1_score: finalMatch.match.participant1_score || 0,
            participant2_score: finalMatch.match.participant2_score || 0,
            status: finalMatch.match.status,
            creator: tournamentData.creator.id,
            user_id: currentUserId,
            format: finalMatch.match.format || "BO1",
            maps: finalMatch.match.maps.map((map) => ({
              id: map.id,
              external_url: map.external_url,
              winner_id: map.winner_id,
            })),
          };
        }
        // console.log(final)

        setPlayoffStage({
          rounds,
          final,
        });

        // Призы
        const prizeTableResponse = await getTournamentPrizeTable(id);
        setPrizeTable({
          rows: prizeTableResponse.data.rows.map((r) => ({
            place: r.place,
            id: r.user?.id || r.team?.id || r.id,
            name: r.user?.name || r.team?.title || "Неизвестно",
            avatar: r.user?.avatar || r.team?.avatar
              ? `${API_URL}/${r.user?.avatar || r.team?.avatar}`
              : `${API_URL}/static/avatars/default.png`,
            prize: r.prize || "0",
          })),
        });
        // Матчи
        const matchesResponse = await getAllTournamentMatches(id);
        // console.log(matchesResponse)
        setMatches(
          matchesResponse.data.map((m) => ({
            id: m.id,
            // winner_id: m.winner_id,
            tournament_id: tournamentData.id,
            number: m.number,
            participant1: m.participant1 || m.team1 || defaultParticipant,
            participant2: m.participant2 || m.team2 || defaultParticipant,
            participant1_score: m.participant1_score || 0,
            participant2_score: m.participant2_score || 0,
            status: m.status,
            creator: tournamentData.creator.id,
            format: m.format || "BO1",
            maps: m.maps.map((map) => ({
              id: map.id,
              external_url: map.external_url,
              winner_id: map.winner_id,
            })),
            group: m.group ? { letter: m.group.letter } : null,
            playoff_match: m.playoff_match ? { round_number: m.playoff_match.round_number } : null,
          }))
        );

        // Команды пользователя
        const teamsResponse = await getUserTeams();
        // console.log(teamsResponse)
        setTeams(
          teamsResponse.data[0].member_teams.map((t) => ({
            id: t.id,
            name: t.title,
            avatar: t.avatar ? `${API_URL}/${t.avatar}` : `${API_URL}/static/team_logos/default.png`,
          }))
        );
        setCreator(tournament?.manager?.id === currentUserId);
        setIsLoading(false);

      } catch (err) {
        setError(err.response?.data?.msg);
        setIsLoading(false);
      }
    }
    fetchData();
  }, [id, currentUserId]);

  const updateApplicationStatus = async () => {
    try {
      const tournamentResponse = await getTournament(id);
      const tournamentData = tournamentResponse.data;
      setTournament((prev) => ({
        ...prev,
        participants: tournamentData.participants.map((p) => ({
          id: p.id,
          name: p.name,
          avatar: p.avatar ? `${API_URL}/${p.avatar}` : `${API_URL}/static/avatars/default.png`,
        })),
        teams: tournamentData.teams.map((t) => ({
          id: t.id,
          name: t.title,
          avatar: t.avatar ? `${API_URL}/${t.avatar}` : `${API_URL}/static/team_logos/default.png`,
        })),
      }));
      setIsApplied(
        tournamentData.type === "team"
          ? tournamentData.teams.some((t) => teams.some((userTeam) => userTeam.id === t.id))
          : tournamentData.participants.some((p) => p.id === currentUserId)
      );
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка при обновлении статуса");
    }
  };

  const getTournamentStatus = (status) => {
    switch (status) {
      case "open": return "Открыт";
      case "ongoing": return "Идет";
      case "completed": return "Завершён";
      case "cancelled": return "Отменён";
      default: return "Неизвестно";
    }
  };

  const getMaxGroupRows = () => {
    if (!groupStage) return 1;
    return Math.max(...groupStage.groups.map((group) => group.group_rows.length), 1);
  };

  const greenRows = (() => {
    const maxRows = getMaxGroupRows();
    if (maxRows <= 4) return Math.ceil(maxRows / 2);
    if (maxRows === 5) return 2;
    if (maxRows >= 6 && maxRows <= 8) return 4;
    return maxRows - 2;
  })();

  const getRowClass = (index) => {
    return index < greenRows ? "row--green" : "row--red";
  };

  const handleApplyClick = async () => {
    if (tournament.status !== "open") return;
    try {
      if (isApplied) {
        await unregisterForTournament(
          id,
          tournament.team,
          tournament.team ? selectedTeam?.id : currentUserId
        );
        setIsApplied(false);
        setSelectedTeam(null);
        await updateApplicationStatus(); // Обновляем данные
      } else if (tournament.team) {
        setIsModalOpen(true);
      } else {
        const response = await registerForTournament(id, false, currentUserId);
        if (response.status === 200) {
          setIsApplied(true);
          await updateApplicationStatus(); // Обновляем данные
        } else {
          setError(response.data.msg || "Ошибка при подаче заявки");
        }
      }
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка при подаче заявки");
    }
  };

  const handleTeamSelect = (team) => {
    setSelectedTeam(team);
  };

  const handleTeamApply = async () => {
    if (!selectedTeam) {
      setError("Команда не выбрана");
      return;
    }
    try {
      const response = await registerForTournament(id, true, selectedTeam.id);
      if (response.status === 200) {
        setIsApplied(true);
        setIsModalOpen(false);
        setSelectedTeam(null);
        await updateApplicationStatus(); // Обновляем данные
      } else {
        setError(response.data.msg || "Ошибка при подаче заявки");
      }
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка при подаче заявки");
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedTeam(null);
  };

  const renderRound = (round) => (
    <div key={round.id} className="bracket-column">
      <h3 className="bracket-column__title">Раунд {round.letter}</h3>
      <div className="bracket-column__matches">
        {round.matches.map((match) => (
          <div key={match.id} className="bracket-match-wrapper">
            <MatchCard match={match} className="match-card--bracket" onFinish={handleMatchFinish} />
          </div>
        ))}
      </div>
    </div>
  );

  const renderFinal = () => (
    <div className="bracket-column">
      <h3 className="bracket-column__title">Финал</h3>
      <div className="bracket-column__matches">
        <div className="bracket-match-wrapper">
          <MatchCard match={playoffStage.final} className="match-card--bracket" onFinish={handleMatchFinish} />
        </div>
      </div>
    </div>
  );

  if (isLoading) return <div>Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!tournament) return <div>Турнир не найден</div>;

  const displayLocalTime = (utcTime) => {
    const utcDate = new Date(utcTime);
    return utcDate.toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' });
  };

  return (
    <div className="tournament-page">
      <div className="tournament-page__header">
        <img
          className="avatar-uploader"
          src={tournament.img}
          alt={tournament.title}
          loading="lazy"
          onError={(e) => (e.target.src = `${API_URL}/static/tournaments/default/trnt_${tournament.game.title.replace(/\s+/g, '')}.png`)}
        />
        <div className="tournament-page__header-left">
          <p>{displayLocalTime(tournament.date)}</p>
          <TitleH2 style="aboutgame__header-title" title={tournament.title} />
          <p className={`tournament-page__status status--${tournament.status}`}>
            {getTournamentStatus(tournament.status)}
          </p>
        </div>
        <div className="tournament-page__header-right">
          <SubmitButton
            text={isApplied ? "Отменить заявку" : "Подать заявку"}
            onClick={handleApplyClick}
            disabled={tournament.status !== "open"}
          />
        </div>
      </div>
      <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
      <div className="tab-content">
        {activeTab === "overview" && (
          <div className="tournament-page__overview">
            <div className="tournament-page__overview-section">
              <h3 className="tournament-page__overview-title">Описание</h3>
              <p className="tournament-page__overview-description">
                {tournament.description}
              </p>
            </div>
            <div className="tournament-page__overview-highlights">
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">Призовой фонд</h4>
                <p className="tournament-page__overview-card-content tournament-page__overview-prize">
                  {tournament.prize_fund
                    ? `${parseInt(tournament.prize_fund).toLocaleString()} ₽`
                    : "Не указан"}
                </p>
              </div>
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">Организатор</h4>
                <Link
                  to={`/profile/${tournament.manager.id}`}
                  className="tournament-page__overview-organizer"
                >
                  <img
                    src={tournament.manager.avatar}
                    alt="Organizer avatar"
                    className="tournament-page__overview-organizer-avatar"
                    loading="lazy"
                  />
                  <span className="tournament-page__overview-organizer-name">
                    {tournament.manager.name}
                  </span>
                </Link>
              </div>
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">Контакты</h4>
                <p className="tournament-page__overview-card-content">
                  {tournament.contact ? (
                    <a
                      href={tournament.contact}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="tournament-page__overview-contact-link"
                    >
                      {tournament.contact}
                    </a>
                  ) : (
                    "Контакты отсутствуют"
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "bracket" && (
          <>
            <div className="stage-filter">
              {stageFilters.map((stage) => (
                <button
                  key={stage.id}
                  className={`stage-filter__button ${activeStage === stage.id ? "stage-filter__button--active" : ""}`}
                  onClick={() => setActiveStage(stage.id)}
                >
                  {stage.label}
                </button>
              ))}
            </div>
            {activeStage === "group" && groupStage && (
              <div className="tournament-stage">
                <div className="tournament-stage__groups-container">
                  {groupStage.groups.map((group) => (
                    <div key={group.id} className="tournament-stage__group">
                      <h3 className="tournament-stage__title">Группа {group.letter}</h3>
                      <div className="tournament-stage__standings">
                        <div className="standings-header">
                          <span>Место</span>
                          <span>Участник</span>
                          <span>В</span>
                          <span>Н</span>
                          <span>П</span>
                          <span>Очки</span>
                        </div>
                        {group.group_rows.map((row, index) => {
                          const entity = row.team || row.user || { name: "TBD", avatar: "static/avatars/default.png" };
                          const linkTo = row.team ? `/team/${entity.id}` : row.user ? `/profile/${entity.id}` : null;
                          const points = row.wins * 2 + row.draws;
                          return (
                            <div key={row.id} className={`standings-row ${getRowClass(index)}`}>
                              <span>{row.place}</span>
                              <Link to={linkTo} className="standings-entity">
                                <img src={`${API_URL}/${entity.avatar}`} alt="avatar" className="entity-avatar" />
                                <span>{entity.name}</span>
                              </Link>
                              <span>{row.wins}</span>
                              <span>{row.draws}</span>
                              <span>{row.loses}</span>
                              <span>{points}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeStage === "playoff" && playoffStage && (
              <div className="tournament-bracket">
                {playoffStage.rounds.map(renderRound)}
                {renderFinal()}
              </div>
            )}
            {activeStage === "final" && playoffStage && (
              <MatchCard key={playoffStage.final.id} match={playoffStage.final} onFinish={handleMatchFinish} />
            )}
          </>
        )}

        {activeTab === "matches" && (
          <>
            <div className="stage-filter">
              {stageFilters.map((stage) => (
                <button
                  key={stage.id}
                  className={`stage-filter__button ${activeStage === stage.id ? "stage-filter__button--active" : ""}`}
                  onClick={() => setActiveStage(stage.id)}
                >
                  {stage.label}
                </button>
              ))}
            </div>
            {activeStage === "group" && groupStage && (
              <div className="tournament-stage">
                {groupStage.groups.map((group) => (
                  <div key={group.id} className="tournament-stage__group">
                    <h3 className="tournament-stage__title">Группа {group.letter}</h3>
                    <div className="tournament-stage__matches">
                      {group.matches.map((match) => (
                        <MatchCard
                          key={match.id}
                          match={match}
                          onFinish={handleMatchFinish} // Передаём handleMatchFinish
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {activeStage === "playoff" && playoffStage && (
              <div className="tournament-stage">
                {playoffStage.rounds.map((round) => (
                  <div key={round.id} className="tournament-stage__group">
                    <h3 className="tournament-stage__title">Раунд {round.letter}</h3>
                    <div className="tournament-stage__matches">
                      {round.matches.map((match) => (
                        <MatchCard
                          key={match.id}
                          match={match}
                          onFinish={handleMatchFinish} // Передаём handleMatchFinish
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {activeStage === "final" && playoffStage && (
              <MatchCard
                key={playoffStage.final.id}
                match={playoffStage.final}
                onFinish={handleMatchFinish} // Передаём handleMatchFinish
              />
            )}
          </>
        )}

        {activeTab === "participants" && (
          <RoundCards
            users={tournament.team ? tournament.teams : tournament.participants}
            isRequest={false}
            isTeam={tournament.team}
          />
        )}

        {activeTab === "prizes" && (
          tournament.status === "completed" && prizeTable ? (
            <div className="tournament-page__prizes">
              <div className="tournament-page__prizes-header">
                <span>№</span>
                <span>Ник</span>
                <span>Приз</span>
              </div>
              {[...prizeTable.rows]
                .sort((a, b) => a.place - b.place)
                .map((p) => (
                  <div className="tournament-page__prizes-row" key={p.id}>
                    <span>{p.place}</span>
                    <Link to={tournament.p ? `/team/${p.id}` : `/profile/${p.id}`} className="tournament-page__team-link">
                      <img src={p.avatar} alt="avatar" className="team-avatar" />
                      {p.name}
                    </Link>
                    <span>{p.prize ? `${parseInt(p.prize).toLocaleString()}₽` : "-"}</span>
                  </div>
                ))}
            </div>
          ) : (
            <p className="tournament-page__not-completed">
              Турнир ещё не завершён. Таблица призов появится после окончания.
            </p>
          )
        )}
      </div>
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <TitleH2 title="Выберите команду" />
        <div className="modal-content__teams">
          <RoundCards
            style="modal"
            users={teams}
            isRequest={false}
            isTeam={true}
            onSelect={handleTeamSelect}
            selectedTeamId={selectedTeam?.id}
          />
        </div>
        <div className="modal-content__actions">
          <SubmitButton
            text="Подать заявку"
            onClick={handleTeamApply}
            disabled={!selectedTeam}
          />
        </div>
      </Modal>
    </div>
  );
}