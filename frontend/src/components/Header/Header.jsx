import './header.scss';
import { useState, useContext, useEffect } from 'react';
import ModalButton from '../Button/ModalButton.jsx';
import Modal from '../Modal/Modal.jsx';
import MenuIcon from '../../icons/list.svg?react';
import ProfileIcon from '../../icons/profile.svg?react';
import { AuthContext } from '../../context/AuthContext';
import AuthForm from './AuthForm.jsx';
import ProfileDropdown from './ProfileDropdown.jsx';

export default function Header({ onMenuToggle }) {
  const { isAuthenticated, user, isAdmin, logout } = useContext(AuthContext);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProfileOpen, setProfileOpen] = useState(false);

  // Открываем модал при 401-ошибке или попытке доступа к защищённому маршруту
  useEffect(() => {
    const handleUnauthorized = () => {
      if (!isModalOpen) {
        setIsModalOpen(true);
      }
    };
    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, [isModalOpen]);

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

      <div className="header__item">
        {isAuthenticated ? (
          <div className="header__item">
            <button
              className="header__button"
              aria-label="профиль"
              onClick={() => setProfileOpen((prev) => !prev)}
            >
              <ProfileIcon className="header__icon" />
            </button>

            <ProfileDropdown
              isOpen={isProfileOpen}
              onClose={() => setProfileOpen(false)}
              logout={logout}
            />
          </div>
        ) : (
          <ModalButton text="Вход" onClick={() => setIsModalOpen(true)} />
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      >
        <AuthForm onSuccess={() => setIsModalOpen(false)} />
      </Modal>
    </div>
  );
}