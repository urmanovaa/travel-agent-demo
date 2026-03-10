from pydantic import BaseModel


class TourSearchRequest(BaseModel):
    country: str
    departure_city: str
    date_from: str
    date_to: str
    nights: int
    budget: int
    adults: int
    children: int
    meal_type: str
    hotel_rating: str


class TourResult(BaseModel):
    hotel_name: str
    country: str
    nights: int
    price: int
    meal_type: str
    hotel_rating: str
    short_reason: str


class ApiSearchRequest(TourSearchRequest):
    sort_by: str = "price_asc"


class ApiSearchResponse(BaseModel):
    tours: list[TourResult]
