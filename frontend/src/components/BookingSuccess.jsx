import CopyButton from "./CopyButton";

import {
  formatCurrency,
  formatDateTime,
  formatDirection,
} from "../utils/formatters";

export default function BookingSuccess({
  booking,
  onBookAnother,
  onManageBooking,
}) {
  if (!booking) {
    return null;
  }

  return (
    <section className="booking-success-wrapper">
      <div className="success-heading">
        <div className="success-icon">✓</div>

        <span className="eyebrow">Booking confirmed</span>

        <h2>Your train ticket is ready</h2>

        <p>
          Save your booking reference to retrieve or cancel this reservation
          later.
        </p>
      </div>

      <article className="train-ticket">
        <header className="ticket-header">
          <div>
            <span className="ticket-company">TRAINSEAT</span>

            <h3>Reserved Train Ticket</h3>
          </div>

          <span className="ticket-status">{booking.status}</span>
        </header>

        <section className="ticket-route">
          <div className="ticket-station">
            <span>From</span>

            <strong>{booking.origin_station.name}</strong>

            <small>{booking.origin_station.code}</small>
          </div>

          <div className="ticket-route-center">
            {/* <span className="ticket-route-line" /> */}

            <span className="ticket-train-icon" aria-hidden="true">
              →
            </span>
          </div>

          <div className="ticket-station ticket-station-end">
            <span>To</span>

            <strong>{booking.destination_station.name}</strong>

            <small>{booking.destination_station.code}</small>
          </div>
        </section>

        <section className="ticket-details-grid">
          <div>
            <span>Passenger</span>

            <strong>{booking.passenger_name}</strong>
          </div>

          <div>
            <span>Train</span>

            <strong>{booking.trip.train_number}</strong>

            <small>{booking.trip.train_name}</small>
          </div>

          <div>
            <span>Direction</span>

            <strong>{formatDirection(booking.trip.direction)}</strong>
          </div>

          <div>
            <span>Reserved seat</span>

            <strong>
              Coach {booking.seat.coach_number}, Seat {booking.seat.seat_number}
            </strong>
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
            <span>Fare</span>

            <strong>{formatCurrency(booking.fare)}</strong>
          </div>

          <div>
            <span>Email</span>

            <strong>{booking.passenger_email || "Not provided"}</strong>
          </div>
        </section>

        <footer className="ticket-footer">
          <div className="ticket-reference">
            <span>Booking reference</span>

            <strong>{booking.booking_reference}</strong>
          </div>

          <CopyButton
            value={booking.booking_reference}
            label="Copy reference"
          />
        </footer>
      </article>

      <div className="success-actions">
        <button
          type="button"
          className="primary-button"
          onClick={onBookAnother}
        >
          Book another journey
        </button>

        <button
          type="button"
          className="secondary-button"
          onClick={() => onManageBooking(booking.booking_reference)}
        >
          Manage this booking
        </button>
      </div>
    </section>
  );
}
