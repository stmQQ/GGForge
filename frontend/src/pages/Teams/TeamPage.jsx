import { useParams } from "react-router-dom";
import { useState } from "react";

import TitleH2 from "../../components/TitleH2/TitleH2";
import TabSwich from "../../components/TabSwitch/TabSwith";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";

const team = {
  id: 0,
  avatar: "/src/images/game1.jpg",
  name: "команда 1",
  description: "sagggg JKHCVBJG iueirybv xmsamadj",
  //   description: "sagggg JKHCVBJG iueirybv xmsamadj",
  description: "",
  participants: [
    { id: 0, avatar: "/src/images/game1.jpg", name: "gg" },
    { id: 1, avatar: "/src/images/game1.jpg", name: "Оля" },
  ],
};
const tabs = [
  { id: "information", label: "Информация" },
  { id: "participants", label: "Участники" },
];

export default function TeamPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("information");
  return (
    <div>
      {/* <h1>Страница команды</h1> */}
      <div className="profile profile__header">
        {/* <p>ID команды: {id}</p> */}
        <div className="profile__avatar">
          <img
            src={team.avatar}
            alt="avatar"
            className="profile__avatar-image"
          />
        </div>
        <TitleH2 title={team.name} />
      </div>
      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      <div className="tab-content">
        {activeTab === "information" && (
          <p>
            {team.description
              ? team.description
              : "Организатор не указал информацию"}
          </p>
        )}
        {activeTab === "participants" && (
          <RoundCards users={team.participants} isRequest={false} isTeam={false} />
        )}
      </div>
    </div>
  );
}
