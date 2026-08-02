from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StationResponse(BaseModel):
    id: int
    name: str
    code: str
    order_index: int
    distance_from_start_km: Decimal

    model_config = ConfigDict(from_attributes=True)