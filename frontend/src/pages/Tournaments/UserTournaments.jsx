import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./userTournaments.scss";
import { getParticipantTournaments, getCreatorTournaments } from "../../api/tournaments";
import { API_URL } from "../../constants";
import TitleH2 from "../../components/TitleH2/TitleH2";
import Tournaments from "../../components/Tournaments/Tournaments";

export default function UserTournaments() {
  const location = useLocation();
  const navigate = useNavigate();
  const [tournamentFilter, setTournamentFilter] = useState("open");
  const [organizerFilter, setOrganizerFilter] = useState("manager");
  const [tournaments, setTournaments] = useState([]);
  const [error, setError] = useState("");

  // Чтение параметров из URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tournament = params.get("tournament") || "open";
    const organizer = params.get("organizer") || "manager";
    setTournamentFilter(tournament);
    setOrganizerFilter(organizer);
  }, [location.search]);

  // Обновление URL при изменении фильтров
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tournament", tournamentFilter);
    params.set("organizer", organizerFilter);
    navigate(`${location.pathname}?${params.toString()}`, { replace: true });
  }, [tournamentFilter, organizerFilter, navigate, location.pathname]);

  // Загрузка турниров
  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const apiCall = organizerFilter === "manager" ? getCreatorTournaments : getParticipantTournaments;
        const res = await apiCall();
        setTournaments(
          res.data.map((t) => ({
            id: t.id,
            img: t.banner_url ? `${API_URL}/${t.banner_url}` : `${API_URL}/static/tournaments/default/trnt_${t.game.title.replace(/\s+/g, '')}.png`,
            title: t.title,
            status: t.status,
            date: t.start_time,
            inf: `Призовой фонд: ${t.prize_fund || "0"} ₽`,
          }))
        );
        setError("");
      } catch (err) {
        setError(err.response?.data?.msg);
      }
    };
    fetchTournaments();
  }, [organizerFilter]);

  // Фильтрация турниров по статусу
  const filteredTournaments = tournaments.filter(
    (tournament) => tournament.status === tournamentFilter
  );

  return (
    <div className="user-tournaments">
      <TitleH2 title="Ваши турниры" style="indent" />
      {error && <div className="error-message">{error}</div>}
      <div className="user-tournaments__filters">
        <div className="user-tournaments__filter">
          <select
            value={tournamentFilter}
            onChange={(e) => setTournamentFilter(e.target.value)}
          >
            <option value="open">Предстоящие</option>
            <option value="ongoing">Текущие</option>
            <option value="completed">Завершённые</option>
            <option value="cancelled">Отменённые</option>
          </select>
        </div>
        <div className="user-tournaments__filter">
          <select
            value={organizerFilter}
            onChange={(e) => setOrganizerFilter(e.target.value)}
          >
            <option value="manager">Организатор</option>
            <option value="participant">Участник</option>
          </select>
        </div>
      </div>

      <div className="user-tournaments__list">
        {filteredTournaments.length > 0 ? (
          <Tournaments array={filteredTournaments} />
        ) : (
          <p className="user-tournaments__empty">
            Нет турниров по выбранным параметрам.
          </p>
        )}
      </div>
    </div>
  );
}