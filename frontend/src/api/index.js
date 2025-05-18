import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { useContext } from 'react';

// Хук для доступа к AuthContext в функциональном стиле
const useAuth = () => useContext(AuthContext);

const api = axios.create({
    baseURL: 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Интерцептор для добавления JWT-токена
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            // Вместо window.location.href вызываем событие или обновляем контекст
            // Компонент Home.jsx должен открыть модальное окно
            return Promise.reject({ ...error, requiresLogin: true });
        }
        return Promise.reject(error);
    }
);

export default api;