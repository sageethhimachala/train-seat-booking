import { useEffect, useState } from "react";

export default function BookingLookupForm({
  loading,
  onSubmit,
  initialBookingReference = "",
}) {
  const [bookingReference, setBookingReference] = useState(
    initialBookingReference,
  );

  useEffect(() => {
    setBookingReference(initialBookingReference);
  }, [initialBookingReference]);

  function handleSubmit(event) {
    event.preventDefault();

    const normalizedReference = bookingReference.trim().toUpperCase();

    if (!normalizedReference) {
      return;
    }

    onSubmit(normalizedReference);
  }

  return (
    <section className="card">
      <div className="section-heading">
        <span className="step-number">1</span>

        <div>
          <h2>Find your booking</h2>

          <p>Enter the booking reference shown on your confirmation.</p>
        </div>
      </div>

      <form className="lookup-form" onSubmit={handleSubmit}>
        <label className="form-field">
          <span>Booking reference</span>

          <input
            type="text"
            value={bookingReference}
            onChange={(event) =>
              setBookingReference(event.target.value.toUpperCase())
            }
            placeholder="TRN-XXXXXXXX"
            maxLength={20}
            autoComplete="off"
            disabled={loading}
            required
          />
        </label>

        <button
          type="submit"
          className="primary-button"
          disabled={loading || bookingReference.trim().length === 0}
        >
          {loading ? "Searching..." : "Find booking"}
        </button>
      </form>
    </section>
  );
}
