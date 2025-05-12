import "./myProfile.scss";
import { useState } from "react";

import TitleH2 from "../../components/TitleH2/TitleH2";
import defaultAvatar from "../../images/default-avatar.jpg";
import add from "../../images/add-photo1.png";
import TextInput from "../../components/InputFields/TextInput";
import Modal from "../../components/Modal/Modal";
import ModalButton from "../../components/Button/ModalButton";
import GamesMain from "../../components/Games/GamesMain";
import SubmitButton from "../../components/Button/SubmitButton";
import GameAccount from "../../components/Games/GameAccount";
import UserInfo from "../../components/User/UserInfo";

// import SubmitButton from "../../components/Button/SubmitButton";

const user = {
  id: 1,
  name: "iburdinova",
  email: "user@example.com",
  avatar: "", // Если здесь пусто или null — будет стандартная картинка
  isOnline: true,
  registeredDays: "20.05.2021",
};

export default function MyProfile() {
  //Аватар
  const [avatar, setAvatar] = useState(user.avatar || defaultAvatar);
  const [isLoading, setIsLoading] = useState(false);
  // Настройки профиля
  const [formValues, setFormValues] = useState({
    currentPassword: "",
    newPassword: "",
    confirmNewPassword: "",
    name: user.name,
  });
  const [error, setError] = useState("");
  // Модалка "Добавить аккаунт"
  const [gameNickname, setGameNickname] = useState("");
  const [selectedGame, setSelectedGame] = useState(null); // Состояние для выбранной игры
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedGame(null); // сбрасываем выбранную игру при закрытии модалки
  };

  const handleGameSelect = (game) => {
    setSelectedGame(game); // Устанавливаем выбранную игру
  };

  // Обработчик загрузки нового аватара
  const handleAvatarChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("avatar", file);

      try {
        setIsLoading(true);
        // **Здесь будет запрос на сервер для загрузки аватара**
        // Пример:
        // const response = await fetch("/api/upload-avatar", {
        //   method: "POST",
        //   body: formData,
        // });

        // **После получения ответа от сервера:**
        // const data = await response.json();
        // setAvatar(data.avatarUrl); // Пример получения URL аватара с сервера
        setTimeout(() => {
          setAvatar(URL.createObjectURL(file));
        }, 1);
      } catch (error) {
        console.error("Ошибка загрузки аватара:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prevValues) => ({
      ...prevValues,
      [name]: value,
    }));
  };

  const handleSaveSettings = async () => {
    // Проверяем, что пароли совпадают
    if (formValues.newPassword !== formValues.confirmNewPassword) {
      alert("Новые пароли не совпадают");
      return;
    }

    try {
      // Здесь будет отправка на сервер
      // Пример:
      // const response = await fetch("/api/update-password", {
      //   method: "POST",
      //   body: JSON.stringify(formValues),
      //   headers: { "Content-Type": "application/json" },
      // });

      // Если сервер вернул ошибку по текущему паролю
      // const data = await response.json();
      // if (data.error === "incorrect_password") {
      //   alert("Неверный текущий пароль");
      //   return;
      // }

      // Сохраняем данные, если все успешно
      alert("Настройки сохранены");
    } catch (error) {
      console.error("Ошибка сохранения настроек:", error);
    }
  };

  const handleDeleteGameAccount = async (id) => {
    try {
      // отправляем запрос на сервер для удаления
      // пример:
      // await fetch(`/api/game-accounts/${id}`, { method: "DELETE" });
      // const response = await fetch(`/api/game-accounts/${id}`, { method: "DELETE" });

      // if (!response.ok) {
      //   throw new Error("Ошибка на сервере");
      // }

      console.log(`Отправлен запрос на удаление аккаунта с id ${id}`);

      // после успешного ответа удаляем из локального состояния
      setGameAccounts((prev) => prev.filter((account) => account.id !== id));
      // console.log({ gameAccounts });
    } catch (error) {
      console.error("Ошибка удаления аккаунта:", error);
      alert("Не удалось удалить аккаунт. Попробуйте ещё раз.");
    }
  };

  const [gameAccounts, setGameAccounts] = useState([
    { id: 1, nickname: "PlayerOne", title: "Dota 2", image: defaultAvatar },
    { id: 2, nickname: "GamerGirl", title: "Valorant", image: defaultAvatar },
  ]);

  return (
    <div className="profile">
      <div className="profile__avatar">
        <img src={avatar} alt="avatar" className="profile__avatar-image" />

        <label className="profile__avatar-button">
          <img src={add} alt="change avatar" />
          <input
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            style={{ display: "none" }} // Скрываем input
          />
        </label>
      </div>

      {/* <div className="profile__info">
        <TitleH2 title={user.name} />

        <div className="profile__status">
          <span
            className="profile__status-indicator"
            style={{
              backgroundColor: user.isOnline ? "#00c853" : "#f44336", // Зеленый если онлайн, красный если оффлайн
            }}
          ></span>
          {user.isOnline ? "В сети" : "Не в сети"} • Дата регистрации{" "}
          {user.registeredDays}
        </div>
      </div> */}

      <UserInfo user={user} avatar={avatar} />

      <div className="profile__windows">
        <div className="profile__window profile__window--left">
          <h3 className="profile__window-title">Игровые аккаунты</h3>
          <ModalButton
            text="Добавить аккаунт"
            onClick={() => setIsModalOpen(true)}
          />

          <div className="gameAccountsList">
            {gameAccounts.map((account) => (
              <GameAccount
                key={account.id}
                id={account.id}
                title={account.title}
                nickname={account.nickname}
                image={account.image}
                onDelete={handleDeleteGameAccount}
              />
            ))}
          </div>
        </div>

        <Modal isOpen={isModalOpen} onClose={handleCloseModal}>
          <TitleH2 title="Добавить игровой аккаунт" />

          {selectedGame ? (
            <form
              className="gameNickname__form"
              onSubmit={(e) => {
                e.preventDefault();
                console.log("Игра:", selectedGame);
                console.log("Игровой ник:", gameNickname);
                // Здесь потом будет отправка на сервер

                // После успешной отправки:
                setGameNickname(""); // очищаем поле
                setSelectedGame(null); // сбрасываем выбранную игру
                setIsModalOpen(false); // закрываем модалку
              }}
            >
              {/* Если игра выбрана, отображаем форму для ввода текста */}
              <TextInput
                id="gameNickname"
                label="Ник в игре:"
                value={gameNickname}
                onChange={(e) => setGameNickname(e.target.value)}
                placeholder="Введите ник"
              />
              <SubmitButton text="Создать" />
            </form>
          ) : (
            // <div>fghj</div>
            // Если игра не выбрана, отображаем список игр
            <GamesMain style="modal" onSelectGame={handleGameSelect} />
          )}
        </Modal>

        <div className="profile__window profile__window--right">
          <h3 className="profile__window-title">Настройки</h3>
          {/* <form onSubmit={(e) => { e.preventDefault(); handleSaveSettings(); }}> */}
          <TextInput
            id="email"
            label="Почта"
            value={user.email}
            // onChange={() => {}}
            placeholder="Ваш email"
            disabled={true}
            style={{ backgroundColor: "#f0f0f0", cursor: "not-allowed" }}
          />
          <TextInput
            id="nickname"
            label="Никнейм"
            value={formValues.name}
            onChange={handleInputChange}
            placeholder="Ваш ник"
            name="name"
          />
          <TextInput
            id="currentPassword"
            label="Текущий пароль"
            type="password"
            value={formValues.currentPassword}
            onChange={handleInputChange}
            placeholder="Введите текущий пароль"
            name="currentPassword"
          />
          <TextInput
            id="newPassword"
            label="Новый пароль"
            type="password"
            value={formValues.newPassword}
            onChange={handleInputChange}
            placeholder="Введите новый пароль"
            name="newPassword"
          />
          <TextInput
            id="confirmNewPassword"
            label="Подтвердите новый пароль"
            type="password"
            value={formValues.confirmNewPassword}
            onChange={handleInputChange}
            placeholder="Подтвердите новый пароль"
            name="confirmNewPassword"
          />
          {error && <div className="error-message">{error}</div>}

          <button className="profile__save-button" onClick={handleSaveSettings}>
            Сохранить
          </button>
        </div>
      </div>
    </div>
  );
}
