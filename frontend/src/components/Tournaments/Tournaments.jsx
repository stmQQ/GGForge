import Tournament from "./Tournament";
import "./tournaments.scss";
import { API_URL } from "../../constants";

export default function Tournaments({ array, modifier = "" }) {
  return (
    <div>
      <ul className={`tournaments ${modifier}`}>
        {array.map((t) => {
          return <Tournament key={t.id} id={t.id} img={t.img} title={t.title} date={displayLocalTime(t.date)} inf={t.inf} />;
        })}
      </ul>
    </div>
  );
}

const displayLocalTime = (utcTime) => {
  const utcDate = new Date(utcTime);
  return utcDate.toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' });
};