import {
  formatCurrency,
  formatDateTime,
  formatDirection,
} from "../utils/formatters";

export default function BookingDetails({ booking, cancelling, onCancel }) {
  if (!booking) {
    return null;
  }

  const isCancelled = booking.status === "CANCELLED";

  return (
    <section className="card booking-details-card">
      <div className="booking-details-header">
        <div>
          <span className="eyebrow">Booking details</span>

          <h2>{booking.booking_reference}</h2>
        </div>

        <span
          className={
            isCancelled
              ? "booking-status booking-status-cancelled"
              : "booking-status booking-status-confirmed"
          }
        >
          {booking.status}
        </span>
      </div>

      <div className="booking-passenger">
        <div>
          <span>Passenger</span>
          <strong>{booking.passenger_name}</strong>
        </div>

        <div>
          <span>Email</span>
          <strong>{booking.passenger_email || "Not provided"}</strong>
        </div>
      </div>

      <div className="management-route">
        <div className="management-station">
          <span>Origin</span>
          <strong>{booking.origin_station.name}</strong>
          <small>{booking.origin_station.code}</small>
        </div>

        <div className="management-route-line">
          <span className="route-dot" />
          <span className="route-track" />
          <span className="route-arrow">›</span>
        </div>

        <div className="management-station management-station-end">
          <span>Destination</span>
          <strong>{booking.destination_station.name}</strong>
          <small>{booking.destination_station.code}</small>
        </div>
      </div>

      <div className="booking-information-grid">
        <div>
          <span>Train</span>

          <strong>
            {booking.trip.train_number} — {booking.trip.train_name}
          </strong>
        </div>

        <div>
          <span>Direction</span>

          <strong>{formatDirection(booking.trip.direction)}</strong>
        </div>

        <div>
          <span>Departure</span>

          <strong>{formatDateTime(booking.trip.departure_time)}</strong>
        </div>

        <div>
          <span>Arrival</span>

          <strong>{formatDateTime(booking.trip.arrival_time)}</strong>
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

        <div>
          <span>Booked at</span>

          <strong>{formatDateTime(booking.created_at)}</strong>
        </div>

        <div>
          <span>Cancelled at</span>

          <strong>
            {booking.cancelled_at
              ? formatDateTime(booking.cancelled_at)
              : "Not cancelled"}
          </strong>
        </div>
      </div>

      {!isCancelled && (
        <div className="cancellation-section">
          <div>
            <h3>Cancel this booking</h3>

            <p>
              Cancellation is allowed only before the train leaves its starting
              station.
            </p>
          </div>

          <button
            type="button"
            className="danger-button"
            onClick={onCancel}
            disabled={cancelling}
          >
            {cancelling ? "Cancelling..." : "Cancel booking"}
          </button>
        </div>
      )}

      {isCancelled && (
        <div className="cancelled-notice">
          This booking has been cancelled. The seat is now available for another
          passenger on this journey segment.
        </div>
      )}
    </section>
  );
}
