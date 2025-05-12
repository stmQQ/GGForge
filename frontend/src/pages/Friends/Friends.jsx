import "./friends.scss";

import { useState } from "react";
import { Link } from "react-router-dom";

import {
  friends,
  requests,
  allusers,
  friendRequests,
} from "../../helpers/friend.js";

import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import TabSwich from "../../components/TabSwitch/TabSwith.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import Search from "../../components/Search/Search.jsx";

export default function Friends() {
  const [activeTab, setActiveTab] = useState("friends");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [query, setQuery] = useState("");
  // const [sentRequests, setSentRequests] = useState([]);
  const [disabledUsers, setDisabledUsers] = useState(new Set()); // Состояние для тех, кому уже отправили запрос

  const filteredFriends = allusers.filter((user) =>
    user.name?.toLowerCase().includes(query.toLowerCase())
  );

  // const handleSendRequest = (userId) => {
  //   setSentRequests((prev) => [...prev, userId]);
  //   // Тут можно добавить реальный запрос к серверу, если нужно
  // };

  // Функция для отправки запроса на сервер
  const handleSendRequest = (userId) => {
    // Сделать кнопку неактивной сразу после нажатия
    setDisabledUsers((prev) => new Set(prev).add(userId));

    // Тут мы отправляем запрос на сервер с ID пользователя (можно заменить на реальный запрос)
    console.log("Запрос на сервер отправлен для пользователя с ID:", userId);

    // Если нужно, отправь запрос на сервер здесь.
    // Например: axios.post("/send-request", { userId })
  };

  const tabs = [
    { id: "friends", label: "Ваши друзья" },
    { id: "requests", label: "Заявки в друзья" },
    { id: "submitted", label: "Отправленные заявки" },
  ];

  console.log(disabledUsers);

  return (
    <div>
      <div className="title-with-button">
        <TitleH2 title="Друзья" style="indent" />
        <ModalButton
          text="Добавить друга"
          onClick={() => {
            setIsModalOpen(true);
            setQuery(""); // очистить ввод при открытии
          }}
        />
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <TitleH2 title="Добавить друга" />
        <Search
          placeholder="Введите ник"
          value={query}
          onChange={setQuery}
          style="inverse"
        />

        {query && (
          <div className="friends__results">
            {filteredFriends.length > 0 ? (
              filteredFriends.map((user) => (
                <div key={user.id} className="friends__user">
                  {/* Отображение аватара, ника и кнопки */}
                  <div className="friends__user-row">
                    <div className="friends__user-left">
                      <Link
                        to={`/profile/${user.id}`}
                        className="friends__link"
                      >
                        <img
                          src={user.avatar}
                          alt="avatar"
                          className="friends__avatar"
                        />
                      </Link>
                      <Link
                        to={`/profile/${user.id}`}
                        className="friends__link"
                      >
                        <span className="friends__nickname" title={user.name}>
                          {user.name}
                        </span>
                      </Link>
                    </div>
                    <button
                      className={`friends__button add ${
                        disabledUsers.has(user.id) ? "sent" : ""
                      }`}
                      onClick={() =>
                        !disabledUsers.has(user.id) &&
                        handleSendRequest(user.id)
                      }
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

      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      <div className="tab-content">

        {activeTab === "friends" && (
          <RoundCards users={friends} isRequest={false} isTeam={false} />
        )}

        {activeTab === "requests" && (
          <RoundCards users={requests} isRequest={true} isTeam={false} />
        )}

        {activeTab === "submitted" && (
          <RoundCards users={friendRequests} isRequest={false} isTeam={false} />
        )}
      </div>
    </div>
  );
}
