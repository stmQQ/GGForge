import { useParams, Link } from "react-router-dom";
import { useState } from "react";
import "./tournamentPage.scss";

import TabSwich from "../../components/TabSwitch/TabSwith.jsx";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import MatchCard from "../../components/Card/MatchCard.jsx";
import SubmitButton from "../../components/Button/SubmitButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";

import game1 from "../../images/game2.jpg";
import { commands } from "../../helpers/commands.js";
import { tournament } from "../../helpers/tournamentPage.js";


const resultPlaces = [
  { place: 1, id: 0, avatar: "/src/images/game1.jpg", name: "da", prize: 50 },
  { place: 2, id: 1, avatar: "/src/images/game1.jpg", name: "gg", prize: 40 },
  { place: 3, id: 2, avatar: "/src/images/game1.jpg", name: "scc", prize: 20 },
  { place: 4, id: 3, avatar: "/src/images/game1.jpg", name: "gg", prize: 0 },
  { place: 5, id: 4, avatar: "/src/images/game1.jpg", name: "ww", prize: 0 },
];


const getMaxGroupRows = () => {
  return Math.max(
    ...tournament.group_stage.groups.map((group) => group.group_rows.length),
    1
  );
};

const greenRows = (() => {
  const maxRows = getMaxGroupRows();
  if (maxRows <= 4) return Math.ceil(maxRows / 2);
  if (maxRows === 5) return 2;
  if (maxRows >= 6 && maxRows <= 8) return 4;
  return maxRows - 2; // For safety, though max is 8 here
})();

const getRowClass = (index) => {
  if (index < greenRows) return "row--green";
  return "row--red";
};


