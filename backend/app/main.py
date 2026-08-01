from fastapi import FastAPI


app = FastAPI(
    title="Segment-Based Train Seat Booking API",
    description=(
        "API for booking reserved train seats across "
        "non-overlapping journey segments."
    ),
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": "Train Seat Booking API is running"
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }