/* eslint-disable react/prop-types */
import "./matchCard.scss";
import { useState, useContext, useEffect } from "react";
import Modal from "../../components/Modal/Modal.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import DetailsIcon from "../../icons/box-arrow-up-right.svg?react";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import ExternalLinkButton from "../Button/ExternalLinkButton.jsx";
import SubmitButton from "../Button/SubmitButton.jsx";
import TextInput from "../InputFields/TextInput.jsx";
import { API_URL } from "../../constants.js";
import { AuthContext } from "../../context/AuthContext.jsx";
import { startMatch, completeMap, addHighlightUrl } from "../../api/tournaments.js";

export default function MatchCard({ match, className, onFinish, final_match = false }) {
  const getMatchStatus = (status) => {
    switch (status) {
      case "scheduled":
        return { text: "Предстоящий", class: "status--upcoming" };
      case "ongoing":
        return { text: "Текущий", class: "status--ongoing" };
      case "completed":
        return { text: "Завершён", class: "status--completed" };
      default:
        return { text: "Отменен", class: "status--unknown" };
    }
  };

  const { isAdmin } = useContext(AuthContext);
  const [currentMatch, setCurrentMatch] = useState(match)

  useEffect(() => {
    if (match && match !== undefined)
      setCurrentMatch(match);
  }, []);

  useEffect(() => {
    if (currentMatch?.maps) {
      const results = currentMatch.maps.map((map) => ({
        mapId: map.id,
        winnerId: map.winner_id || null,
        externalUrl: map.external_url || "",
      }));
      setMapResults(results);
    }
  }, [currentMatch]);

  // console.log(currentMatch, match)
  const [isCreator, setCreator] = useState(currentMatch.creator === currentMatch.user_id);
  const [canBeStarted, setCanBeStarted] = useState(currentMatch.participant1?.id || currentMatch.participant2?.id)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [isFinished, setIsFinished] = useState(false); // Состояние для кнопки "Завершить матч"
  const [mapResults, setMapResults] = useState(
    currentMatch.maps?.map((map) => ({
      mapId: map.id,
      winnerId: null, // Выбранный победитель
      externalUrl: map.external_url || "", // Ссылка на игру
    })) || []
  );
  const [highlightUrl, setHighlightUrl] = useState("");

  if (currentMatch.participant1?.user) {
    currentMatch.participant1 = currentMatch.participant1.user
    currentMatch.participant1.avatar = `${API_URL}/${currentMatch.participant1.avatar}`
  }
  if (currentMatch.participant2?.user) {
    currentMatch.participant2 = currentMatch.participant2.user
    currentMatch.participant2.avatar = `${API_URL}/${currentMatch.participant2.avatar}`
  }
  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };
  // Компонент для блока с победителями
  const renderWinners = () => (
    <div className="match-details-modal__winners">
      {currentMatch.maps?.map((map, index) => {
        const winner =
          map.winner_id === currentMatch.participant1.id.toString()
            ? currentMatch.participant1
            : map.winner_id === currentMatch.participant2.id.toString()
              ? currentMatch.participant2
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

      {currentMatch.maps?.map((map, index) => {
        const result = mapResults[index];
        return (
          <div key={index} className="winner-block ongoin-maps">
            <div className="ongoing-block__title">Карта {index + 1}</div>
            <div className="ongoing-block__participants">
              <label className="winner-block__details">
                <input
                  type="radio"
                  name={`winner-${map.id}`}
                  value={currentMatch.participant1.id}
                  checked={result?.winnerId?.toString() === currentMatch.participant1?.id?.toString() || false}
                  onChange={() =>
                    updateMapResult(index, "winnerId", currentMatch.participant1.id.toString())
                  }
                  disabled={isFinished}
                />
                <img
                  src={currentMatch.participant1.avatar || "2.png"}
                  alt="avatar"
                  className="winner-block__avatar"
                />
                <span>{currentMatch.participant1.name}</span>
              </label>
              <label className="winner-block__details">
                <input
                  type="radio"
                  name={`winner-${map.id}`}
                  value={currentMatch.participant2.id}
                  checked={result?.winnerId?.toString() === currentMatch.participant2?.id?.toString() || false}
                  onChange={() =>
                    updateMapResult(index, "winnerId", currentMatch.participant2.id.toString())
                  }
                  disabled={isFinished}
                />
                <img
                  src={currentMatch.participant2.avatar || "3.png"}
                  alt="avatar"
                  className="winner-block__avatar"
                />
                <span>{currentMatch.participant2.name}</span>
              </label>
            </div>
            <TextInput
              id={`url-${map.id}`}
              // label="Ссылка на игру"
              value={result?.externalUrl}
              onChange={(e) => updateMapResult(index, "externalUrl", e.target.value)}
              placeholder="Введите ссылку на игру"
              disabled={isFinished}
            />
          </div>
        );
      })}

      {final_match == true && (
        <TextInput
          id={`highlight-url-match-${match.id}`}
          value={highlightUrl}
          onChange={(e) => setHighlightUrl(e.target.value)}
          placeholder="Ссылка на самый яркий момент игры"
          disabled={isFinished}
        />
      )}

      <div className="match-details-modal__finish">
        <SubmitButton
          text="Завершить матч"
          onClick={() => handleFinishMatch(currentMatch.tournament_id, currentMatch.id, highlightUrl)}
          disabled={isFinished || mapResults.length == 0 || !mapResults.every((result) => result.winnerId)}
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
      const updated_data = await startMatch(tournamentId, matchId);
      setCurrentMatch(updated_data.data.match)
      setIsStarted(true);

    } catch (error) {
      console.error('Ошибка при старте матча:', error);
      throw error;
    }
  };

  // Обработчик для кнопки "Завершить матч"
  const handleFinishMatch = async (tournamentId, matchId, highlightUrl = '') => {
    try {
      let updated_response = null;
      for (const res of mapResults) {
        updated_response = await completeMap(tournamentId, matchId, res.mapId, res.winnerId || null);
      }
      if (highlightUrl) {
        await addHighlightUrl(tournamentId, highlightUrl);
      }
      setCurrentMatch(updated_response.data.match);
      setIsFinished(true);
      closeModal();
      // Вызываем onFinish для обновления родительского состояния
      onFinish(matchId, updated_response.data.match);
    } catch (err) {
      console.log(err)
      throw new Error(err.response?.data?.msg);
    }
  };

  return (
    <div className={`match-card ${className || ""}`}>
      <div className="match-card__header">
        <div className="match-card__header-left">
          <span
            className={`match-card__status ${getMatchStatus(currentMatch.status).class
              }`}
          >
            {getMatchStatus(currentMatch.status).text}
          </span>
          <span className="match-card__number">Матч {currentMatch.number}</span>
        </div>
        <div className="match-card__header-right">
          <span className="match-card__format">
            {currentMatch.format.toUpperCase()}
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
            src={currentMatch.participant1?.avatar || "4.png"}
            alt="avatar"
            className="match-card__avatar"
          />
          <span className="match-card__name">{currentMatch.participant1?.name}</span>
          <span className="match-card__score">{currentMatch.participant1_score}</span>
        </div>
        <div className="match-card__team">
          <img
            src={currentMatch.participant2?.avatar || "5.png"}
            alt="avatar"
            className="match-card__avatar"
          />
          <span className="match-card__name">{currentMatch.participant2?.name}</span>
          <span className="match-card__score">{currentMatch.participant2_score}</span>
        </div>
      </div>
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <div className="match-details-modal">
          <TitleH2 title={`Матч ${currentMatch.number}`} />
          <div className="match-details-modal__header">
            <span
              className={`match-card__status ${getMatchStatus(currentMatch.status).class
                }`}
            >
              {getMatchStatus(currentMatch.status).text}
            </span>
            <span className="match-card__format">
              {currentMatch.format.toUpperCase()}
            </span>
          </div>
          <div className="match-details-modal__teams">
            <p>{currentMatch.participant1?.name}</p>
            <img
              src={currentMatch.participant1?.avatar || "6.png"}
              alt="avatar"
              className="match-details-modal__avatar"
            />
            <span className="match-details-modal__score">
              {currentMatch.participant1_score} : {currentMatch.participant2_score}
            </span>
            <img
              src={currentMatch.participant2?.avatar || "7.png"}
              alt="avatar"
              className="match-details-modal__avatar"
            />
            <p>{currentMatch.participant2?.name}</p>
          </div>
          {(isAdmin || isCreator) && canBeStarted && currentMatch.status === "scheduled" ? (
            <div className="match-details-modal__start">
              <SubmitButton
                text="Начать"
                onClick={() => handleStartMatch(currentMatch.tournament_id, match.id)}
                disabled={isStarted}
                isSent={isStarted}
              />
            </div>
          ) : ((isAdmin || isCreator) && currentMatch.status === "ongoing") ? (
            renderOngoingMaps()
          ) : (
            renderWinners()
          )}
        </div>
      </Modal>
    </div>
  );
}