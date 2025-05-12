import "./header.scss";
import { useState } from "react";
import ModalButton from "../Button/ModalButton.jsx";
import Modal from "../Modal/Modal.jsx";
import TabSwich from "../TabSwitch/TabSwith.jsx";
import TextInput from "../InputFields/TextInput.jsx";
import SubmitButton from "../Button/SubmitButton.jsx";
import MenuIcon from "../../icons/list.svg?react";

export default function HeaderLogIn({ onMenuToggle }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [email, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [activeTab, setActiveTab] = useState("login");
  const tabs = [
    { id: "login", label: "Вход" },
    { id: "register", label: "Зарегистрироваться" },
  ];
  const resetForm = () => {
    setName("");
    setPassword("");
    setConfirmPassword("");
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (!email || !password) {
      alert("Введите почту и пароль.");
      return;
    }
    console.log("Вход:", { email, password });
    alert("Успешный вход (пока только имитация)");
    // Тут будет запрос к серверу

    resetForm();
    setIsModalOpen(false);
  };

  const handleRegister = (e) => {
    e.preventDefault();
    if (!email || !password || !confirmPassword) {
      alert("Пожалуйста, заполните все поля.");
      return;
    }
    if (password !== confirmPassword) {
      alert("Пароли не совпадают.");
      return;
    }
    console.log("Регистрация:", { email, password, confirmPassword });
    alert("Регистрация успешна (пока без сервера)");
    // Тут будет запрос на регистрацию

    resetForm();
    setIsModalOpen(false);
  };

  return (
    <div className="header">
      <div className="header__item">
        <button
          className="header__button header__burger"
          aria-label="меню"
          onClick={onMenuToggle} // Используем onMenuToggle, как в Header.jsx
        >
          <MenuIcon className="header__icon" />
        </button>
      </div>

      <ModalButton text="Вход" onClick={() => setIsModalOpen(true)} />
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
      >
        <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

        {activeTab === "login" ? (
          <form className="header__form" onSubmit={handleLogin}>
            <TextInput
              id="email"
              label="Почта:"
              value={email}
              onChange={(e) => setName(e.target.value)}
              placeholder="Введите почту"
            />
            <TextInput
              id="password"
              label="Пароль:"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
            />
            <SubmitButton text="Войти" />
          </form>
        ) : (
          <form className="header__form" onSubmit={handleRegister}>
            <TextInput
              id="email"
              label="Почта:"
              value={email}
              onChange={(e) => setName(e.target.value)}
              placeholder="Введите почту"
            />
            <TextInput
              id="password"
              label="Пароль:"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
            />
            <TextInput
              id="confirm-password"
              label="Подтверждение пароля:"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Повторите пароль"
            />
            <SubmitButton text="Зарегистрироваться" />
          </form>
        )}
      </Modal>
    </div>
  );
}
