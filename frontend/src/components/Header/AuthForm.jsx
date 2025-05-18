import { useState, useContext } from 'react';
import TabSwitch from '../TabSwitch/TabSwitch.jsx';
import TextInput from '../InputFields/TextInput.jsx';
import SubmitButton from '../Button/SubmitButton.jsx';
import { AuthContext } from '../../context/AuthContext';

export default function AuthForm({ onSuccess }) {
    const { login, register } = useContext(AuthContext);
    const [activeTab, setActiveTab] = useState('login');
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [avatar, setAvatar] = useState(null);
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
            onSuccess();
        } catch (err) {
            setError(err.response?.data?.msg || 'Ошибка входа');
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        console.log(name, email, password, confirmPassword);
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
            onSuccess();
        } catch (err) {
            setError(err.response?.data?.msg || 'Ошибка регистрации');
        }
    };

    const handleAvatarChange = (e) => {
        setAvatar(e.target.files[0]);
    };

    return (
        <div className="header__form">
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
                    <SubmitButton text="Зарегистрироваться" />
                </form>
            )}
        </div>
    );
}