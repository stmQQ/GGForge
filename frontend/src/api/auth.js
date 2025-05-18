import api from './index';

export const register = async (name, email, password, avatar) => {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('password', password);
    if (avatar) formData.append('avatar', avatar);
    return api.post('/auth/register', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

export const login = async (email, password) => {
    return api.post('/auth/login', { email, password });
};

export const refreshToken = async () => {
    return api.post('/auth/refresh');
};

export const logout = async () => {
    return api.post('/auth/logout');
};