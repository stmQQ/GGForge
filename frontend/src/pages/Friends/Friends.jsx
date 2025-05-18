import "./friends.scss";
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getMyFriends,
  getFriendRequests,
  searchUsers,
  sendFriendRequest,
  respondToFriendRequest,
} from "../../api/users";
import { API_URL } from "../../constants.js"; // Импорт API_URL
import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import TabSwitch from "../../components/TabSwitch/TabSwitch.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import Search from "../../components/Search/Search.jsx";

export default function Friends() {
  const [activeTab, setActiveTab] = useState("friends");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [friends, setFriends] = useState([]);
  const [incomingRequests, setIncomingRequests] = useState([]);
  const [outgoingRequests, setOutgoingRequests] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [disabledUsers, setDisabledUsers] = useState(new Set());
  const [error, setError] = useState("");

  // Формирование URL для аватара
  const getAvatarUrl = (avatar) =>
    avatar ? `${API_URL}/${avatar}` : `${API_URL}/static/avatars/default.png`;

  // Загрузка данных с сервера
  const fetchData = async () => {
    try {
      // Друзья
      const friendsRes = await getMyFriends();
      setFriends(
        (friendsRes.data || []).map((f) => ({
          id: f.id,
          name: f.name,
          avatar: getAvatarUrl(f.avatar),
        }))
      );

      // Заявки
      const requestsRes = await getFriendRequests();
      setIncomingRequests(
        (requestsRes.data.incoming_requests || []).map((req) => ({
          id: req.from_user.id,
          name: req.from_user.name,
          avatar: getAvatarUrl(req.from_user.avatar),
          requestId: req.id,
        }))
      );
      setOutgoingRequests(
        (requestsRes.data.outgoing_requests || []).map((req) => ({
          id: req.to_user.id,
          name: req.to_user.name,
          avatar: getAvatarUrl(req.to_user.avatar),
        }))
      );
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка загрузки данных");
    }
  };

  // Поиск пользователей
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

  // Отправка запроса в друзья
  const handleSendRequest = async (userId) => {
    setDisabledUsers((prev) => new Set(prev).add(userId));
    try {
      await sendFriendRequest(userId);
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

  // Ответ на заявку
  const handleRespondRequest = async (requestId, action) => {
    try {
      await respondToFriendRequest(requestId, action);
      await fetchData();
      setError("");
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка обработки заявки");
    }
  };

  // Загрузка данных при монтировании
  useEffect(() => {
    fetchData();
  }, []);

  const tabs = [
    { id: "friends", label: "Ваши друзья" },
    { id: "requests", label: "Заявки в друзья" },
    { id: "submitted", label: "Отправленные заявки" },
  ];

  return (
    <div>
      <div className="title-with-button">
        <TitleH2 title="Друзья" style="indent" />
        <ModalButton
          text="Добавить друга"
          onClick={() => {
            setIsModalOpen(true);
            setQuery("");
            setSearchResults([]);
          }}
        />
      </div>

      {error && <div className="friends__error">{error}</div>}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <TitleH2 title="Добавить друга" />
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
        {activeTab === "friends" && (
          <RoundCards
            users={friends}
            isRequest={false}
            isTeam={false}
          />
        )}

        {activeTab === "requests" && (
          <RoundCards
            users={incomingRequests}
            isRequest={true}
            isTeam={false}
            onRespond={handleRespondRequest}
          />
        )}

        {activeTab === "submitted" && (
          <RoundCards
            users={outgoingRequests}
            isRequest={false}
            isTeam={false}
          />
        )}
      </div>
    </div>
  );
}