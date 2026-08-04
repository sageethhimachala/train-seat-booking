import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",

  headers: {
    "Content-Type": "application/json",
  },

  timeout: 10000,
});

export function getApiErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  if (error.code === "ECONNABORTED") {
    return "The request took too long. Please try again.";
  }

  if (error.request) {
    return "The server could not be reached. " + "Please try again shortly.";
  }

  return error.message || "An unexpected error occurred.";
}

export default apiClient;
