import axios from "./axios";

// token
export const setToken = (token) =>
  (axios.defaults.headers.common["Authorization"] = `Bearer ${token}`);

export const removeToken = () => {
  delete axios.defaults.headers.common["Authorization"];
};

// pteams
export const getPTeamTagsSummary = async (pteamId) => axios.get(`/pteams/${pteamId}/tags/summary`);

export const getATeamTopics = async (ateamId, params) =>
  axios.get(`/ateams/${ateamId}/topicstatus`, { params: params ?? {} });

// topics
export const fetchFlashsense = async (topicId) => axios.get(`/topics/fetch_fs/${topicId}`);

// external
export const checkFs = async () => axios.post("/external/flashsense/check");

export const getFsInfo = async () => axios.get("/external/flashsense/info");
