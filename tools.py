import requests
from datetime import date
from agents import function_tool
from models import GetCityAirportParams, GetFlightsParams
from config import (
    CITY_TO_AIRPORT,
    MULTIPLE_AIRPORTS,
    AVIATIONSTACK_KEY,
    API_TIMEOUT,
    MAX_FLIGHT_RESULTS,
)
from formatters import (
    format_flight_info,
    format_upcoming_flights_info,
    format_no_flights_message,
)


@function_tool
def get_city_airport_code(params: GetCityAirportParams) -> str:
    """
    Converts a city name to its airport code(s). If multiple airports exist,
    returns all options for the user to choose from.

    Args:
        params: A GetCityAirportParams object containing the city name.

    Returns:
        A string with the airport code or multiple options if the city has multiple airports.
    """
    city = params.city_name.lower().strip()

    # Check if city has multiple airports
    if city in MULTIPLE_AIRPORTS:
        airports = MULTIPLE_AIRPORTS[city]
        options = "\n".join(
            [f"• {airport['code']} - {airport['name']}" for airport in airports]
        )
        return f"I found multiple airports in {params.city_name.title()}:\n{options}\n\nWhich airport would you like to use?"

    # Check if city has a single airport
    if city in CITY_TO_AIRPORT:
        return f"The airport code for {params.city_name.title()} is {CITY_TO_AIRPORT[city]}"

    # City not found
    return f"Sorry, I couldn't find an airport code for '{params.city_name.title()}'. You can try checking the spelling, using a different major city, or providing the 3-letter IATA airport code directly."


@function_tool
def get_flights(params: GetFlightsParams) -> str:
    """
    Searches for flights based on departure and arrival airports. It prioritizes
    today's flights and can also show upcoming flights if none are available today.

    Args:
        params: A GetFlightsParams object with departure and arrival airport codes.

    Returns:
        A formatted string of available flights or a message if none are found.
    """
    api_url = "http://api.aviationstack.com/v1/flights"
    api_params = {
        "access_key": AVIATIONSTACK_KEY,
        "dep_iata": params.departure,
        "arr_iata": params.arrival,
        "limit": MAX_FLIGHT_RESULTS,
    }

    try:
        print(f"DEBUG: Searching flights from {params.departure} to {params.arrival}")
        response = requests.get(api_url, params=api_params, timeout=API_TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        # Check for API-level errors returned in a 200 OK response
        if "error" in data:
            error_info = data["error"]
            code = error_info.get("code")
            info = error_info.get("info", "No additional information provided.")
            print(f"DEBUG: API returned error in JSON: {error_info}")
            return (
                f"An error occurred while fetching flight data: {info} (Code: {code})"
            )

        all_flights = data.get("data", [])

        if not all_flights:
            print("DEBUG: No flights found in the API response.")
            return format_no_flights_message(params.departure, params.arrival)

        today = date.today()
        today_str = today.isoformat()

        # Separate today's flights from upcoming ones
        todays_flights = [f for f in all_flights if f.get("flight_date") == today_str]

        if todays_flights:
            print(f"DEBUG: Found {len(todays_flights)} flights for today.")
            return format_flight_info(todays_flights, today)
        else:
            # If no flights for today, treat all results as "upcoming"
            print(
                f"DEBUG: No flights for today. Found {len(all_flights)} upcoming flights to display."
            )
            return format_upcoming_flights_info(
                all_flights, params.departure, params.arrival
            )

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print(f"DEBUG: HTTP Error {status_code} from API. Response: {e.response.text}")
        if status_code == 422:
            return f"Error: Invalid airport code provided. Please double-check the departure '{params.departure}' and arrival '{params.arrival}' codes and try again."
        elif status_code == 401:
            return "API Key Error: Authentication failed. Please check the AVIATIONSTACK_KEY."
        else:
            return f"Error Fetching Flight Data: The server returned status {status_code}. Please try again later."
    except requests.exceptions.Timeout:
        print("DEBUG: Request to AviationStack API timed out.")
        return "Request Timed Out: The flight search is taking too long. Please try again in a moment."
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Network request exception: {e}")
        return "Network Error: Could not connect to the flight data service. Please check your internet connection."
    except Exception as e:
        print(f"UNEXPECTED ERROR in get_flights: {e}")
        return f"An unexpected error occurred: {e}. Please try again."
