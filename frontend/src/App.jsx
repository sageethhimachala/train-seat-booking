import { useState } from "react";

import Header from "./components/Header";
import BookingPage from "./pages/BookingPage";
import ManageBookingPage from "./pages/ManageBookingPage";

export default function App() {
  const [activePage, setActivePage] =
    useState("booking");

  const [
    selectedBookingReference,
    setSelectedBookingReference,
  ] = useState("");

  function handleNavigate(page) {
    setActivePage(page);

    if (page !== "manage") {
      setSelectedBookingReference("");
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function handleManageBooking(
    bookingReference,
  ) {
    setSelectedBookingReference(
      bookingReference,
    );

    setActivePage("manage");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  return (
    <div className="app">
      <Header
        activePage={activePage}
        onNavigate={handleNavigate}
      />

      {activePage === "booking" && (
        <BookingPage
          onManageBooking={handleManageBooking}
        />
      )}

      {activePage === "manage" && (
        <ManageBookingPage
          initialBookingReference={
            selectedBookingReference
          }
        />
      )}
    </div>
  );
}
