import SeatCard from "./SeatCard";
import TripSummary from "./TripSummary";

function splitSeatsIntoRows(seats) {
  const rows = [];

  for (let index = 0; index < seats.length; index += 4) {
    rows.push(seats.slice(index, index + 4));
  }

  return rows;
}

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

          <p>Choose an available seat for your selected journey segment.</p>
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

        <span>
          <i className="legend-seat legend-booked" />
          Booked
        </span>
      </div>

      <div className="coach-list">
        {Object.entries(groupedSeats).map(([coachNumber, seats]) => {
          const rows = splitSeatsIntoRows(seats);

          return (
            <section className="coach-section" key={coachNumber}>
              <div className="coach-heading">
                <div>
                  <h3>Reserved Coach {coachNumber}</h3>

                  <span>
                    {seats.filter((seat) => seat.is_available).length} seats
                    available
                  </span>
                </div>

                <span className="coach-direction">Front of train →</span>
              </div>

              <div className="coach-shell">
                <div className="coach-end-label">Coach {coachNumber}</div>

                <div className="seat-map">
                  {rows.map((row, rowIndex) => {
                    const leftSeats = row.slice(0, 2);
                    const rightSeats = row.slice(2, 4);

                    return (
                      <div className="seat-row" key={rowIndex}>
                        <div className="seat-pair">
                          {leftSeats.map((seat) => (
                            <SeatCard
                              key={seat.seat_id}
                              seat={seat}
                              selected={selectedSeat?.seat_id === seat.seat_id}
                              onSelect={onSelectSeat}
                            />
                          ))}
                        </div>

                        <div className="coach-aisle">
                          <span>Aisle</span>
                        </div>

                        <div className="seat-pair">
                          {rightSeats.map((seat) => (
                            <SeatCard
                              key={seat.seat_id}
                              seat={seat}
                              selected={selectedSeat?.seat_id === seat.seat_id}
                              onSelect={onSelectSeat}
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="coach-end-label">Exit</div>
              </div>
            </section>
          );
        })}
      </div>
    </section>
  );
}
