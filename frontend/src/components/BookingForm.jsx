import { useEffect, useState } from "react";
import { formatCurrency } from "../utils/formatters";

const INITIAL_FORM = {
  passengerName: "",
  passengerEmail: "",
};

export default function BookingForm({
  selectedSeat,
  availability,
  loading,
  onSubmit,
}) {
  const [formData, setFormData] = useState(INITIAL_FORM);

  useEffect(() => {
    setFormData(INITIAL_FORM);
  }, [selectedSeat?.seat_id]);

  if (!selectedSeat || !availability?.trip) {
    return null;
  }

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    onSubmit({
      trip_id: availability.trip.trip_id,
      seat_id: selectedSeat.seat_id,
      origin_station_id: availability.origin_station_id,
      destination_station_id: availability.destination_station_id,
      passenger_name: formData.passengerName.trim(),
      passenger_email: formData.passengerEmail.trim(),
    });
  }

  const formIsValid =
    formData.passengerName.trim().length >= 2 &&
    formData.passengerEmail.includes("@");

  return (
    <section className="card">
      <div className="section-heading">
        <span className="step-number">3</span>

        <div>
          <h2>Passenger details</h2>
          <p>Enter the passenger information to confirm the reservation.</p>
        </div>
      </div>

      <div className="selected-seat-summary">
        <div>
          <span>Selected seat</span>
          <strong>
            Coach {selectedSeat.coach_number}, Seat {selectedSeat.seat_number}
          </strong>
        </div>

        <div>
          <span>Fare</span>
          <strong>{formatCurrency(availability.estimated_fare)}</strong>
        </div>
      </div>

      <form className="booking-form" onSubmit={handleSubmit}>
        <label className="form-field">
          <span>Passenger name</span>

          <input
            type="text"
            name="passengerName"
            value={formData.passengerName}
            onChange={handleChange}
            minLength={2}
            maxLength={150}
            placeholder="Enter passenger name"
            autoComplete="name"
            required
            disabled={loading}
          />
        </label>

        <label className="form-field">
          <span>Email address</span>

          <input
            type="email"
            name="passengerEmail"
            value={formData.passengerEmail}
            onChange={handleChange}
            placeholder="passenger@example.com"
            autoComplete="email"
            required
            disabled={loading}
          />
        </label>

        <button
          type="submit"
          className="primary-button"
          disabled={!formIsValid || loading}
        >
          {loading ? "Confirming booking..." : "Confirm booking"}
        </button>
      </form>
    </section>
  );
}
