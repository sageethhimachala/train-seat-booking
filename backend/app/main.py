from fastapi import FastAPI

from app.database.database import engine
from app.models.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Train Seat Booking API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Train Seat Booking API is running"
    }