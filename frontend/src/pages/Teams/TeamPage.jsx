import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { getTeam } from "../../api/teams";
import { API_URL } from "../../constants.js";
import TitleH2 from "../../components/TitleH2/TitleH2";
import TabSwitch from "../../components/TabSwitch/TabSwitch.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";

const tabs = [
  { id: "information", label: "Информация" },
  { id: "participants", label: "Участники" },
];

export default function TeamPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("information");
  const [team, setTeam] = useState(null);
  const [error, setError] = useState("");

  // Формирование URL для логотипа
  const getLogoUrl = (logoPath) =>
    logoPath ? `${API_URL}${logoPath}` : `${API_URL}/static/team_logos/default.png`;

  // Формирование URL для аватара участника
  const getAvatarUrl = (avatar) =>
    avatar ? `${API_URL}${avatar}` : `${API_URL}/static/avatars/default.png`;

  // Загрузка данных команды
  const fetchTeam = async () => {
    try {
      const res = await getTeam(id);
      const teamData = res.data;
      setTeam({
        id: teamData.id,
        name: teamData.title,
        avatar: getLogoUrl(teamData.logo_path),
        description: teamData.description,
        participants: (teamData.players || []).map((player) => ({
          id: player.id,
          name: player.name,
          avatar: getAvatarUrl(player.avatar),
        })),
      });
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка загрузки данных команды");
    }
  };

  // Загрузка данных при монтировании
  useEffect(() => {
    fetchTeam();
  }, [id]);

  if (error) {
    return <div className="team__error">{error}</div>;
  }

  if (!team) {
    return <div>Загрузка...</div>;
  }

  return (
    <div>
      <div className="profile profile__header">
        <div className="profile__avatar">
          <img
            src={team.avatar}
            alt="team avatar"
            className="profile__avatar-image"
          />
        </div>
        <TitleH2 title={team.name} />
      </div>
      <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      <div className="tab-content">
        {activeTab === "information" && (
          <p>
            {team.description
              ? team.description
              : "Организатор не указал информацию"}
          </p>
        )}
        {activeTab === "participants" && (
          <RoundCards
            users={team.participants}
            isRequest={false}
            isTeam={false}
          />
        )}
      </div>
    </div>
  );
}