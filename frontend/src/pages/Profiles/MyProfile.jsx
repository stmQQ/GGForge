import './myProfile.scss';
import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { getMyGameAccounts, updateMyProfile, changeAvatar, changePassword, addGameAccount, deleteGameAccount } from '../../api/users';
import TitleH2 from '../../components/TitleH2/TitleH2';
import add from '../../images/add-photo1.png';
import TextInput from '../../components/InputFields/TextInput';
import Modal from '../../components/Modal/Modal';
import ModalButton from '../../components/Button/ModalButton';
import GamesMain from '../../components/Games/GamesMain';
import SubmitButton from '../../components/Button/SubmitButton';
import GameAccount from '../../components/Games/GameAccount';
import UserInfo from '../../components/User/UserInfo';

const API_URL = 'http://localhost:5000';
const DEFAULT_AVATAR = `${API_URL}/static/avatars/default.png`;

export default function MyProfile() {
  const { user, isAuthenticated, updateUser } = useContext(AuthContext);
  const [avatar, setAvatar] = useState(DEFAULT_AVATAR);
  const [formValues, setFormValues] = useState({
    name: '',
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });
  const [gameAccounts, setGameAccounts] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gameNickname, setGameNickname] = useState('');
  const [selectedGame, setSelectedGame] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAccountsLoading, setIsAccountsLoading] = useState(true);

  // Синхронизация данных пользователя
  useEffect(() => {
    if (user) {
      setAvatar(user.avatar ? `${API_URL}/${user.avatar}` : DEFAULT_AVATAR);
      setFormValues((prev) => ({ ...prev, name: user.name || '' }));
    }
  }, [user]);

  // Загрузка игровых аккаунтов
  useEffect(() => {
    if (isAuthenticated) {
      getMyGameAccounts()
        .then((res) => {
          console.log(res.data);
          setGameAccounts(
            res.data.map((acc) => ({
              id: acc.id,
              nickname: acc.connection?.external_user_url || 'Unknown',
              title: acc.game?.title || 'Unknown',
              image: `${API_URL}/${acc.game?.logo_path}`,
            }))
          );
        })
        .catch((err) => setError(err.response?.data?.msg || 'Ошибка загрузки аккаунтов'))
        .finally(() => setIsAccountsLoading(false));
    }
  }, [isAuthenticated]);

  const handleAvatarChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      setIsLoading(true);
      const res = await changeAvatar(file);
      const newAvatar = res.data.avatar;
      const avatarUrl = newAvatar ? `${API_URL}/${newAvatar}` : DEFAULT_AVATAR;
      setAvatar(avatarUrl);
      updateUser({ avatar: newAvatar });
      setError('');
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка загрузки аватара');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormValues((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSaveSettings = async () => {
    if (formValues.newPassword !== formValues.confirmNewPassword) {
      setError('Новые пароли не совпадают');
      return;
    }
    try {
      setIsLoading(true);
      if (formValues.currentPassword && formValues.newPassword) {
        await changePassword(formValues.currentPassword, formValues.newPassword);
      }
      if (formValues.name !== user?.name) {
        const res = await updateMyProfile(formValues.name);
        updateUser(res.data.user);
      }
      setFormValues((prev) => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
      }));
      setError('');
    } catch (err) {
      setError(err.response?.data?.msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddGameAccount = async (e) => {
    e.preventDefault();
    if (!selectedGame || !gameNickname) {
      setError('Выберите игру и введите ник');
      return;
    }
    try {
      const res = await addGameAccount(
        selectedGame.id,
        selectedGame.service_name || 'default',
        gameNickname
      );
      setGameAccounts((prev) => [
        ...prev,
        {
          id: res.data.id,
          nickname: gameNickname,
          title: selectedGame.title,
          image: DEFAULT_AVATAR,
        },
      ]);
      setIsModalOpen(false);
      setSelectedGame(null);
      setGameNickname('');
      setError('');
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка добавления аккаунта');
    }
  };

  const handleDeleteGameAccount = async (id) => {
    try {
      await deleteGameAccount(id);
      setGameAccounts((prev) => prev.filter((acc) => acc.id !== id));
      setError('');
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка удаления аккаунта');
    }
  };

  if (!isAuthenticated) {
    return <div className="error-message">Пожалуйста, войдите в аккаунт</div>;
  }
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
            style={{ display: 'none' }}
            disabled={isLoading}
          />
        </label>
      </div>

      <UserInfo user={user} avatar={avatar} />

      <div className="profile__windows">
        <div className="profile__window profile__window--left">
          <h3 className="profile__window-title">Игровые аккаунты</h3>
          <ModalButton
            text="Добавить аккаунт"
            onClick={() => setIsModalOpen(true)}
            disabled={isAccountsLoading}
          />
          <div className="gameAccountsList">
            {isAccountsLoading ? (
              <p>Загрузка...</p>
            ) : gameAccounts.length ? (
              gameAccounts.map((acc) => (
                <GameAccount
                  key={acc.id}
                  id={acc.id}
                  title={acc.title}
                  nickname={acc.nickname}
                  image={acc.image}
                  onDelete={handleDeleteGameAccount}
                  showDelete={true}
                />
              ))
            ) : (
              <p>Нет аккаунтов</p>
            )}
          </div>
        </div>

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <TitleH2 title="Добавить игровой аккаунт" />
          {selectedGame ? (
            <form className="gameNickname__form" onSubmit={handleAddGameAccount}>
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
            <GamesMain style="modal" onSelectGame={(game) => setSelectedGame(game)} />
          )}
        </Modal>

        <div className="profile__window profile__window--right">
          <h3 className="profile__window-title">Настройки</h3>
          <TextInput
            id="email"
            label="Почта"
            value={user.email}
            disabled={true}
            style={{ backgroundColor: '#f0f0f0', cursor: 'not-allowed' }}
          />
          <TextInput
            id="name"
            label="Никнейм"
            name="name"
            value={formValues.name}
            onChange={handleInputChange}
            placeholder="Ваш ник"
          />
          <TextInput
            id="currentPassword"
            label="Текущий пароль"
            type="password"
            name="currentPassword"
            value={formValues.currentPassword}
            onChange={handleInputChange}
            placeholder="Введите текущий пароль"
          />
          <TextInput
            id="newPassword"
            label="Новый пароль"
            type="password"
            name="newPassword"
            value={formValues.newPassword}
            onChange={handleInputChange}
            placeholder="Введите новый пароль"
          />
          <TextInput
            id="confirmNewPassword"
            label="Подтвердите новый пароль"
            type="password"
            name="confirmNewPassword"
            value={formValues.confirmNewPassword}
            onChange={handleInputChange}
            placeholder="Подтвердите новый пароль"
          />
          {error && <div className="error-message">{error}</div>}
          <SubmitButton
            text="Сохранить"
            onClick={handleSaveSettings}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
}