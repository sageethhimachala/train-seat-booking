export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="loading-container" role="status">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}
