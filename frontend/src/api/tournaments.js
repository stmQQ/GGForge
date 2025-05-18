import api from './index';

export const createTournament = async (tournamentData) => {
  return api.post('/tournaments/', tournamentData, { headers: { 'Content-Type': 'multipart/form-data' }, });
};

export const getTournamentsByGame = async (gameId) => {
  return api.get(`/tournaments/game/${gameId}`);
};

export const getParticipantTournaments = async () => {
  return api.get('/tournaments/participant/me');
};

export const getCreatorTournaments = async () => {
  return api.get('/tournaments/creator/me');
};

export const getUserCreatedTournaments = async (userId) => {
  return api.get(`/tournaments/creator/${userId}`);
};

export const getTournament = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}`);
};

export const getTournamentGroupStage = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/group-stage`);
};

export const getTournamentPlayoffStage = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/playoff-stage`);
};

export const getTournamentPrizeTable = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/prize-table`);
};

export const getAllTournamentMatches = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/matches`);
};

export const getGroupStageMatches = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/group-stage/matches`);
};

export const getPlayoffStageMatches = async (tournamentId) => {
  return api.get(`/tournaments/${tournamentId}/playoff-stage/matches`);
};

export const getMatch = async (tournamentId, matchId) => {
  return api.get(`/tournaments/${tournamentId}/matches/${matchId}`);
};

export const createMatch = async (tournamentId, matchData) => {
  return api.post(`/tournaments/${tournamentId}/matches`, matchData);
};

export const updateMatchResults = async (tournamentId, matchId, winnerId, status) => {
  return api.patch(`/tournaments/${tournamentId}/matches/${matchId}`, { winner_id: winnerId, status });
};

export const startTournament = async (tournamentId) => {
  return api.post(`/tournaments/${tournamentId}/start`);
};

export const completeTournament = async (tournamentId) => {
  return api.post(`/tournaments/${tournamentId}/complete`);
};

export const registerForTournament = async (tournamentId, isTeam, participantId) => {
  return api.post(`/tournaments/${tournamentId}/register`, { is_team: isTeam, participant_id: participantId });
};

export const unregisterForTournament = async (tournamentId, isTeam, participantId) => {
  return api.post(`/tournaments/${tournamentId}/unregister`, { is_team: isTeam, participant_id: participantId });
};

export const resetTournament = async (tournamentId) => {
  return api.post(`/tournaments/${tournamentId}/reset`);
};

export const deleteTournament = async (tournamentId) => {
  return api.delete(`/tournaments/${tournamentId}`);
};

export const completeMap = async (tournamentId, matchId, mapId, winnerId) => {
  return api.post(`/tournaments/${tournamentId}/matches/${matchId}/maps/${mapId}/complete`, { winner_id: winnerId });
};

export const completeMatch = async (tournamentId, matchId, winnerId) => {
  return api.post(`/tournaments/${tournamentId}/matches/${matchId}/complete`, { winner_id: winnerId });
};

export const startMatch = async (tournamentId, matchId) => {
  return api.post(`/tournaments/${tournamentId}/matches/${matchId}/start`);
};
