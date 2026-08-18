import { useEffect, useRef, useState } from "react";

import { getApiErrorMessage } from "../api/apiClient";
import Alert from "../components/Alert";
import BookingDetails from "../components/BookingDetails";
import BookingLookupForm from "../components/BookingLookupForm";
import { cancelBooking, getBooking } from "../services/bookingService";

import ConfirmationModal from "../components/ConfirmationModal";

export default function ManageBookingPage({ initialBookingReference = "" }) {
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [cancellationModalOpen, setCancellationModalOpen] = useState(false);

  const lastAutomaticReference = useRef("");

  useEffect(() => {
    if (
      !initialBookingReference ||
      lastAutomaticReference.current === initialBookingReference
    ) {
      return;
    }

    lastAutomaticReference.current = initialBookingReference;

    handleLookup(initialBookingReference);
  }, [initialBookingReference]);

  async function handleLookup(bookingReference) {
    try {
      setError("");
      setSuccessMessage("");
      setBooking(null);
      setLoading(true);

      const result = await getBooking(bookingReference);

      setBooking(result);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  function openCancellationModal() {
    if (!booking || cancelling) {
      return;
    }

    setCancellationModalOpen(true);
  }

  function closeCancellationModal() {
    if (cancelling) {
      return;
    }

    setCancellationModalOpen(false);
  }

  async function handleConfirmCancellation() {
    if (!booking) {
      return;
    }

    try {
      setError("");
      setSuccessMessage("");
      setCancelling(true);

      const updatedBooking = await cancelBooking(booking.booking_reference);

      setBooking(updatedBooking);
      setCancellationModalOpen(false);

      setSuccessMessage("The booking was cancelled successfully.");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setCancelling(false);
    }
  }

  return (
    <main className="page-container">
      <section className="hero manage-hero">
        <span className="eyebrow">Existing reservations</span>

        <h2>Retrieve or cancel your booking</h2>

        <p>
          Use your booking reference to view the passenger, train, journey,
          fare, and seat details.
        </p>
      </section>

      <BookingLookupForm
        loading={loading}
        onSubmit={handleLookup}
        initialBookingReference={initialBookingReference}
      />

      <BookingDetails
        booking={booking}
        cancelling={cancelling}
        onCancel={openCancellationModal}
      />
      <ConfirmationModal
        open={cancellationModalOpen}
        title="Cancel this booking?"
        message={
          booking
            ? `Booking ${booking.booking_reference} will be cancelled and the reserved seat will become available for this journey segment. This action cannot be undone.`
            : ""
        }
        confirmText="Yes, cancel booking"
        cancelText="Keep booking"
        loading={cancelling}
        onConfirm={handleConfirmCancellation}
        onCancel={closeCancellationModal}
      />

      <Alert type="error" message={error} onClose={() => setError("")} />

      <Alert
        type="success"
        message={successMessage}
        onClose={() => setSuccessMessage("")}
      />
    </main>
  );
}
