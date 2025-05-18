import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as authApi from '../api/auth';
import * as userApi from '../api/users';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            userApi.getMyProfile()
                .then((response) => {
                    setUser(response.data);
                    setIsAuthenticated(true);
                    setIsAdmin(response.data.is_admin || false); // Проверяем is_admin из /users/me
                })
                .catch(() => {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    setIsAuthenticated(false);
                    setIsAdmin(false);
                })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        const response = await authApi.login(email, password);
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        setUser(response.data.user);
        setIsAuthenticated(true);
        setIsAdmin(response.data.user.is_admin || false);
        return response.data; // Возвращаем данные для закрытия модального окна
    };

    const register = async (name, email, password, avatar) => {
        console.log(name, email, password);
        const response = await authApi.register(name, email, password, avatar);
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        setUser(response.data.user);
        setIsAuthenticated(true);
        setIsAdmin(response.data.user.is_admin || false);
        return response.data; // Возвращаем данные для закрытия модального окна
    };

    const logout = async () => {
        await authApi.logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        setIsAuthenticated(false);
        setIsAdmin(false);
        navigate('/'); // Перенаправляем на главную
    };

    const refresh = async () => {
        try {
            const response = await authApi.refreshToken();
            localStorage.setItem('access_token', response.data.access_token);
            setUser(response.data.user);
            setIsAuthenticated(true);
            setIsAdmin(response.data.user.is_admin || false);
        } catch (error) {
            logout();
        }
    };

    return (
        <AuthContext.Provider
            value={{ user, isAuthenticated, isAdmin, isLoading, login, register, logout, refresh }}
        >
            {children}
        </AuthContext.Provider>
    );
};