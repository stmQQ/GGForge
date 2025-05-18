import "./matchCard.scss";
import { useState, useContext } from "react";
import Modal from "../../components/Modal/Modal.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import DetailsIcon from "../../icons/box-arrow-up-right.svg?react";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import ExternalLinkButton from "../Button/ExternalLinkButton.jsx";
import SubmitButton from "../Button/SubmitButton.jsx";
import TextInput from "../InputFields/TextInput.jsx";
import { API_URL } from "../../constants.js";
import { AuthContext } from "../../context/AuthContext.jsx";
import { startMatch, completeMap } from "../../api/tournaments.js";

export default function MatchCard({ match, className }) {
  const getMatchStatus = (status) => {
    switch (status) {
      case "scheduled":
        return { text: "Предстоящий", class: "status--upcoming" };
      case "ongoing":
        return { text: "Текущий", class: "status--ongoing" };
      case "completed":
        return { text: "Завершён", class: "status--completed" };
      default:
        return { text: "Отмене", class: "status--unknown" };
    }
  };

  const { isAdmin } = useContext(AuthContext);
  const [isCreator, setCreator] = useState(match.creator === match.user_id);
  const [canBeStarted, setCanBeStarted] = useState(match.participant1?.id || match.participant2?.id)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [isFinished, setIsFinished] = useState(false); // Состояние для кнопки "Завершить матч"
  const [mapResults, setMapResults] = useState(
    match.maps?.map((map) => ({
      mapId: map.id,
      winnerId: null, // Выбранный победитель
      externalUrl: map.external_url || "", // Ссылка на игру
    })) || []
  );
  // setCreator(match.creator === match.user_id)
  // console.log(match)
  if (match.participant1?.user) {
    match.participant1 = match.participant1.user
    match.participant1.avatar = `${API_URL}/${match.participant1.avatar}`
  }
  if (match.participant2?.user) {
    match.participant2 = match.participant2.user
    match.participant2.avatar = `${API_URL}/${match.participant2.avatar}`
  }

  console.log(match)

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };
  // Компонент для блока с победителями
  const renderWinners = () => (
    <div className="match-details-modal__winners">
      {match.maps?.map((map, index) => {
        const winner =
          map.winner_id === match.participant1.id.toString()
            ? match.participant1
            : map.winner_id === match.participant2.id.toString()
              ? match.participant2
              : null;
        return (
          <div key={index} className="winner-block">
            <div className="winner-block-left">
              <div className="winner-block__title">Победитель</div>
              {winner && (
                <div className="winner-block__details">
                  <img
                    src={winner.avatar || "1.png"}
                    alt="winner avatar"
                    className="winner-block__avatar"
                  />
                  <span className="winner-block__name">{winner.name}</span>
                </div>
              )}
            </div>
            <div className="winner-block-right">
              <ExternalLinkButton
                text="Посмотреть матч"
                href={map.external_url}
                disabled={!map.external_url}
              />
            </div>
          </div>
        );
      })}
    </div>
  );



  // Компонент для выбора победителя и ссылки
  const renderOngoingMaps = () => (
    <div className="match-details-modal__ongoing">

      {match.maps?.map((map, index) => {
        const result = mapResults[index];
        return (
          <div key={index} className="winner-block ongoin-maps">
            {/* <div className="ongoing-block__title">Карта {index + 1}</div> */}
            <div className="ongoing-block__participants">
              <label className="winner-block__details">
                <input
                  type="radio"
                  name={`winner-${map.id}`}
                  value={match.participant1.id}
                  checked={result.winnerId === match.participant1.id.toString()}
                  onChange={() =>
                    updateMapResult(index, "winnerId", match.participant1.id.toString())
                  }
                  disabled={isFinished}
                />
                <img
                  src={match.participant1.avatar || "2.png"}
                  alt="avatar"
                  className="winner-block__avatar"
                />
                <span>{match.participant1.name}</span>
              </label>
              <label className="winner-block__details">
                <input
                  type="radio"
                  name={`winner-${map.id}`}
                  value={match.participant2.id}
                  checked={result.winnerId === match.participant2.id.toString()}
                  onChange={() =>
                    updateMapResult(index, "winnerId", match.participant2.id.toString())
                  }
                  disabled={isFinished}
                />
                <img
                  src={match.participant2.avatar || "3.png"}
                  alt="avatar"
                  className="winner-block__avatar"
                />
                <span>{match.participant2.name}</span>
              </label>
            </div>
            <TextInput
              id={`url-${map.id}`}
              // label="Ссылка на игру"
              value={result.externalUrl}
              onChange={(e) => updateMapResult(index, "externalUrl", e.target.value)}
              placeholder="Введите ссылку на игру"
              disabled={isFinished}
            />
          </div>
        );
      })}
      <div className="match-details-modal__finish">
        <SubmitButton
          text="Завершить матч"
          onClick={() => handleFinishMatch(match.tournament_id, match.id)}
          disabled={isFinished || !mapResults.every((result) => result.winnerId)}
          isSent={isFinished}
        />
      </div>
    </div>
  );

  // Обновление результатов карты
  const updateMapResult = (index, field, value) => {
    const updatedResults = [...mapResults];
    updatedResults[index] = { ...updatedResults[index], [field]: value };
    setMapResults(updatedResults);
  };

  // Обработчик для кнопки "Начать"
  const handleStartMatch = async (tournamentId, matchId) => {
    try {
      await startMatch(tournamentId, matchId);
      setIsStarted(true);
    } catch (error) {
      console.error('Ошибка при старте матча:', error);
      throw error;
    }
  };

  // Обработчик для кнопки "Завершить матч"
  const handleFinishMatch = async (tournamentId, matchId) => {
    try {
      for (const res of mapResults) {
        if (res.winnerId) {
          // console.log(tournamentId, matchId, res.mapId, res.winnerId)
          await completeMap(tournamentId, matchId, res.mapId, res.winnerId)
        }
      }
      setIsFinished(true)
    } catch (err) {
      throw new Error(err.response?.data?.msg || "Ошибка при завершении матча");
    }
  };
  return (
    <div className={`match-card ${className || ""}`}>
      <div className="match-card__header">
        <div className="match-card__header-left">
          <span
            className={`match-card__status ${getMatchStatus(match.status).class
              }`}
          >
            {getMatchStatus(match.status).text}
          </span>
          <span className="match-card__number">Матч {match.number}</span>
        </div>
        <div className="match-card__header-right">
          <span className="match-card__format">
            {match.format.toUpperCase()}
          </span>
          <ModalButton
            text={<DetailsIcon />}
            onClick={openModal}
            style="button__svg"
          />
        </div>
      </div>
      <div className="match-card__teams">
        <div className="match-card__team">
          <img
            src={match.participant1?.avatar || "4.png"}
            alt="avatar"
            className="match-card__avatar"
          />
          <span className="match-card__name">{match.participant1?.name}</span>
          <span className="match-card__score">{match.score1}</span>
        </div>
        <div className="match-card__team">
          <img
            src={match.participant2?.avatar || "5.png"}
            alt="avatar"
            className="match-card__avatar"
          />
          <span className="match-card__name">{match.participant2?.name}</span>
          <span className="match-card__score">{match.score2}</span>
        </div>
      </div>
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <div className="match-details-modal">
          <TitleH2 title={`Матч ${match.number}`} />
          <div className="match-details-modal__header">
            <span
              className={`match-card__status ${getMatchStatus(match.status).class
                }`}
            >
              {getMatchStatus(match.status).text}
            </span>
            <span className="match-card__format">
              {match.format.toUpperCase()}
            </span>
          </div>
          <div className="match-details-modal__teams">
            <p>{match.participant1?.name}</p>
            <img
              src={match.participant1?.avatar || "6.png"}
              alt="avatar"
              className="match-details-modal__avatar"
            />
            <span className="match-details-modal__score">
              {match.score1} : {match.score2}
            </span>
            <img
              src={match.participant2?.avatar || "7.png"}
              alt="avatar"
              className="match-details-modal__avatar"
            />
            <p>{match.participant2?.name}</p>
          </div>
          {(isAdmin || isCreator) && canBeStarted && match.status === "scheduled" ? (
            <div className="match-details-modal__start">
              <SubmitButton
                text="Начать"
                onClick={() => handleStartMatch(match.tournament_id, match.id)}
                disabled={isStarted}
                isSent={isStarted}
              />
            </div>
          ) : (isAdmin || isCreator) && match.status === "ongoing" ? (
            renderOngoingMaps()
          ) : (
            renderWinners()
          )}
        </div>
      </Modal>
    </div>
  );
}