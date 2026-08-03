export function formatDateTime(dateTime) {
  if (!dateTime) {
    return "Not available";
  }

  const date = new Date(dateTime);

  if (Number.isNaN(date.getTime())) {
    return "Invalid date";
  }

  return new Intl.DateTimeFormat("en-LK", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatCurrency(value) {
  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return "LKR 0.00";
  }

  return new Intl.NumberFormat("en-LK", {
    style: "currency",
    currency: "LKR",
    minimumFractionDigits: 2,
  }).format(numericValue);
}

export function formatDirection(direction) {
  if (direction === "FORWARD") {
    return "Colombo Fort to Badulla";
  }

  if (direction === "REVERSE") {
    return "Badulla to Colombo Fort";
  }

  return direction;
}
