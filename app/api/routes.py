from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import TourSearchRequest, TourResult, ApiSearchRequest, ApiSearchResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

MOCK_TOURS = [
    {
        "hotel_name": "Rixos Premium Belek",
        "country": "Турция",
        "price_per_night": 8500,
        "meal_type": "AI",
        "hotel_rating": "5",
        "max_adults": 3,
        "max_children": 2,
    },
    {
        "hotel_name": "Voyage Belek Golf & Spa",
        "country": "Турция",
        "price_per_night": 5500,
        "meal_type": "UAI",
        "hotel_rating": "5",
        "max_adults": 4,
        "max_children": 3,
    },
    {
        "hotel_name": "Justiniano Deluxe Resort",
        "country": "Турция",
        "price_per_night": 3800,
        "meal_type": "AI",
        "hotel_rating": "4",
        "max_adults": 2,
        "max_children": 1,
    },
    {
        "hotel_name": "Steigenberger Aqua Magic",
        "country": "Египет",
        "price_per_night": 5000,
        "meal_type": "AI",
        "hotel_rating": "5",
        "max_adults": 3,
        "max_children": 2,
    },
    {
        "hotel_name": "Atlantis The Palm",
        "country": "ОАЭ",
        "price_per_night": 12000,
        "meal_type": "HB",
        "hotel_rating": "5",
        "max_adults": 3,
        "max_children": 2,
    },
]


def search_tours(search: TourSearchRequest) -> list[TourResult]:
    results = []

    for tour in MOCK_TOURS:
        if tour["country"] != search.country:
            continue
        if int(tour["hotel_rating"]) < int(search.hotel_rating):
            continue
        if tour["max_adults"] < search.adults:
            continue
        if tour["max_children"] < search.children:
            continue

        total_people = search.adults + search.children
        total_price = tour["price_per_night"] * search.nights * total_people

        if total_price > search.budget:
            continue

        reasons = []
        saving = search.budget - total_price
        if saving > 0:
            reasons.append(f"экономия {saving:,} ₽ от бюджета".replace(",", " "))
        if int(tour["hotel_rating"]) > int(search.hotel_rating):
            reasons.append("рейтинг выше запрошенного")
        if tour["meal_type"] == search.meal_type:
            reasons.append("подходящий тип питания")
        if not reasons:
            reasons.append("соответствует параметрам поиска")

        short_reason = reasons[0].capitalize()
        if len(reasons) > 1:
            short_reason += ", " + ", ".join(reasons[1:])

        results.append(TourResult(
            hotel_name=tour["hotel_name"],
            country=tour["country"],
            nights=search.nights,
            price=total_price,
            meal_type=tour["meal_type"],
            hotel_rating=tour["hotel_rating"],
            short_reason=short_reason,
        ))

    return results


SORT_OPTIONS = {
    "price_asc": lambda t: t.price,
    "price_desc": lambda t: -t.price,
    "rating_desc": lambda t: (-int(t.hotel_rating), t.price),
}


def sort_tours(tours: list[TourResult], sort_by: str) -> list[TourResult]:
    key_func = SORT_OPTIONS.get(sort_by, SORT_OPTIONS["price_asc"])
    return sorted(tours, key=key_func)


@router.post("/api/search", response_model=ApiSearchResponse)
async def api_search(body: ApiSearchRequest):
    tours = sort_tours(search_tours(body), body.sort_by)
    return ApiSearchResponse(tours=tours)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    country: str = Form(...),
    departure_city: str = Form(...),
    date_from: str = Form(...),
    date_to: str = Form(...),
    nights: int = Form(...),
    budget: int = Form(...),
    adults: int = Form(...),
    children: int = Form(...),
    meal_type: str = Form(...),
    hotel_rating: str = Form(...),
    sort_by: str = Form("price_asc"),
):
    search_data = TourSearchRequest(
        country=country,
        departure_city=departure_city,
        date_from=date_from,
        date_to=date_to,
        nights=nights,
        budget=budget,
        adults=adults,
        children=children,
        meal_type=meal_type,
        hotel_rating=hotel_rating,
    )

    tours = sort_tours(search_tours(search_data), sort_by)

    return templates.TemplateResponse(
        "results.html",
        {"request": request, "data": search_data, "tours": tours, "sort_by": sort_by},
    )
