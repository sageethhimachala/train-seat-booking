export default function SeatCard({ seat, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`seat-card ${selected ? "seat-card-selected" : ""}`}
      onClick={() => onSelect(seat)}
      aria-pressed={selected}
    >
      <span className="seat-icon" aria-hidden="true">
        ▣
      </span>

      <strong>Seat {seat.seat_number}</strong>

      <span>Coach {seat.coach_number}</span>
    </button>
  );
}
