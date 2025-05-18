import "./teams.scss";
import { useState, useEffect } from "react";
import {
  getUserTeams,
  getIncomingTeamInvites,
  createTeam,
  acceptTeamInvite,
  declineTeamInvite,
} from "../../api/teams"; // Импорт из teams.js
import { API_URL } from "../../constants.js";
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import TabSwitch from "../../components/TabSwitch/TabSwitch.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import CreateTeamForm from "../../components/CreateTeamForm/CreateTeamForm.jsx";

export default function Teams() {
  const [activeTab, setActiveTab] = useState("teams");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [teams, setTeams] = useState([]);
  const [invites, setInvites] = useState([]);
  const [error, setError] = useState("");

  // Формирование URL для логотипа
  const getLogoUrl = (logoPath) =>
    logoPath ? `${API_URL}/${logoPath}` : `${API_URL}/static/team_logos/default.png`;

  // Загрузка данных с сервера
  const fetchData = async () => {
    try {
      // Команды пользователя
      const teamsRes = await getUserTeams();
      console.log(teamsRes);
      const allTeams = [
        ...(teamsRes.data[0].member_teams || []),
      ].map((team) => ({
        id: team.id,
        name: team.title,
        avatar: getLogoUrl(team.logo_path),
      }));
      setTeams(allTeams);

      // Входящие приглашения
      const invitesRes = await getIncomingTeamInvites();
      setInvites(
        (invitesRes.data || []).map((invite) => ({
          id: invite.team_id,
          name: invite.team?.title || "Без названия",
          avatar: getLogoUrl(invite.team?.logo_path),
          requestId: invite.id,
        }))
      );
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка загрузки данных");
    }
  };

  // Создание команды
  const handleCreateTeam = async ({ teamName, description, logoFile }) => {
    try {
      await createTeam(teamName, description, logoFile);
      await fetchData();
      setIsModalOpen(false);
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка создания команды");
    }
  };

  // Ответ на приглашение
  const handleRespondInvite = async (requestId, action) => {
    try {
      if (action === "accept") {
        await acceptTeamInvite(requestId);
      } else if (action === "decline") {
        await declineTeamInvite(requestId);
      }
      await fetchData();
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка обработки приглашения");
    }
  };

  // Загрузка данных при монтировании
  useEffect(() => {
    fetchData();
  }, []);

  const tabs = [
    { id: "teams", label: "Ваши команды" },
    { id: "requests_teams", label: "Приглашения в команды" },
  ];

  return (
    <div>
      <div className="title-with-button">
        <TitleH2 title="Команды" style="indent" />
        <ModalButton
          text="Создать команду"
          onClick={() => setIsModalOpen(true)}
        />
      </div>

      {error && <div className="teams__error">{error}</div>}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <CreateTeamForm onSubmit={handleCreateTeam} />
      </Modal>

      <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      <div className="tab-content">
        {activeTab === "teams" && (
          <RoundCards users={teams} isRequest={false} isTeam={true} />
        )}
        {activeTab === "requests_teams" && (
          <RoundCards
            users={invites}
            isRequest={true}
            isTeam={true}
            onRespond={handleRespondInvite}
          />
        )}
      </div>
    </div>
  );
}