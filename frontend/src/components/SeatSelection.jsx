import SeatCard from "./SeatCard";
import TripSummary from "./TripSummary";

export default function SeatSelection({
  availability,
  selectedSeat,
  onSelectSeat,
}) {
  if (!availability) {
    return null;
  }

  if (!availability.trip) {
    return (
      <section className="card empty-state">
        <div className="empty-icon">!</div>
        <h2>No seats available</h2>
        <p>{availability.message}</p>
      </section>
    );
  }

  const groupedSeats = availability.available_seats.reduce((groups, seat) => {
    const coachNumber = seat.coach_number;

    if (!groups[coachNumber]) {
      groups[coachNumber] = [];
    }

    groups[coachNumber].push(seat);

    return groups;
  }, {});

  return (
    <section className="card">
      <div className="section-heading">
        <span className="step-number">2</span>

        <div>
          <h2>Select a reserved seat</h2>
          <p>
            Seats shown below are available for your selected journey segment.
          </p>
        </div>
      </div>

      <TripSummary availability={availability} />

      <div className="seat-legend">
        <span>
          <i className="legend-seat" />
          Available
        </span>

        <span>
          <i className="legend-seat legend-selected" />
          Selected
        </span>
      </div>

      <div className="coach-list">
        {Object.entries(groupedSeats).map(([coachNumber, seats]) => (
          <section className="coach-section" key={coachNumber}>
            <div className="coach-heading">
              <h3>Reserved Coach {coachNumber}</h3>
              <span>{seats.length} seats available</span>
            </div>

            <div className="seat-grid">
              {seats.map((seat) => (
                <SeatCard
                  key={seat.seat_id}
                  seat={seat}
                  selected={selectedSeat?.seat_id === seat.seat_id}
                  onSelect={onSelectSeat}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}
