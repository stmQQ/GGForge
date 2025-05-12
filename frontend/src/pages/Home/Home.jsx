// import Coll from "../../components/Collapse/Collapse.jsx";
import "./home.scss";
import Card from "../../components/Card/Card";
import GamesMain from "../../components/Games/GamesMain.jsx";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import Tournaments from "../../components/Tournaments/Tournaments.jsx";
import Footer from "../../components/Footer/Footer.jsx";
import { tournaments } from "../../helpers/tournamentsList";
// import Header from "../../components/Header/Header.jsx";

export default function Home() {
  return (
    <div className="home">
      {/* <Header /> */}
      <div className="home__intro">
        <h1 className="home__title">GGForge</h1>
        <p className="home__description">
          Здесь рождаются турниры для игроков, стремящихся к победе, и для
          организаторов, ищущих вызов и вдохновение.{" "}
          <span className="home__highlight">GGForge</span> — это сообщество,
          объединенное страстью к киберспорту и желанием создавать уникальные
          игровые события.
        </p>
      </div>
      <Card
        text="Оттачивай мастерство, собирай награды и погружайся в мир киберспорта!"
        link="/games"
        linkText="Найти турнир"
        image="src/images/Ghostrunner.png"
      />
      <TitleH2 title="Просмотр игр" style="indent"/>
      <GamesMain />
      <Card
        reverse={true}
        text="Создай комунду мечты: твой формат, твои правила, твои участники!"
        link="/teams"
        linkText="Создать команду"
        image="src/images/sova.png"
      />
      <TitleH2 title="Популярные турниры" style="indent"/>
      <Tournaments array={tournaments}/>
      <Footer />
    </div>
  );
}
