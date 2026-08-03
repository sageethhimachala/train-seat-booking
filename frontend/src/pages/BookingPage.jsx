import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/apiClient";
import Alert from "../components/Alert";
import BookingForm from "../components/BookingForm";
import BookingSuccess from "../components/BookingSuccess";
import LoadingSpinner from "../components/LoadingSpinner";
import SearchForm from "../components/SearchForm";
import SeatSelection from "../components/SeatSelection";
import { searchAvailability } from "../services/availabilityService";
import { createBooking } from "../services/bookingService";
import { getStations } from "../services/stationService";

export default function BookingPage({ onManageBooking }) {
  const [stations, setStations] = useState([]);
  const [availability, setAvailability] = useState(null);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [booking, setBooking] = useState(null);

  const [loadingStations, setLoadingStations] = useState(true);
  const [searchingAvailability, setSearchingAvailability] = useState(false);
  const [creatingBooking, setCreatingBooking] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadStations() {
      try {
        setError("");

        const stationData = await getStations();

        setStations(stationData);
      } catch (requestError) {
        setError(getApiErrorMessage(requestError));
      } finally {
        setLoadingStations(false);
      }
    }

    loadStations();
  }, []);

  async function handleSearch({ originStationId, destinationStationId }) {
    try {
      setError("");
      setBooking(null);
      setSelectedSeat(null);
      setAvailability(null);
      setSearchingAvailability(true);

      const result = await searchAvailability(
        originStationId,
        destinationStationId,
      );

      setAvailability(result);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setSearchingAvailability(false);
    }
  }

  async function handleCreateBooking(bookingData) {
    try {
      setError("");
      setCreatingBooking(true);

      const result = await createBooking(bookingData);

      setBooking(result);
      setAvailability(null);
      setSelectedSeat(null);

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (requestError) {
      const status = requestError.response?.status;

      if (status === 409 && availability) {
        setSelectedSeat(null);

        setError(
          getApiErrorMessage(requestError) +
            " Please search again to refresh availability.",
        );
      } else {
        setError(getApiErrorMessage(requestError));
      }
    } finally {
      setCreatingBooking(false);
    }
  }

  function handleBookAnother() {
    setBooking(null);
    setAvailability(null);
    setSelectedSeat(null);
    setError("");
  }

  if (loadingStations) {
    return (
      <main className="page-container">
        <LoadingSpinner message="Loading stations..." />
      </main>
    );
  }

  if (booking) {
    return (
      <main className="page-container">
        <BookingSuccess
          booking={booking}
          onBookAnother={handleBookAnother}
          onManageBooking={onManageBooking}
        />
      </main>
    );
  }

  return (
    <main className="page-container">
      <section className="hero">
        <span className="eyebrow">Colombo Fort–Badulla railway line</span>

        <h2>Reserve one seat for exactly the journey you travel</h2>

        <p>
          Find available reserved seats for your selected segment and book the
          next eligible train.
        </p>
      </section>

      <Alert type="error" message={error} onClose={() => setError("")} />

      <SearchForm
        stations={stations}
        loading={searchingAvailability}
        onSearch={handleSearch}
      />

      {searchingAvailability && (
        <LoadingSpinner message="Finding the earliest train with available seats..." />
      )}

      {!searchingAvailability && (
        <SeatSelection
          availability={availability}
          selectedSeat={selectedSeat}
          onSelectSeat={setSelectedSeat}
        />
      )}

      <BookingForm
        selectedSeat={selectedSeat}
        availability={availability}
        loading={creatingBooking}
        onSubmit={handleCreateBooking}
      />
    </main>
  );
}
