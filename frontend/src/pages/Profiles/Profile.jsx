import './myProfile.scss';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getProfile, getUserGameAccounts, getUserFriends, sendFriendRequest, respondToFriendRequest, removeFriend } from '../../api/users';
import { getUserTeams } from '../../api/teams';
import { getUserCreatedTournaments } from '../../api/tournaments'
import UserInfo from '../../components/User/UserInfo';
import SubmitButton from '../../components/Button/SubmitButton';
import TabSwitch from '../../components/TabSwitch/TabSwitch.jsx';
import RoundCards from '../../components/RoundCard/RoundCardsContainer.jsx';
import GameAccount from '../../components/Games/GameAccount.jsx';
import Tournaments from '../../components/Tournaments/Tournaments';
import { API_URL } from '../../constants.js';

const tabs = [
  { id: 'information', label: 'Информация' },
  { id: 'teamsUser', label: 'Команды' },
  { id: 'friendsUser', label: 'Друзья' },
];

const DEFAULT_AVATAR = `${API_URL}/static/avatars/default.png`;

export default function Profile() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('information');
  const [user, setUser] = useState(null);
  const [gameAccounts, setGameAccounts] = useState([]);
  const [teams, setTeams] = useState([]);
  const [friends, setFriends] = useState([]);
  const [tournaments, setTournaments] = useState([]);
  const [friendshipStatus, setFriendshipStatus] = useState('no'); // 'no', 'yes', 'requested', 'pending'
  const [error, setError] = useState('');

  // Формирование URL для аватара
  const getAvatarUrl = (avatar) =>
    avatar ? `${API_URL}/${avatar}` : DEFAULT_AVATAR;

  // Формирование URL для логотипа команды
  const getTeamLogoUrl = (logoPath) =>
    logoPath ? `${API_URL}/${logoPath}` : `${API_URL}/static/team_logos/default.png`;

  // Загрузка данных
  const fetchData = async () => {
    try {
      // Данные пользователя
      const userRes = await getProfile(id);
      const userData = userRes.data.user;
      setUser({
        id: userData.id,
        name: userData.name,
        avatar: getAvatarUrl(userData.avatar),
        email: userData.email || '',
        isOnline: userData.is_online || false,
        registration_date: new Date(userData.registration_date).toLocaleDateString('ru-RU'),
        friendshipStatus: userRes.data.friendship_status || 'no',
      });
      setFriendshipStatus(userRes.data.friendship_status || 'no');

      // Игровые аккаунты
      const accountsRes = await getUserGameAccounts(id);
      setGameAccounts(
        accountsRes.data.map((acc) => ({
          id: acc.id,
          nickname: acc.external_user_url || 'Unknown',
          title: acc.game?.title || 'Unknown',
          image: DEFAULT_AVATAR,
        }))
      );

      // Команды
      const memberTeamsRes = await getUserTeams(id);
      const allTeams = [
        ...(memberTeamsRes.data.member_teams || []),
      ].map((team) => ({
        id: team.id,
        name: team.title,
        avatar: getTeamLogoUrl(team.logo_path),
      }));
      setTeams(allTeams);

      // Друзья
      const friendsRes = await getUserFriends(id);
      setFriends(
        friendsRes.data.map((friend) => ({
          id: friend.id,
          name: friend.name,
          avatar: getAvatarUrl(friend.avatar),
        }))
      );

      // Турниры (загружено созданные турниры)
      const tournamentsRes = await getUserCreatedTournaments(id);
      setTournaments(
        tournamentsRes.data.map((tournament) => ({
          id: tournament.id,
          title: tournament.title,
          game: tournament.game?.title || 'Unknown',
          startTime: new Date(tournament.start_time).toLocaleString('ru-RU'),
          status: tournament.status,
          banner: tournament.banner_url ? `${API_URL}/${tournament.banner_url}` : null,
          prizeFund: tournament.prize_fund,
        }))
      );

      setError('');
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка загрузки данных');
    }
  };

  // Действия с дружбой
  const handleFriendAction = async () => {
    try {
      if (friendshipStatus === 'yes') {
        await removeFriend(id);
        setFriendshipStatus('no');
      } else if (friendshipStatus === 'requested') {
        await respondToFriendRequest(id, 'reject');
        setFriendshipStatus('no');
      } else if (friendshipStatus === 'pending') {
        await respondToFriendRequest(id, 'accept');
        setFriendshipStatus('yes');
      } else {
        await sendFriendRequest(id);
        setFriendshipStatus('requested');
      }
      await fetchData();
      setError('');
    } catch (err) {
      setError(err.response?.data?.msg || 'Ошибка обработки запроса');
    }
  };

  // Загрузка при монтировании
  useEffect(() => {
    fetchData();
  }, [id]);

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!user) {
    return <div>Загрузка...</div>;
  }

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
        <SubmitButton
          text={
            friendshipStatus === 'yes'
              ? 'Удалить из друзей'
              : friendshipStatus === 'requested'
                ? 'Отменить заявку'
                : friendshipStatus === 'pending'
                  ? 'Принять заявку'
                  : 'Отправить заявку'
          }
          onClick={handleFriendAction}
          type="button"
        />
      </div>

      <TabSwitch tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      {activeTab === 'information' && (
        <div className="tab-content">
          <div className="profile__windows">
            <div className="profile__window profile__window--left">
              <h3 className="profile__window-title">Игровые аккаунты</h3>
              <div className="gameAccountsList">
                {gameAccounts.length ? (
                  gameAccounts.map((acc) => (
                    <GameAccount
                      key={acc.id}
                      id={acc.id}
                      title={acc.title}
                      nickname={acc.nickname}
                      image={acc.image}
                      showDelete={false}
                    />
                  ))
                ) : (
                  <p>Нет аккаунтов</p>
                )}
              </div>
            </div>
            <div className="profile__window profile__window--right">
              <h3 className="profile__window-title">Турниры пользователя</h3>
              {tournaments.length ? (
                <Tournaments array={tournaments} modifier="profile-view" />
              ) : (
                <p className="user-tournaments__empty">Нет турниров</p>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'teamsUser' && (
        <div className="tab-content">
          <RoundCards users={teams} isRequest={false} isTeam={true} />
        </div>
      )}

      {activeTab === 'friendsUser' && (
        <div className="tab-content">
          <RoundCards users={friends} isRequest={false} isTeam={false} />
        </div>
      )}
    </div>
  );
}