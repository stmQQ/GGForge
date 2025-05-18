import "./header.scss";
import { useState, useContext, useEffect } from "react";
import ModalButton from "../Button/ModalButton.jsx";
import Modal from "../Modal/Modal.jsx";
import TabSwitch from "../TabSwitch/TabSwith.jsx";
import TextInput from "../InputFields/TextInput.jsx";
import SubmitButton from "../Button/SubmitButton.jsx";
import MenuIcon from "../../icons/list.svg?react";
import { AuthContext } from '../../context/AuthContext';
import * as authApi from '../../api/auth';

export default function HeaderLogin({ onMenuToggle }) {
  const { login, register, isAuthenticated, user, isAdmin, logout } = useContext(AuthContext);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const [email, setEmail] = useState('');
  const [name, setName] = useState(''); // Добавлено для регистрации
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [avatar, setAvatar] = useState(null); // Для загрузки аватара
  const [error, setError] = useState(null);

  const tabs = [
    { id: 'login', label: 'Вход' },
    { id: 'register', label: 'Зарегистрироваться' },
  ];

  const resetForm = () => {
    setEmail('');
    setName('');
    setPassword('');
    setConfirmPassword('');
    setAvatar(null);
    setError(null);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Введите почту и пароль');
      return;
    }
    try {
      await login(email, password);
      resetForm();
      setIsModalOpen(false);
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка входа');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      setError('Заполните все поля');
      return;
    }
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    try {
      await register(name, email, password, avatar);
      resetForm();
      setIsModalOpen(false);
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка регистрации');
    }
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      setIsModalOpen(true);
      setActiveTab('login');
    };
    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);


  const handleAvatarChange = (e) => {
    setAvatar(e.target.files[0]);
  };
  console.log(isAuthenticated)

  return (
    <div className="header">
      <div className="header__item">
        <button
          className="header__button header__burger"
          aria-label="меню"
          onClick={onMenuToggle}
        >
          <MenuIcon className="header__icon" />
        </button>
      </div>

      {isAuthenticated ? (
        <div className="header__user">
          <span>{user?.name} {isAdmin && '(Админ)'}</span>
          <button onClick={logout}>Выйти</button>
        </div>
      ) : (
        <ModalButton text="Вход" onClick={() => setIsModalOpen(true)} />
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
      >
        <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
        {error && <p className="error">{error}</p>}

        {activeTab === 'login' ? (
          <form className="header__form" onSubmit={handleLogin}>
            <TextInput
              id="email"
              label="Почта:"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              id="name"
              label="Имя:"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Введите имя"
            />
            <TextInput
              id="email"
              label="Почта:"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
            <div className="form__group">
              <label htmlFor="avatar">Аватар:</label>
              <input
                id="avatar"
                type="file"
                accept="image/png,image/jpeg,image/gif"
                onChange={handleAvatarChange}
              />
            </div>
            <SubmitButton text="Зарегистрироваться" />
          </form>
        )}
      </Modal>
    </div>
  );
}