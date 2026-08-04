export default function Header({ activePage, onNavigate }) {
  return (
    <header className="site-header">
      <div className="header-content">
        <button
          type="button"
          className="brand-button"
          onClick={() => onNavigate("booking")}
          aria-label="Go to booking page"
        >
          <img src="/favicon.svg" alt="TrainSeat logo" className="brand-logo" />

          <span className="brand-text">
            <strong>TrainSeat</strong>
            <small>segment based reserved seat booking</small>
          </span>
        </button>

        <nav className="main-navigation" aria-label="Main navigation">
          <button
            type="button"
            className={
              activePage === "booking"
                ? "nav-button nav-button-active"
                : "nav-button"
            }
            onClick={() => onNavigate("booking")}
          >
            Book a seat
          </button>

          <button
            type="button"
            className={
              activePage === "manage"
                ? "nav-button nav-button-active"
                : "nav-button"
            }
            onClick={() => onNavigate("manage")}
          >
            Manage booking
          </button>
        </nav>
      </div>
    </header>
  );
}
