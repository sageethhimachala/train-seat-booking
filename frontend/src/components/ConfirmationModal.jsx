import { useEffect } from "react";

export default function ConfirmationModal({
  open,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Go back",
  loading = false,
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === "Escape" && !loading) {
        onCancel();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);

      document.body.style.overflow = "";
    };
  }, [open, loading, onCancel]);

  if (!open) {
    return null;
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget && !loading) {
      onCancel();
    }
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={handleBackdropClick}
    >
      <section
        className="confirmation-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirmation-modal-title"
        aria-describedby="confirmation-modal-message"
      >
        <div className="confirmation-modal-icon" aria-hidden="true">
          !
        </div>

        <div className="confirmation-modal-content">
          <h2 id="confirmation-modal-title">{title}</h2>

          <p id="confirmation-modal-message">{message}</p>
        </div>

        <div className="confirmation-modal-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelText}
          </button>

          <button
            type="button"
            className="danger-button"
            onClick={onConfirm}
            disabled={loading}
            autoFocus
          >
            {loading ? "Cancelling..." : confirmText}
          </button>
        </div>
      </section>
    </div>
  );
}
