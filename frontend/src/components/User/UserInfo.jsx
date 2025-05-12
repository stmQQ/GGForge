import "./userInfo.scss";
import TitleH2 from "../TitleH2/TitleH2";

export default function UserInfo({ user, avatar }) {
  return (
    <div className="profile__info">
      <TitleH2 title={user.name} />
      <div className="profile__status">
        <span
          className="profile__status-indicator"
          style={{
            backgroundColor: user.isOnline ? "#00c853" : "#f44336",
          }}
        ></span>
        {user.isOnline ? "В сети" : "Не в сети"} • Дата регистрации {user.registeredDays}
      </div>
    </div>
  );
}