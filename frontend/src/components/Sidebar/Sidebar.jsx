import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./sidebar.scss";

import logo from "../../images/logo.png";
import FriendsIcon from "../../icons/friends1.svg?react";
import GamesIcon from "../../icons/games1.svg?react";
import TeamsIcon from "../../icons/teams1.svg?react";
import TournamentIcon from "../../icons/tournament1.svg?react";
import HeadsetIcon from "../../icons/headset1.svg?react";
import Modal from "../Modal/Modal";
import TitleH2 from "../TitleH2/TitleH2";
import GamesMain from "../Games/GamesMain";
import TextInput from "../InputFields/TextInput";
import TextareaField from "../InputFields/TextareaField";
import SubmitButton from "../Button/SubmitButton";

export default function Sidebar({ isOpen, onClose }) {
  const [isTournamentModalOpen, setIsTournamentModalOpen] = useState(false);
  const [selectedGame, setSelectedGame] = useState(null);
  const [tournamentName, setTournamentName] = useState("");
  const [isSupportModalOpen, setIsSupportModalOpen] = useState(false);
  const [supportMessage, setSupportMessage] = useState("");
  const navigate = useNavigate();

  const handleCloseModal = () => {
    setIsTournamentModalOpen(false);
    setSelectedGame(null);
    setTournamentName("");
  };

  const handleGameSelect = (game) => {
    setSelectedGame(game);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    handleCloseModal();
    navigate("/newtournament", {
      state: {
        game: selectedGame,
        tournamentName: tournamentName,
      },
    });
  };

  return (
    <>
      <nav className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__logo">
          <Link to="/" className="sidebar__link" onClick={onClose}>
            <img src={logo} alt="Главная" loading="lazy" />
          </Link>
        </div>

        <div>
          <ul>
            <li>
              <Link to="/games" className="sidebar__link" onClick={onClose}>
                <GamesIcon
                  className="sidebar__icon"
                  aria-label="Найти турнир"
                />
              </Link>
            </li>
            <li>
              <Link to="/friends" className="sidebar__link" onClick={onClose}>
                <FriendsIcon className="sidebar__icon" aria-label="Друзья" />
              </Link>
            </li>
            <li>
              <Link to="/teams" className="sidebar__link" onClick={onClose}>
                <TeamsIcon className="sidebar__icon" aria-label="Команды" />
              </Link>
            </li>
            <li>
              <button
                className="sidebar__link"
                onClick={() => {
                  onClose();
                  setIsTournamentModalOpen(true);
                }}
              >
                <TournamentIcon
                  className="sidebar__icon"
                  aria-label="Создать турнир"
                />
              </button>
            </li>
          </ul>
        </div>

        <div className="sidebar__bottom">
          <button
            className="sidebar__link"
            onClick={() => {
              onClose();
              setIsSupportModalOpen(true);
            }}
          >
            <HeadsetIcon className="sidebar__icon" aria-label="Поддержка" />
          </button>
        </div>
      </nav>

      {isOpen && <div className="sidebar__overlay" onClick={onClose} />}

      <Modal isOpen={isTournamentModalOpen} onClose={handleCloseModal}>
        <TitleH2 title="Создать турнир" />
        {!selectedGame ? (
          <>
            <p className="modal__subtitle">Выберите игру:</p>
            <GamesMain style="modal" onSelectGame={handleGameSelect} />
          </>
        ) : (
          <form className="gameNickname__form" onSubmit={handleSubmit}>
            <TextInput
              id="tournamentName"
              label="Название турнира"
              value={tournamentName}
              onChange={(e) => setTournamentName(e.target.value)}
              placeholder="Введите название турнира"
            />
            <SubmitButton text="Создать турнир" />
          </form>
        )}
      </Modal>

      <Modal
        isOpen={isSupportModalOpen}
        onClose={() => setIsSupportModalOpen(false)}
      >
        <TitleH2 title="Поддержка" />
        <form
          className="support__form"
          onSubmit={(e) => {
            if (!supportMessage) {
              alert("Заявка отклонена. Ваш запрос пустой");
              return;
            }
            e.preventDefault();
            console.log("Сообщение в поддержку отправлено:", supportMessage);
            setIsSupportModalOpen(false);
            setSupportMessage("");
          }}
        >
          <TextareaField
            id="supportMessage"
            label="Ваш вопрос:"
            placeholder="Опишите проблему"
            value={supportMessage}
            onChange={(e) => setSupportMessage(e.target.value)}
          />
          <SubmitButton text="Отправить" />
        </form>
      </Modal>
    </>
  );
}
