import { useState } from "react";

import GamesMain from "../../components/Games/GamesMain.jsx";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import Search from "../../components/Search/Search.jsx";
export default function Games() {
  const [query, setQuery] = useState(""); // состояние для поиска

  return (
    <div>
      <TitleH2 title="Игры" style="indent" />
      <Search
        placeholder="Введите название игры"
        value={query}
        onChange={setQuery}
      />
      <GamesMain query={query}/>
    </div>
  );
}
