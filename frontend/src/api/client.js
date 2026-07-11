import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

export const HcpAPI = {
  list: () => apiClient.get("/api/hcps/"),
  create: (payload) => apiClient.post("/api/hcps/", payload),
  history: (hcpId) => apiClient.get(`/api/hcps/${hcpId}/interactions`),
};

export const InteractionAPI = {
  list: () => apiClient.get("/api/interactions/"),
  create: (payload) => apiClient.post("/api/interactions/", payload),
  update: (id, payload) => apiClient.put(`/api/interactions/${id}`, payload),
  remove: (id) => apiClient.delete(`/api/interactions/${id}`),
};

export const ChatAPI = {
  send: (payload) => apiClient.post("/api/chat/", payload),
};
