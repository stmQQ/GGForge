import { useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function ProfileDropdown({ isOpen, onClose, logout }) {
    const dropdownRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                onClose();
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [onClose]);

    if (!isOpen) return null;

    return (
        <div className="dropdown dropdown__profile" ref={dropdownRef}>
            <Link to="/profile" className="dropdown__item" onClick={onClose}>
                Профиль
            </Link>
            <Link to="/friends" className="dropdown__item" onClick={onClose}>
                Друзья
            </Link>
            <Link to="/teams" className="dropdown__item" onClick={onClose}>
                Команды
            </Link>
            <div className="dropdown__divider" />
            <Link to="/games" className="dropdown__item" onClick={onClose}>
                Игры
            </Link>
            <Link to="/tournaments" className="dropdown__item" onClick={onClose}>
                Турниры
            </Link>
            <div className="dropdown__divider" />
            <Link className="dropdown__item" onClick={() => { logout(); onClose(); }}>
                Выйти
            </Link>
        </div>
    );
}