import api from './index';

export const createTeam = async (title, description, logo) => {
    const formData = new FormData();
    formData.append('title', title);
    if (description) formData.append('description', description);
    if (logo) formData.append('logo', logo);
    return api.post('/teams/', formData, { headers: { 'Content-Type': 'multipart/form-data' }, });
};

export const getTeams = async () => {
    return api.get('/teams/');
};

export const getTeam = async (teamId) => {
    return api.get(`/teams/${teamId}`);
};

export const updateTeam = async (teamId, title, description, logo) => {
    const formData = new FormData();
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);
    if (logo) formData.append('logo', logo);
    return api.patch(`/teams/${teamId}`, formData, { headers: { 'Content-Type': 'multipart/form-data' }, });
};

export const deleteTeam = async (teamId) => {
    return api.delete(`/teams/${teamId}`);
};

export const inviteUserToTeam = async (teamId, userId) => {
    return api.post(`/teams/${teamId}/invite`, { user_id: userId });
};

export const acceptTeamInvite = async (requestId) => {
    return api.post(`/teams/invites/${requestId}/accept`);
};

export const declineTeamInvite = async (requestId) => {
    return api.post(`/teams/invites/${requestId}/decline`);
};

export const leaveTeam = async (teamId) => {
    return api.post(`/teams/${teamId}/leave`);
};

export const kickMember = async (teamId, userId) => {
    return api.post(`/teams/${teamId}/kick`, { user_id: userId });
};

export const getTeamMembers = async (teamId) => {
    return api.get(`/teams/${teamId}/members`);
};

export const getUserInvites = async () => {
    return api.get('/teams/invites');
};

export const getUserTeams = async () => {
    return api.get('/teams/me');
};

export const getIncomingTeamInvites = async () => {
    return api.get('/teams/invites/incoming');
};