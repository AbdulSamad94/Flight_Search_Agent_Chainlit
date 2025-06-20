from pydantic import BaseModel, Field


class GetCityAirportParams(BaseModel):
    city_name: str = Field(..., description="City name to convert to airport code")


class GetFlightsParams(BaseModel):
    departure: str = Field(..., description="Departure airport code")
    arrival: str = Field(..., description="Arrival airport code")
