import axios from "./axios";

// token
export const setToken = (token) =>
  (axios.defaults.headers.common["Authorization"] = `Bearer ${token}`);

export const removeToken = () => {
  delete axios.defaults.headers.common["Authorization"];
};

// users
export const getMyUserInfo = async () => axios.get("/users/me");

export const createUser = async (data) => axios.post("/users", data);

export const updateUser = async (userId, data) => axios.put(`/users/${userId}`, data);

export const deleteUser = async () => axios.delete("/users");

// pteams
export const createPTeam = async (data) => axios.post("/pteams", data);

export const getPTeam = async (pteamId) => axios.get(`/pteams/${pteamId}`);

export const updatePTeam = async (pteamId, data) => axios.put(`/pteams/${pteamId}`, data);

export const getPTeamMembers = async (pteamId) => axios.get(`/pteams/${pteamId}/members`);

export const deletePTeamMember = async (pteamId, userId) =>
  axios.delete(`/pteams/${pteamId}/members/${userId}`);

export const getPTeamAuthInfo = async () => axios.get("/pteams/auth_info");

export const getPTeamAuth = async (pteamId) => axios.get(`/pteams/${pteamId}/authority`);

export const updatePTeamAuth = async (pteamId, data) =>
  axios.post(`/pteams/${pteamId}/authority`, data);

export const getPTeamTag = async (pteamId, tagId) => axios.get(`/pteams/${pteamId}/tags/${tagId}`);

export const getPTeamTopics = async (pteamId) => axios.get(`/pteams/${pteamId}/topics`);

export const getPTeamServiceTaggedTicketIds = async (pteamId, serviceId, tagId) =>
  axios.get(`/pteams/${pteamId}/services/${serviceId}/tags/${tagId}/ticket_ids`);

export const createPTeamInvitation = async (pteamId, data) =>
  axios.post(`/pteams/${pteamId}/invitation`, data);

export const getPTeamInvited = async (tokenId) => axios.get(`/pteams/invitation/${tokenId}`);

export const applyPTeamInvitation = async (tokenId) =>
  axios.post("/pteams/apply_invitation", { invitation_id: tokenId });

export const createTopicStatus = async (pteamId, topicId, tagId, data) => {
  return axios.post(`/pteams/${pteamId}/topicstatus/${topicId}/${tagId}`, data);
};

export const getPTeamTopicStatus = async (pteamId, topicId, tagId) =>
  axios.get(`/pteams/${pteamId}/topicstatus/${topicId}/${tagId}`);

export const getPTeamTopicStatusesSummary = async (pteamId, tagId) =>
  axios.get(`/pteams/${pteamId}/topicstatusessummary/${tagId}`);

export const getPTeamTopicActions = async (pteamId, topicId) =>
  axios.get(`/topics/${topicId}/actions/pteam/${pteamId}`);

export const removeWatcherATeam = async (pteamId, ateamId) =>
  axios.delete(`/pteams/${pteamId}/watchers/${ateamId}`);

export const getPTeamServiceTagsSummary = async (pteamId, serviceId) =>
  axios.get(`/pteams/${pteamId}/services/${serviceId}/tags/summary`);

export const uploadSBOMFile = async (pteamId, service, file, forceMode = true) => {
  const formData = new FormData();
  formData.append("file", file);
  const paramData = {
    service: service,
    force_mode: forceMode,
  };
  return axios.post(`/pteams/${pteamId}/upload_sbom_file`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    params: paramData,
  });
};

export const autoClose = async (pteamId) => axios.post(`/pteams/${pteamId}/fix_status_mismatch`);

export const autoCloseTag = async (pteamId, tagId) =>
  axios.post(`/pteams/${pteamId}/tags/${tagId}/fix_status_mismatch`);

// ateams
export const updateATeam = async (ateamId, data) => axios.put(`/ateams/${ateamId}`, data);

export const createATeam = async (data) => axios.post("/ateams", data);

export const getATeam = async (ateamId) => axios.get(`/ateams/${ateamId}`);

export const getATeamMembers = async (ateamId) => axios.get(`/ateams/${ateamId}/members`);

export const deleteATeamMember = async (ateamId, userId) =>
  axios.delete(`/ateams/${ateamId}/members/${userId}`);

export const createATeamInvitation = async (ateamId, data) =>
  axios.post(`/ateams/${ateamId}/invitation`, data);

export const getATeamInvited = async (tokenId) => axios.get(`/ateams/invitation/${tokenId}`);

export const applyATeamInvitation = async (tokenId) =>
  axios.post("/ateams/apply_invitation", { invitation_id: tokenId });

export const getATeamAuthInfo = async () => axios.get("/ateams/auth_info");

export const getATeamAuth = async (ateamId) => axios.get(`/ateams/${ateamId}/authority`);

export const updateATeamAuth = async (ateamId, data) =>
  axios.post(`/ateams/${ateamId}/authority`, data);

export const removeWatchingPTeam = async (ateamId, pteamId) =>
  axios.delete(`/ateams/${ateamId}/watching_pteams/${pteamId}`);

export const createATeamWatchingRequest = async (ateamId, data) =>
  axios.post(`/ateams/${ateamId}/watching_request`, data);

export const getATeamRequested = async (tokenId) =>
  axios.get(`/ateams/watching_request/${tokenId}`);

export const applyATeamWatchingRequest = async (data) =>
  axios.post("/ateams/apply_watching_request", data);

export const getATeamTopics = async (ateamId, params) =>
  axios.get(`/ateams/${ateamId}/topicstatus`, { params: params ?? {} });

export const getATeamTopicComments = async (ateamId, topicId) =>
  axios.get(`/ateams/${ateamId}/topiccomment/${topicId}`);

export const createATeamTopicComment = async (ateamId, topicId, data) =>
  axios.post(`/ateams/${ateamId}/topiccomment/${topicId}`, data);

export const updateATeamTopicComment = async (ateamId, topicId, commentId, data) =>
  axios.put(`/ateams/${ateamId}/topiccomment/${topicId}/${commentId}`, data);

export const deleteATeamTopicComment = async (ateamId, topicId, commentId) =>
  axios.delete(`/ateams/${ateamId}/topiccomment/${topicId}/${commentId}`);

// topics
export const getTopic = async (topicId) => axios.get(`/topics/${topicId}`);

export const createTopic = async (topicId, data) => axios.post(`/topics/${topicId}`, data);

export const updateTopic = async (topicId, data) => axios.put(`/topics/${topicId}`, data);

export const deleteTopic = async (topicId) => axios.delete(`/topics/${topicId}`);

export const searchTopics = async (params) => axios.get("topics/search", { params: params ?? {} });

export const getUserTopicActions = async (topicId) =>
  axios.get(`/topics/${topicId}/actions/user/me`);

export const fetchFlashsense = async (topicId) => axios.get(`/topics/fetch_fs/${topicId}`);

// actions
export const createAction = async (data) => axios.post("/actions", data);

export const updateAction = async (actionId, data) => axios.put(`/actions/${actionId}`, data);

export const deleteAction = async (actionId) => axios.delete(`/actions/${actionId}`);

// tags
export const getTags = async () => axios.get("/tags");

export const createTag = async (data) => axios.post("/tags", data);

// actionlogs
export const createActionLog = async (data) => axios.post("/actionlogs", data);

// external
export const checkSlack = async (data) => axios.post("/external/slack/check", data);

export const checkMail = async (data) => axios.post("/external/email/check", data);

export const checkFs = async () => axios.post("/external/flashsense/check");

export const getFsInfo = async () => axios.get("/external/flashsense/info");
