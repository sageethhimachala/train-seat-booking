import apiClient from "../api/apiClient";

export async function createBooking(bookingData) {
  const response = await apiClient.post("/bookings", bookingData);

  return response.data;
}

export async function getBooking(bookingReference) {
  const response = await apiClient.get(
    `/bookings/${encodeURIComponent(bookingReference)}`,
  );

  return response.data;
}

export async function cancelBooking(bookingReference) {
  const response = await apiClient.post(
    `/bookings/${encodeURIComponent(bookingReference)}/cancel`,
  );

  return response.data;
}
