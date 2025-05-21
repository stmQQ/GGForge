import { useState, useEffect } from 'react';
import './home.scss';
import Card from '../../components/Card/Card';
import GamesMain from '../../components/Games/GamesMain.jsx';
import TitleH2 from '../../components/TitleH2/TitleH2.jsx';
import Tournaments from '../../components/Tournaments/Tournaments.jsx';
import Footer from '../../components/Footer/Footer.jsx';
import { API_URL } from '../../constants.js';
import { getNearestTournaments } from '../../api/tournaments';

export default function Home() {
  const [tournaments, setTournaments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTournaments() {
      try {
        setIsLoading(true);
        const response = await getNearestTournaments();
        setTournaments(
          response.data.data.map((t) => ({
            id: t.id,
            img: `${API_URL}/${t.banner_url}`,
            title: t.title,
            date: t.start_time,
            inf: `Призовой фонд: ${t.prize_fund}₽` || '',
          }))
        );
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }
    fetchTournaments();
  }, []);

  if (isLoading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;
  // if (tournaments.length === 0) return <div>Ближайшие турниры отсутствуют</div>;

  return (
    <div className="home">
      <div className="home__intro">
        <h1 className="home__title">GGForge</h1>
        <p className="home__description">
          Здесь рождаются турниры для игроков, стремящихся к победе, и для
          организаторов, ищущих вызов и вдохновение.{' '}
          <span className="home__highlight">GGForge</span> — это сообщество,
          объединенное страстью к киберспорту и желанием создавать уникальные
          игровые события.
        </p>
      </div>
      <Card
        text="Оттачивай мастерство, собирай награды и погружайся в мир киберспорта!"
        link="/games"
        linkText="Найти турнир"
        image={`${API_URL}/static/general/Ghostrunner.png`}
      />
      <TitleH2 title="Просмотр игр" style="indent" />
      <GamesMain limit={6} />
      <Card
        reverse={true}
        text="Создай команду мечты: твой формат, твои правила, твои участники!"
        link="/teams"
        linkText="Создать команду"
        image={`${API_URL}/static/general/Sova.png`}
      />
      <TitleH2 title="Ближайшие турниры" style="indent" />
      {tournaments.length === 0 ? <p>Нет предстоящих турниров</p> :
        <Tournaments array={tournaments} />}
      <Footer />
    </div>
  );
}