import { Link } from "react-router-dom";
import "./tournaments.scss";

export default function Game({ id, title, img, date, inf }) {
  return (
    <li className="tournament">
      {/* <a href="./project-paasd"> */}
      <Link to={`/tournament/${id}`}>
        <img src={img} alt={title} className="tournament__img" />
        <p className="tournament__date">{date}</p>
        <h3 className="tournament__title">{title}</h3>
        <p className="tournament__inf">{inf}</p>
      {/* </a> */}
      </Link>
    </li>
  );
}
