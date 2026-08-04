import {
  formatCurrency,
  formatDateTime,
  formatDirection,
} from "../utils/formatters";

export default function TripSummary({ availability }) {
  if (!availability?.trip) {
    return null;
  }

  const { trip } = availability;

  return (
    <section className="trip-summary">
      <div className="trip-summary-header">
        <div>
          <span className="eyebrow">Earliest train with available seats</span>

          <h3>
            {trip.train_number} : {trip.train_name}
          </h3>
        </div>

        <span className="status-badge">{trip.direction}</span>
      </div>

      <div className="trip-route">
        <div className="route-station">
          <span className="route-label">From</span>
          <strong>{availability.origin_station_name}</strong>
        </div>

        <div className="route-line">
          <span className="route-dot" />
          <span className="route-track" />
          <span className="route-dot" />
        </div>

        <div className="route-station route-station-end">
          <span className="route-label">To</span>
          <strong>{availability.destination_station_name}</strong>
        </div>
      </div>

      <div className="trip-details-grid">
        <div>
          <span>Direction</span>
          <strong>{formatDirection(trip.direction)}</strong>
        </div>

        <div>
          <span>Departure</span>
          <strong>{formatDateTime(trip.departure_time)}</strong>
        </div>

        <div>
          <span>Arrival</span>
          <strong>{formatDateTime(trip.arrival_time)}</strong>
        </div>

        <div>
          <span>Distance</span>
          <strong>{availability.distance_km} km</strong>
        </div>

        <div>
          <span>Fare</span>
          <strong>{formatCurrency(availability.estimated_fare)}</strong>
        </div>

        <div>
          <span>Available seats</span>
          <strong>{availability.available_seats.length}</strong>
        </div>
      </div>
    </section>
  );
}
