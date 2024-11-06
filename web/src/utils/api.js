import axios from "./axios";

// token
export const setToken = (token) =>
  (axios.defaults.headers.common["Authorization"] = `Bearer ${token}`);

export const removeToken = () => {
  delete axios.defaults.headers.common["Authorization"];
};

// pteams
export const getPTeamAuthInfo = async () => axios.get("/pteams/auth_info");

export const getPTeamAuth = async (pteamId) => axios.get(`/pteams/${pteamId}/authority`);

export const getPTeamServiceTagsSummary = async (pteamId, serviceId) =>
  axios.get(`/pteams/${pteamId}/services/${serviceId}/tags/summary`);

export const getPTeamTagsSummary = async (pteamId) => axios.get(`/pteams/${pteamId}/tags/summary`);

export const getDependencies = async (pteamId, serviceId) =>
  axios.get(`/pteams/${pteamId}/services/${serviceId}/dependencies`);

export const getServiceThumbnail = async (pteamId, serviceId) =>
  axios.get(`/pteams/${pteamId}/services/${serviceId}/thumbnail`, { responseType: "blob" });

// ateams
export const getATeam = async (ateamId) => axios.get(`/ateams/${ateamId}`);

export const getATeamAuthInfo = async () => axios.get("/ateams/auth_info");

export const getATeamAuth = async (ateamId) => axios.get(`/ateams/${ateamId}/authority`);

export const getATeamRequested = async (tokenId) =>
  axios.get(`/ateams/watching_request/${tokenId}`);

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

export const updateTopic = async (topicId, data) => axios.put(`/topics/${topicId}`, data);

export const searchTopics = async (params) => axios.get("topics/search", { params: params ?? {} });

export const fetchFlashsense = async (topicId) => axios.get(`/topics/fetch_fs/${topicId}`);

// tags
export const getTags = async () => axios.get("/tags");

// external
export const checkSlack = async (data) => axios.post("/external/slack/check", data);

export const checkMail = async (data) => axios.post("/external/email/check", data);

export const checkFs = async () => axios.post("/external/flashsense/check");

export const getFsInfo = async () => axios.get("/external/flashsense/info");
