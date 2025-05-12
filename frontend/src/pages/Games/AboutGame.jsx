import { useParams } from "react-router-dom";
import { useState } from "react";

import { games } from "../../helpers/gamesList";
import { allTournaments } from "../../helpers/tournamentsList";
import TitleH2 from "../../components/TitleH2/TitleH2";
import "./aboutGame.scss";
import TabSwich from "../../components/TabSwitch/TabSwith";
import Tournaments from "../../components/Tournaments/Tournaments";

export default function AboutGame() {
  const { id } = useParams(); // Получаем id игры из URL
  const gameInfo = games.find((game) => game.id.toString() === id); // Преобразование id в строку для сравнения
  const [activeTab, setActiveTab] = useState("review");
  const tabs = [
    { id: "review", label: "Обзор" },
    { id: "tournament", label: "Турниры" },
  ];

  const [tournamentFilter, setTournamentFilter] = useState("open");

  const filteredTournaments = allTournaments.filter(
    (t) => t.status === tournamentFilter
  );

  if (!gameInfo) {
    return <p>Игра не найдена.</p>; // Сообщение об ошибке, если игра не найдена
  }

  return (
    <div className="aboutgame">
      <div className="aboutgame__header">
        <img
          className="aboutgame__header-image"
          src={gameInfo?.img ?? ""}
          alt=""
        />
        <TitleH2
          style="aboutgame__header-title"
          title={gameInfo?.title ?? "Название неизвестно"}
        />
      </div>
      <div className='aboutgame__tab'>
      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
      </div>

      {activeTab === "tournament" && (
        <>
          <div className="aboutgame__filter">
            <select
              value={tournamentFilter}
              onChange={(e) => setTournamentFilter(e.target.value)}
            >
              <option value="open">Предстоящие</option>
              <option value="ongoing">Текущие</option>
              <option value="completed">Завершённые</option>
            </select>
          </div>

          <div className="aboutgame__tournaments">
            {filteredTournaments.length > 0 ? (
              <Tournaments array={filteredTournaments} />
            ) : (
              <p>Нет турниров по выбранному фильтру.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
