import api from './index';

export const getProfile = async (userId) => {
    return api.get(`/users/${userId}`);
};

export const getMyProfile = async () => {
    return api.get('/users/me');
};

export const updateMyProfile = async (name, email, password, avatar) => {
    const formData = new FormData();
    if (name) formData.append('name', name);
    if (email) formData.append('email', email);
    if (password) formData.append('password', password);
    if (avatar) formData.append('avatar', avatar);
    return api.put('/users/me', formData, { headers: { 'Content-Type': 'multipart/form-data' }, });
};

export const deleteMyProfile = async () => {
    return api.delete('/users/me');
};

export const changePassword = async (currentPassword, newPassword) => {
    return api.patch('/users/me/password', { current_password: currentPassword, new_password: newPassword });
};

export const changeAvatar = async (avatar) => {
    const formData = new FormData();
    formData.append('avatar', avatar);
    return api.patch('/users/me/avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' }, });
};

export const ping = async () => {
    return api.post('/users/me/ping');
};

export const searchUsers = async (nickname) => {
    return api.get('/users/search', { params: { nickname } });
};

export const sendFriendRequest = async (targetUserId) => {
    return api.post('/users/me/friends', { target_user_id: targetUserId });
};

export const getFriendRequests = async () => {
    return api.get('/users/me/friends/requests');
};

export const respondToFriendRequest = async (userId, action) => {
    return api.post(`/users/me/friends/requests/${userId}`, { action });
};

export const getMyFriends = async () => {
    return api.get('/users/me/friends');
};

export const getUserFriends = async (userId) => {
    return api.get(`/users/${userId}/friends`);
};

export const removeFriend = async (friendId) => {
    return api.delete(`/users/me/friends/${friendId}`);
};

export const addGameAccount = async (gameId, serviceName, externalUserUrl) => {
    return api.post('/users/me/game_accounts', { game_id: gameId, service_name: serviceName, external_user_url: externalUserUrl });
};

export const deleteGameAccount = async (gameAccountId) => {
    return api.delete(`/users/me/game_accounts/${gameAccountId}`);
};

export const getMyGameAccounts = async () => {
    return api.get('/users/me/game_accounts');
};

export const getUserGameAccounts = async (userId) => {
    return api.get(`/users/${userId}/game_accounts`);
};

export const createSupportTicket = async (theme, text) => {
    return api.post('/users/me/support_tickets', { theme, text });
};

export const getSupportTickets = async () => {
    return api.get('/users/me/support_tickets');
};