export default function TournamentPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("overview");
  const [activeStage, setActiveStage] = useState("playoff");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);

  const tabs = [
    { id: "overview", label: "Обзор" },
    { id: "bracket", label: "Сетка" },
    { id: "matches", label: "Матчи" },
    { id: "participants", label: "Участники" },
    { id: "prizes", label: "Призы" },
  ];

  const stageFilters = [
    ...(tournament.has_groupstage ? [{ id: "group", label: "Групповой" }] : []),
    { id: "playoff", label: "Плей-офф" },
    { id: "final", label: "Финал" },
  ];

  const getTournamentStatus = (status) => {
    switch (status) {
      case "open":
        return "Открыт";
      case "ongoing":
        return "Идет";
      case "completed":
        return "Завершён";
      case "cancelled":
        return "Отменён";
      default:
        return "Неизвестно";
    }
  };

  const handleApplyClick = () => {
    if (tournament.status !== "open") return;

    if (isApplied) {
      // Отменяем заявку
      setIsApplied(false);
      console.log("Заявка отменена");
    } else if (tournament.team) {
      // Открываем модальное окно для выбора команды
      setIsModalOpen(true);
    } else {
      // Отправляем заявку для индивидуального участия
      setIsApplied(true);
      console.log("Отправка заявки на сервер для индивидуального участия");
    }
  };

  const handleTeamSelect = (team) => {
    setSelectedTeam(team);
  };

  const handleTeamApply = () => {
    if (!selectedTeam) {
      console.log("Ошибка: команда не выбрана");
      return;
    }

    console.log("Отправка заявки на сервер для командного участия", {
      tournamentId: id,
      teamId: selectedTeam.id,
      teamName: selectedTeam.name,
      userId: "currentUserId",
    });

    setIsApplied(true);
    setIsModalOpen(false);
    setSelectedTeam(null);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedTeam(null);
  };

  // Function to render a single round with proper spacing
  const renderRound = (round) => {
    const matches = round.matches;
    return (
      <div key={round.id} className="bracket-column">
        <h3 className="bracket-column__title">Раунд {round.letter}</h3>
        <div className="bracket-column__matches">
          {matches.map((match) => (
            <div key={match.id} className="bracket-match-wrapper">
              <MatchCard match={match} className="match-card--bracket" />
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render the final match
  const renderFinal = () => {
    return (
      <div className="bracket-column">
        <h3 className="bracket-column__title">Финал</h3>
        <div className="bracket-column__matches">
          <div className="bracket-match-wrapper">
            <MatchCard
              match={tournament.final}
              className="match-card--bracket"
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="tournament-page">
      <div className="tournament-page__header">
        <img className="avatar-uploader" src={tournament?.img ?? ""} alt="" />
        <div className="tournament-page__header-left">
          <p>{tournament.date}</p>
          <TitleH2
            style="aboutgame__header-title"
            title={tournament?.title ?? "Название неизвестно"}
          />
          <p className={`tournament-page__status status--${tournament.status}`}>
            {getTournamentStatus(tournament.status)}
          </p>
        </div>

        <div className="tournament-page__header-right">
          <SubmitButton
            text={isApplied ? "Отменить заявку" : "Подать заявку"}
            onClick={handleApplyClick}
            // disabled={tournament.status !== "open" || isApplied}
            // isSent={isApplied}
          />
        </div>
      </div>
      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
      <div className="tab-content">
        {activeTab === "overview" && (
          <div className="tournament-page__overview">
            <div className="tournament-page__overview-section">
              <h3 className="tournament-page__overview-title">Описание</h3>
              <p className="tournament-page__overview-description">
                {tournament.description || "Описание отсутствует"}
              </p>
            </div>
            <div className="tournament-page__overview-highlights">
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">
                  Призовой фонд
                </h4>
                <p className="tournament-page__overview-card-content tournament-page__overview-prize">
                  {tournament.prize_fund
                    ? `${tournament.prize_fund.toLocaleString()} ₽`
                    : "Не указан"}
                </p>
              </div>
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">
                  Организатор
                </h4>
                <Link
                  to={`/profile/${tournament.manager?.id || 0}`}
                  className="tournament-page__overview-organizer"
                >
                  <img
                    src={
                      tournament.manager?.avatar ||
                      "/src/images/default-avatar.png"
                    }
                    alt="Organizer avatar"
                    className="tournament-page__overview-organizer-avatar"
                  />
                  <span className="tournament-page__overview-organizer-name">
                    {tournament.manager?.name || "Неизвестно"}
                  </span>
                </Link>
              </div>
              <div className="tournament-page__overview-card">
                <h4 className="tournament-page__overview-card-title">
                  Контакты
                </h4>
                <p className="tournament-page__overview-card-content">
                  {tournament.contact ? (
                    <a
                      href={`https://t.me/${tournament.contact.replace(
                        "@",
                        ""
                      )}`}
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
                  className={`stage-filter__button ${
                    activeStage === stage.id
                      ? "stage-filter__button--active"
                      : ""
                  }`}
                  onClick={() => setActiveStage(stage.id)}
                >
                  {stage.label}
                </button>
              ))}
            </div>

            {activeStage === "group" && tournament.has_groupstage && (
              <div className="tournament-stage">
                <div className="tournament-stage__groups-container">
                  {tournament.group_stage.groups.map((group) => (
                    <div key={group.id} className="tournament-stage__group">
                      <h3 className="tournament-stage__title">
                        Группа {group.letter}
                      </h3>
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
                          const entity = row.team || row.user;
                          const linkTo = row.team
                            ? `/team/${entity.id}`
                            : `/profile/${entity.id}`;
                            const points = row.wins * 2 + row.draws;
                          return (
                            <div
                              key={row.id}
                              className={`standings-row ${getRowClass(
                                index,
                                group.group_rows.length
                              )}`}
                            >
                              <span>{row.place}</span>
                              <Link to={linkTo} className="standings-entity">
                                <img
                                  src={entity.avatar}
                                  alt="avatar"
                                  className="entity-avatar"
                                />
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

            {activeStage === "playoff" && (
              <div className="tournament-bracket">
                {tournament.playoff_stage.rounds.map((round) =>
                  renderRound(round)
                )}
                {renderFinal()}
              </div>
            )}
            {activeStage === "final" && (
               <MatchCard key={tournament.final.id} match={tournament.final} />
            )}
          </>
        )}

        {activeTab === "matches" && (
          <>
            <div className="stage-filter">
              {stageFilters.map((stage) => (
                <button
                  key={stage.id}
                  className={`stage-filter__button ${
                    activeStage === stage.id
                      ? "stage-filter__button--active"
                      : ""
                  }`}
                  onClick={() => setActiveStage(stage.id)}
                >
                  {stage.label}
                </button>
              ))}
            </div>

            {activeStage === "group" && tournament.has_groupstage && (
              <div className="tournament-stage">
                {tournament.group_stage.groups.map((group) => (
                  <div key={group.id} className="tournament-stage__group">
                    <h3 className="tournament-stage__title">
                      Группа {group.letter}
                    </h3>
                    <div className="tournament-stage__matches">
                      {group.matches.map((match) => (
                        <MatchCard key={match.id} match={match} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {activeStage === "playoff" && (
              <div className="tournament-stage">
                {tournament.playoff_stage.rounds.map((round) => (
                  <div key={round.id} className="tournament-stage__group">
                    <h3 className="tournament-stage__title">
                      Раунд {round.letter}
                    </h3>
                    <div className="tournament-stage__matches">
                      {round.matches.map((match) => (
                        <MatchCard key={match.id} match={match} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {activeStage === "final" && (
              <MatchCard key={tournament.final.id} match={tournament.final} />
            )}
          </>
        )}

        {activeTab === "participants" && (
          <RoundCards
            users={tournament.participants}
            isRequest={false}
            isTeam={false}
          />
        )}

        {activeTab === "prizes" &&
          (tournament.status === "completed" ? (
            <div className="tournament-page__prizes">
              <div className="tournament-page__prizes-header">
                <span>№</span>
                <span>Ник</span>
                <span>Приз</span>
              </div>
              {resultPlaces.map((team) => (
                <div className="tournament-page__prizes-row" key={team.id}>
                  <span>{team.place}</span>
                  <Link
                    to={`/profile/${team.id}`}
                    className="tournament-page__team-link"
                  >
                    <img
                      src={team.avatar}
                      alt="avatar"
                      className="team-avatar"
                    />
                    {team.name}
                  </Link>
                  <span>{team.prize > 0 ? `${team.prize}₽` : "-"}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="tournament-page__not-completed">
              Турнир ещё не завершён. Таблица призов появится после окончания.
            </p>
          ))}
      </div>
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <TitleH2 title="Выберите команду" />
        <div className="modal-content__teams">
          <RoundCards
            style="modal"
            users={commands}
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
