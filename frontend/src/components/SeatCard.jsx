export default function SeatCard({ seat, selected, onSelect }) {
  const isBooked = !seat.is_available;

  function handleClick() {
    if (isBooked) {
      return;
    }

    onSelect(seat);
  }

  return (
    <button
      type="button"
      className={[
        "seat-card",
        selected ? "seat-card-selected" : "",
        isBooked ? "seat-card-booked" : "",
      ]
        .filter(Boolean)
        .join(" ")}
      onClick={handleClick}
      disabled={isBooked}
      aria-pressed={selected}
      aria-label={
        isBooked
          ? `Coach ${seat.coach_number}, seat ${seat.seat_number}, booked`
          : `Coach ${seat.coach_number}, seat ${seat.seat_number}, available`
      }
    >
      <span className="seat-back" aria-hidden="true" />

      <span className="seat-number">{seat.seat_number}</span>

      <span className="seat-coach-label">Coach {seat.coach_number}</span>

      {selected && (
        <span className="seat-selected-mark" aria-hidden="true">
          ✓
        </span>
      )}

      {isBooked && <span className="seat-status-label">Booked</span>}
    </button>
  );
}
