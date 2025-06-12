import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { getTeam, inviteUserToTeam } from "../../api/teams";
import { API_URL } from "../../constants.js";
import TitleH2 from "../../components/TitleH2/TitleH2";
import TabSwitch from "../../components/TabSwitch/TabSwitch.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import Search from "../../components/Search/Search.jsx";
import {
  searchUsers,
} from "../../api/users";

const tabs = [
  { id: "information", label: "Информация" },
  { id: "participants", label: "Участники" },
];

export default function TeamPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("information");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [team, setTeam] = useState(null);
  const [error, setError] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [disabledUsers, setDisabledUsers] = useState(new Set());

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

  const handleSendRequest = async (userId) => {
    setDisabledUsers((prev) => new Set(prev).add(userId));
    try {
      await inviteUserToTeam(team.id, userId);
      await fetchData();
      setError("");
    } catch (err) {
      setDisabledUsers((prev) => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
      setError(err.response?.data?.msg || "Ошибка отправки заявки");
    }
  };

  const handleSearch = async (value) => {
    setQuery(value);
    if (!value) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await searchUsers(value);
      setSearchResults(
        (res.data || []).map((user) => ({
          id: user.id,
          name: user.name,
          avatar: getAvatarUrl(user.avatar),
        }))
      );
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка поиска");
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
        <div className="profile__info">
          <TitleH2 title={team.name} />
        </div>
        <ModalButton
          text="Добавить участника"
          onClick={() => {
            setIsModalOpen(true);
            setQuery("");
            setSearchResults([]);
          }}
        />
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <TitleH2 title="Добавить участника" />
        <Search
          placeholder="Введите ник"
          value={query}
          onChange={handleSearch}
          style="inverse"
        />

        {query && (
          <div className="friends__results">
            {searchResults.length > 0 ? (
              searchResults.map((user) => (
                <div key={user.id} className="friends__user">
                  <div className="friends__user-row">
                    <div className="friends__user-left">
                      <Link to={`/profile/${user.id}`} className="friends__link">
                        <img
                          src={user.avatar}
                          alt="avatar"
                          className="friends__avatar"
                        />
                      </Link>
                      <Link to={`/profile/${user.id}`} className="friends__link">
                        <span className="friends__nickname" title={user.name}>
                          {user.name}
                        </span>
                      </Link>
                    </div>
                    <button
                      className={`friends__button add ${disabledUsers.has(user.id) ? "sent" : ""
                        }`}
                      onClick={() => handleSendRequest(user.id)}
                      disabled={disabledUsers.has(user.id)}
                    >
                      +
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="friends__user empty">Никого не найдено</div>
            )}
          </div>
        )}
      </Modal>

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