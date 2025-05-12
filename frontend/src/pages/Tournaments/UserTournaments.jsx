import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // useNavigate нужен
import "./userTournaments.scss";
import game1 from "../../images/game2.jpg";

import TitleH2 from "../../components/TitleH2/TitleH2";
import Tournaments from "../../components/Tournaments/Tournaments";

export default function UserTournaments() {
  const location = useLocation();
  const navigate = useNavigate();

  // Начальные значения — пока просто дефолтные
  const [tournamentFilter, setTournamentFilter] = useState("open");
  const [organizerFilter, setOrganizerFilter] = useState("manager");

  // При заходе на страницу — читаем параметры из URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tournament = params.get("tournament");
    const organizer = params.get("organizer");

    if (tournament) {
      setTournamentFilter(tournament);
    }
    if (organizer) {
      setOrganizerFilter(organizer);
    }
  }, [location.search]);

  // При изменении фильтров — обновляем URL
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tournament", tournamentFilter);
    params.set("organizer", organizerFilter);
    navigate(`${location.pathname}?${params.toString()}`, { replace: true });
  }, [tournamentFilter, organizerFilter, navigate, location.pathname]);

  const participantTournaments = [
    {
      id: 1,
      img: game1,
      title: "Турнир 1 уч",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 7,
      img: game1,
      title: "Турнир 1 уч",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 72,
      img: game1,
      title: "Турнир 1 уч",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 71,
      img: game1,
      title: "Турнир 1 уч",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 11,
      img: game1,
      title: "Турнир 1 уч",
      status: "cancelled",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 2,
      img: game1,
      title: "Турнир 2 уч",
      status: "ongoing",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 3,
      img: game1,
      title: "Турнир 3 уч",
      status: "completed",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
  ];

  const managerTournaments = [
    {
      id: 1,
      img: game1,
      title: "Турнир 1 орг",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 2,
      img: game1,
      title: "Турнир 2 орг",
      status: "ongoing",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 3,
      img: game1,
      title: "Турнир 3 орг",
      status: "completed",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
  ];

  const arrayTournaments =
    organizerFilter === "manager" ? managerTournaments : participantTournaments;

  const filteredTournaments = arrayTournaments.filter(
    (tournament) => tournament.status === tournamentFilter
  );

  return (
    <div className="user-tournaments">
      <TitleH2 title="Ваши турниры" style="indent" />
      <div className="user-tournaments__filters">
        <div className="user-tournaments__filter">
          <select
            value={tournamentFilter}
            onChange={(e) => setTournamentFilter(e.target.value)}
          >
            <option value="open">Предстоящие</option>
            <option value="ongoing">Текущие</option>
            <option value="completed">Завершённые</option>
            <option value="cancelled">Отмененные</option>
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
