from fastapi import FastAPI

app = FastAPI(
    title="Train Seat Booking API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Train Seat Booking API is running"
    }