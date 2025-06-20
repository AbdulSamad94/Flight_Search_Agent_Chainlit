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
    return f"I couldn't find an airport code for '{params.city_name}'. Please provide the 3-letter airport code directly, or try a different city name."


@function_tool
def get_flights(params: GetFlightsParams) -> str:
    """
    Searches for flights based on the provided departure and arrival airports.
    First searches for today's flights, if none found, searches for upcoming flights.

    Args:
        params: A GetFlightsParams object containing departure and arrival airport codes.

    Returns:
        A formatted string describing the available flights, or an error message.
    """
    try:
        # First, try to get today's flights (without date filter to get current flights)
        today = date.today()
        url_today = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_KEY}&dep_iata={params.departure}&arr_iata={params.arrival}"

        print(
            f"DEBUG: Searching for flights from {params.departure} to {params.arrival}"
        )

        response_today = requests.get(url_today, timeout=API_TIMEOUT)

        print(f"DEBUG: API Response Status: {response_today.status_code}")

        if response_today.status_code == 200:
            data_today = response_today.json()
            flights_today = data_today.get("data", [])

            print(f"DEBUG: Found {len(flights_today)} flights")

            if flights_today:
                # Found flights for today
                formatted_result = format_flight_info(flights_today, today)
                return formatted_result
            else:
                # No flights found - try with simpler search
                print("DEBUG: No flights found, trying alternative search")

                # Try without date filter and just get any available flights
                url_general = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_KEY}&dep_iata={params.departure}&arr_iata={params.arrival}&limit={MAX_FLIGHT_RESULTS}"

                response_general = requests.get(url_general, timeout=API_TIMEOUT)

                if response_general.status_code == 200:
                    data_general = response_general.json()
                    flights_general = data_general.get("data", [])

                    if flights_general:
                        # Found some flights, format as upcoming
                        for flight in flights_general:
                            flight["search_date"] = (
                                today  # Default to today for formatting
                            )

                        formatted_result = format_upcoming_flights_info(
                            flights_general, params.departure, params.arrival
                        )
                        return formatted_result
                    else:
                        return format_no_flights_message(
                            params.departure, params.arrival
                        )
                else:
                    return f"Error Fetching Flight Data\n\nAPI returned status code: {response_general.status_code}"
        else:
            return f"Error Fetching Flight Data\n\nAPI returned status code: {response_today.status_code}. Please verify the airport codes and try again."

    except requests.exceptions.Timeout:
        return "Request Timed Out\n\nThe flight search is taking too long. Please try again in a moment."
    except requests.exceptions.RequestException as e:
        return f"Network Error\n\nConnection issue: {str(e)}\n\nPlease check your internet connection and try again."
    except Exception as e:
        return f"Unexpected Error\n\nSomething went wrong: {str(e)}\n\nPlease try again or contact support if the issue persists."
