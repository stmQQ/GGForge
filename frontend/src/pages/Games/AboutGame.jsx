// src/pages/AboutGame/AboutGame.jsx
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { getGameById } from "../../api/games";
import { getTournamentsByGame } from "../../api/tournaments";
import { API_URL } from "../../constants";
import TitleH2 from "../../components/TitleH2/TitleH2";
import "./aboutGame.scss";
import TabSwitch from "../../components/TabSwitch/TabSwitch";
import Tournaments from "../../components/Tournaments/Tournaments";

export default function AboutGame() {
  const { id } = useParams();
  const [gameInfo, setGameInfo] = useState(null);
  const [tournaments, setTournaments] = useState([]);
  const [activeTab, setActiveTab] = useState("review");
  const [tournamentFilter, setTournamentFilter] = useState("open");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const tabs = [
    { id: "review", label: "Обзор" },
    { id: "tournament", label: "Турниры" },
  ];

  useEffect(() => {
    async function fetchData() {
      try {
        // Загрузка данных игры
        const gameResponse = await getGameById(id);
        setGameInfo({
          id: gameResponse.data.id,
          title: gameResponse.data.title,
          img: gameResponse.data.image_path
            ? `${API_URL}/${gameResponse.data.image_path}`
            : "",
        });

        // Загрузка турниров
        const tournamentsResponse = await getTournamentsByGame(id);
        console.log(tournamentsResponse);

        setTournaments(
          tournamentsResponse.data.map((tournament) => ({
            id: tournament.id,
            title: tournament.title,
            img: tournament.banner_url
              ? `${API_URL}/${tournament.banner_url}`
              : "",
            date: tournament.start_time,
            inf: `Призовой фонд: ${tournament.prize_fund || "0"} ₽`,
            status: tournament.status,
          }))

        );
        setIsLoading(false);
      } catch (err) {
        setError(err.response?.data?.msg || "Ошибка загрузки данных");
        setIsLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const filteredTournaments = tournaments.filter(
    (t) => t.status === tournamentFilter
  );

  if (isLoading) return <div>Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!gameInfo) return <p>Игра не найдена.</p>;

  return (
    <div className="aboutgame">
      <div className="aboutgame__header">
        <img
          className="aboutgame__header-image"
          src={gameInfo.img}
          alt={gameInfo.title}
          onError={(e) => (e.target.src = "")}
        />
        <TitleH2
          style="aboutgame__header-title"
          title={gameInfo.title}
        />
      </div>
      <div className="aboutgame__tab">
        <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
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
              <p>Нет турниров по выбранному фильтру</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}