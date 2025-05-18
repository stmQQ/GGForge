import api from './index';

export const getGames = async () => {
  return api.get('/games/');
};

export const addGame = async (title, imagePath, logoPath, serviceName) => {
  return api.post('/games/', { title, image_path: imagePath, logo_path: logoPath, service_name: serviceName });
};

export const getGameById = async (gameId) => {
  return api.get(`/games/${gameId}`);
};

export const deleteGame = async (gameId) => {
  return api.delete(`/games/${gameId}`);
};

export const addAchievement = async (gameId, title, description, imagePath) => {
  return api.post(`/games/${gameId}/achievements`, { title, description, image_path: imagePath });
};

export const assignAchievement = async (achievementId, userId) => {
  return api.post(`/games/achievements/${achievementId}/assign`, { user_id: userId });
};

export const getUserAchievements = async (userId) => {
  return api.get(`/games/users/${userId}/achievements`);
};