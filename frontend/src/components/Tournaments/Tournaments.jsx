import Tournament from "./Tournament";
import "./tournaments.scss";
// import { tournaments } from "../../helpers/tournamentsList";

export default function Tournaments({array,  modifier = ""}) {
  return (
    <div>
      <ul className={`tournaments ${modifier}`}>
        {array.map((game) => {
          return <Tournament key={game.id} id={game.id} img={game.img} title={game.title} date={game.date} inf={game.inf}/>;
        })}
      </ul>
    </div>
  );
}
