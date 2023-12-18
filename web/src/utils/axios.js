import axios from "axios";

const DEFAULT_API_CONFIG = {
  baseURL: process.env.REACT_APP_API_BASE_URL,
  headers: {
    "Access-Control-Allow-Origin": "*",
  },
  timeout: 30000,
  paramsSerializer: { indexes: null },
};

const instance = axios.create({ ...DEFAULT_API_CONFIG });

export default instance;
