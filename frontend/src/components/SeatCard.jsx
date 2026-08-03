export default function SeatCard({ seat, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`seat-card ${selected ? "seat-card-selected" : ""}`}
      onClick={() => onSelect(seat)}
      aria-pressed={selected}
      aria-label={`Coach ${seat.coach_number}, seat ${seat.seat_number}`}
    >
      <span className="seat-back" aria-hidden="true" />

      <span className="seat-number">{seat.seat_number}</span>

      <span className="seat-coach-label">Coach {seat.coach_number}</span>

      {selected && (
        <span className="seat-selected-mark" aria-hidden="true">
          ✓
        </span>
      )}
    </button>
  );
}
