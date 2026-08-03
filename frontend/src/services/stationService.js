import apiClient from "../api/apiClient";

export async function getStations() {
  const response = await apiClient.get("/stations");

  return response.data;
}
