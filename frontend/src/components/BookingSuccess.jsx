import { formatCurrency, formatDateTime } from "../utils/formatters";

export default function BookingSuccess({ booking, onBookAnother }) {
  if (!booking) {
    return null;
  }

  return (
    <section className="card success-card">
      <div className="success-icon">✓</div>

      <span className="eyebrow">Booking confirmed</span>

      <h2>Your reserved seat is confirmed</h2>

      <p className="success-message">
        Keep your booking reference safe. You will need it to retrieve or cancel
        this booking.
      </p>

      <div className="booking-reference">
        <span>Booking reference</span>
        <strong>{booking.booking_reference}</strong>
      </div>

      <div className="confirmation-grid">
        <div>
          <span>Passenger</span>
          <strong>{booking.passenger_name}</strong>
        </div>

        <div>
          <span>Train</span>
          <strong>
            {booking.trip.train_number} — {booking.trip.train_name}
          </strong>
        </div>

        <div>
          <span>Journey</span>
          <strong>
            {booking.origin_station.name} to {booking.destination_station.name}
          </strong>
        </div>

        <div>
          <span>Departure</span>
          <strong>{formatDateTime(booking.trip.departure_time)}</strong>
        </div>

        <div>
          <span>Reserved seat</span>
          <strong>
            Coach {booking.seat.coach_number}, Seat {booking.seat.seat_number}
          </strong>
        </div>

        <div>
          <span>Fare</span>
          <strong>{formatCurrency(booking.fare)}</strong>
        </div>
      </div>

      <button type="button" className="primary-button" onClick={onBookAnother}>
        Book another journey
      </button>
    </section>
  );
}
