import { useState, useEffect } from 'react';
import Game from './Game';
import './gamesMain.scss';
import { getGames } from '../../api/games';
import { API_URL } from '../../constants';

export default function GamesMain({ style = '', onSelectGame, query = '', limit = 0 }) {
  const [games, setGames] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchGames() {
      try {
        const response = await getGames();
        const data = response.data.map(game => ({
          ...game,
          image_path: game.image_path ? `${API_URL}/${game.image_path}` : null
        }));
        setGames(data);
        setIsLoading(false);
      } catch (err) {
        setError(err.response?.data?.msg || 'Ошибка загрузки игр');
        setIsLoading(false);
      }
    }
    fetchGames();
  }, []);

  const filteredGames = games.filter((game) =>
    game.title.toLowerCase().includes(query.toLowerCase())
  );

  // Применяем limit: если 0, показываем все, иначе обрезаем до limit
  const displayedGames = limit === 0 ? filteredGames : filteredGames.slice(0, limit);

  if (isLoading) return <div className="games__loading">Загрузка...</div>;
  if (error) return <div className="games__error">{error}</div>;

  return (
    <ul className={`games ${style}`}>
      {displayedGames.length > 0 ? (
        displayedGames.map((game) => (
          <Game
            key={game.id}
            id={game.id}
            title={game.title}
            img={game.image_path}
            onClick={(e) => {
              if (onSelectGame) {
                e.preventDefault();
                onSelectGame(game);
              }
            }}
          />
        ))
      ) : (
        <div className="games__empty">Ничего не найдено</div>
      )}
    </ul>
  );
}