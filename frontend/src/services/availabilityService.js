import apiClient from "../api/apiClient";

export async function searchAvailability(
  originStationId,
  destinationStationId,
) {
  const response = await apiClient.get("/availability", {
    params: {
      origin_station_id: originStationId,
      destination_station_id: destinationStationId,
    },
  });

  return response.data;
}
