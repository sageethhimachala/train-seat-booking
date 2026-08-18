export const stations = [
  {
    id: 1,
    name: "Colombo Fort",
    code: "FOT",
    order_index: 0,
    distance_from_start_km: "0.00",
  },
  {
    id: 2,
    name: "Ragama",
    code: "RGM",
    order_index: 1,
    distance_from_start_km: "13.70",
  },
  {
    id: 3,
    name: "Kandy",
    code: "KDT",
    order_index: 2,
    distance_from_start_km: "120.70",
  },
  {
    id: 4,
    name: "Badulla",
    code: "BAD",
    order_index: 3,
    distance_from_start_km: "292.30",
  },
];

export const availability = {
  origin_station_id: 1,
  origin_station_name: "Colombo Fort",

  destination_station_id: 3,
  destination_station_name: "Kandy",

  distance_km: "120.70",
  estimated_fare: "362.10",

  message: "Seats available.",

  trip: {
    trip_id: 10,
    train_id: 1,
    train_number: "1005",
    train_name: "Podi Menike",
    direction: "FORWARD",
    departure_time: "2026-08-20T03:00:00Z",
    arrival_time: "2026-08-20T13:00:00Z",
  },

  available_seats: [
    {
      seat_id: 1,
      coach_number: 1,
      seat_number: "01",
    },
    {
      seat_id: 2,
      coach_number: 1,
      seat_number: "02",
    },
    {
      seat_id: 3,
      coach_number: 1,
      seat_number: "03",
    },
    {
      seat_id: 4,
      coach_number: 1,
      seat_number: "04",
    },
  ],
};

export const booking = {
  booking_reference: "TRN-ABC12345",
  status: "CONFIRMED",

  passenger_name: "Test Passenger",
  passenger_email: "test@example.com",

  fare: "362.10",

  created_at: "2026-08-18T08:00:00Z",
  cancelled_at: null,

  origin_station: {
    id: 1,
    name: "Colombo Fort",
    code: "FOT",
  },

  destination_station: {
    id: 3,
    name: "Kandy",
    code: "KDT",
  },

  seat: {
    seat_id: 1,
    coach_number: 1,
    seat_number: "01",
  },

  trip: {
    trip_id: 10,
    train_number: "1005",
    train_name: "Podi Menike",
    direction: "FORWARD",
    departure_time: "2026-08-20T03:00:00Z",
    arrival_time: "2026-08-20T13:00:00Z",
  },
};

export const cancelledBooking = {
  ...booking,

  status: "CANCELLED",

  cancelled_at: "2026-08-18T09:00:00Z",
};
