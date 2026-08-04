import { useMemo, useState } from "react";

export default function SearchForm({ stations, loading, onSearch }) {
  const [originStationId, setOriginStationId] = useState("");

  const [destinationStationId, setDestinationStationId] = useState("");

  const originOptions = useMemo(
    () =>
      stations.filter((station) => String(station.id) !== destinationStationId),
    [stations, destinationStationId],
  );

  const destinationOptions = useMemo(
    () => stations.filter((station) => String(station.id) !== originStationId),
    [stations, originStationId],
  );

  function handleSubmit(event) {
    event.preventDefault();

    if (!originStationId || !destinationStationId) {
      return;
    }

    onSearch({
      originStationId: Number(originStationId),
      destinationStationId: Number(destinationStationId),
    });
  }

  function swapStations() {
    setOriginStationId(destinationStationId);
    setDestinationStationId(originStationId);
  }

  const formIsValid =
    originStationId &&
    destinationStationId &&
    originStationId !== destinationStationId;

  return (
    <section className="card search-card">
      <div className="section-heading">
        <span className="step-number">1</span>

        <div>
          <h2>Plan your journey</h2>
          <p>Select the stations for your reserved seat journey.</p>
        </div>
      </div>

      <form className="search-form" onSubmit={handleSubmit}>
        <div className="station-fields">
          <label className="form-field">
            <span>Origin station</span>

            <select
              value={originStationId}
              onChange={(event) => setOriginStationId(event.target.value)}
              disabled={loading}
            >
              <option value="">Select origin station</option>

              {originOptions.map((station) => (
                <option key={station.id} value={station.id}>
                  {station.name}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            className="swap-button"
            onClick={swapStations}
            disabled={loading || !originStationId || !destinationStationId}
            aria-label="Swap origin and destination"
          >
            ⇄
          </button>

          <label className="form-field">
            <span>Destination station</span>

            <select
              value={destinationStationId}
              onChange={(event) => setDestinationStationId(event.target.value)}
              disabled={loading}
            >
              <option value="">Select destination station</option>

              {destinationOptions.map((station) => (
                <option key={station.id} value={station.id}>
                  {station.name} ({station.code})
                </option>
              ))}
            </select>
          </label>
        </div>

        <button
          type="submit"
          className="primary-button search-button"
          disabled={!formIsValid || loading}
        >
          {loading ? "Searching..." : "Search available seats"}
        </button>
      </form>
    </section>
  );
}
