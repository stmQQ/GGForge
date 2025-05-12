// import "./myProfile.scss";
import { useState } from "react";
import { useParams } from "react-router-dom";

import UserInfo from "../../components/User/UserInfo";
import SubmitButton from "../../components/Button/SubmitButton";
import TabSwich from "../../components/TabSwitch/TabSwith";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import GameAccount from "../../components/Games/GameAccount.jsx";
import Tournaments from "../../components/Tournaments/Tournaments";

import avatar from "../../images/game1.jpg";
import { commands } from "../../helpers/commands.js";
import { friends } from "../../helpers/friend.js";
import defaultAvatar from "../../images/default-avatar.jpg";
import game1 from "../../images/game2.jpg";

const user = {
  id: 1,
  name: "inova",
  // email: "user@example.com",
  avatar: avatar,
  isOnline: true,
  registeredDays: "55.05.2021",
  friendshipStatus: "yes", //no/yes/requested
};

const tabs = [
  { id: "information", label: "Информация" },
  { id: "teamsUser", label: "Команды" },
  { id: "Friendsuser", label: "Друзья" },
];

export default function Profile() {
  const { id } = useParams();

  const [activeTab, setActiveTab] = useState("information");

  const [friendshipStatus, setFriendshipStatus] = useState(
    user.friendshipStatus
  );
  const [isRequestSent, setIsRequestSent] = useState(false);

  const getButtonText = () => {
    if (friendshipStatus === "yes") {
      return "Удалить из друзей";
    }
    return isRequestSent ? "Отменить заявку" : "Отправить заявку";
  };

  const handleFriendAction = () => {
    if (friendshipStatus === "yes") {
      // Удаляем из друзей
      setFriendshipStatus("no");
      setIsRequestSent(false);
      console.log("Запрос отправлен: удалить друга");
    } else if (isRequestSent) {
      // Отменяем заявку
      setIsRequestSent(false);
      console.log("Запрос отправлен: отменить заявку");
    } else {
      // Отправляем заявку
      setIsRequestSent(true);
      console.log("Запрос отправлен: добавить друга");
    }

    // Здесь можно отправить fetch / axios POST запрос
    // fetch('/api/friend-action', { method: 'POST', body: JSON.stringify({ id: user.id }) })

    // Можно также менять текст кнопки после нажатия:
  };

  const gameAccounts = [
    { id: 1, nickname: "PlayerOne", title: "Dota 2", image: defaultAvatar },
    { id: 2, nickname: "GamerGirl", title: "Valorant", image: defaultAvatar },
  ];

  const listTournaments = [
    {
      id: 1,
      img: game1,
      title: "Турнир 1 орг",
      status: "open",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 2,
      img: game1,
      title: "Турнир 2 орг",
      status: "ongoing",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
    {
      id: 3,
      img: game1,
      title: "Турнир 3 орг",
      status: "completed",
      date: "12.12.2003 | 17:00",
      inf: "5v5 | 32 места | 1.000.000₽ ",
    },
  ];

  return (
    <div>
      <div className="profile profile__header">
        <div className="profile__avatar">
          <img
            src={user.avatar}
            alt="avatar"
            className="profile__avatar-image"
          />
        </div>

        <UserInfo user={user} avatar={user.avatar} />

        {user.friendshipStatus !== "requested" && (
          <SubmitButton
            text={getButtonText()}
            onClick={handleFriendAction}
            // disabled={true}
            // isSent={isRequestSent && friendshipStatus !== "yes"}
            type="button"
          />
        )}
      </div>

      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      {activeTab === "information" && (
        <div className="tab-content">
          <div className="profile__windows">
            <div className="profile__window profile__window--left">
              <h3 className="profile__window-title">Игровые аккаунты</h3>
              <div className="gameAccountsList">
                {gameAccounts.map((account) => (
                  <GameAccount
                    key={account.id}
                    id={account.id}
                    title={account.title}
                    nickname={account.nickname}
                    image={account.image}
                    showDelete={false}
                    // onDelete={handleDeleteGameAccount} // если нужно
                  />
                ))}
              </div>
            </div>
            <div className="profile__window profile__window--right">
              <h3 className="profile__window-title">Турниры пользователя</h3>
              {listTournaments.length > 0 ? (
                <Tournaments array={listTournaments} modifier="profile-view" />
              ) : (
                <p className="user-tournaments__empty">Нет турниров</p>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === "teamsUser" && (
        <div className="tab-content">
          <RoundCards users={commands} isRequest={false} isTeam={true} />
        </div>
      )}

      {activeTab === "Friendsuser" && (
        <div className="tab-content">
          <RoundCards users={friends} isRequest={false} isTeam={false} />
        </div>
      )}
    </div>
  );
}
