import textwrap
from datetime import date, datetime
from typing import Dict, List
from utils import (
    format_flight_time,
    format_date,
    generate_booking_url,
    get_status_indicator,
)


def create_booking_link(airline: str, booking_url: str, flight_number: str) -> str:
    """Create a markdown link for booking a flight."""

    return f"""
        <div style="margin: 10px 0;">
        <a href="{booking_url}" target="_blank" style="
        display: inline-block;
        background-color: #007bff;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
        " onmouseover="this.style.backgroundColor='#0056b3'" onmouseout="this.style.backgroundColor='#007bff'">
        Book {flight_number} with {airline}
        </a>
        </div>"""


def _format_single_flight_card(
    flight: Dict, dep_code: str, arr_code: str, index: int
) -> str:
    """Formats the details for a single flight into a markdown card."""
    try:
        flight_number = flight["flight"]["iata"]
        airline = flight["airline"]["name"]
        dep_time = format_flight_time(flight["departure"]["scheduled"])
        dep_terminal = flight["departure"].get("terminal", "N/A")
        dep_delay = flight["departure"].get("delay", 0)
        arr_time = format_flight_time(flight["arrival"]["scheduled"])
        arr_terminal = flight["arrival"].get("terminal", "N/A")
        status = flight["flight_status"].title()
        status_indicator = get_status_indicator(status)
        booking_url = generate_booking_url(flight, dep_code, arr_code)
        booking_link = create_booking_link(airline, booking_url, flight_number)

        card_lines = [
            f"### {index}. Flight {flight_number} - {airline}",
            "",
            "**DEPARTURE**",
            f"- Terminal: {dep_terminal}",
            f"- Time: {dep_time}",
        ]

        if dep_delay and dep_delay > 0:
            card_lines.append(f"- Delay: {dep_delay} minutes")

        card_lines.extend(
            [
                "",
                "**ARRIVAL**",
                f"- Terminal: {arr_terminal}",
                f"- Time: {arr_time}",
                "",
                f"**STATUS:** {status_indicator} {status}",
                "",
                f"**BOOKING:** {booking_link}",
            ]
        )

        if flight["flight"].get("codeshared"):
            codeshare = flight["flight"]["codeshared"]
            card_lines.append(
                f"**CODESHARE:** {codeshare['airline_name']} {codeshare['flight_iata']}"
            )

        return "\n".join(card_lines)

    except (KeyError, TypeError) as e:
        print(
            f"Error formatting flight data for flight {flight.get('flight', {}).get('iata', 'N/A')}: {e}"
        )
        return f"### {index}. Flight Details Unavailable"


def _format_single_upcoming_flight_card(
    flight: Dict, dep_code: str, arr_code: str, index: int
) -> str:
    """Formats the details for a single upcoming flight into a markdown card."""
    try:
        flight_number = flight["flight"]["iata"]
        airline = flight["airline"]["name"]
        dep_time = format_flight_time(flight["departure"]["scheduled"])
        arr_time = format_flight_time(flight["arrival"]["scheduled"])
        dep_terminal = flight["departure"].get("terminal", "N/A")
        arr_terminal = flight["arrival"].get("terminal", "N/A")
        status = flight["flight_status"].title()
        status_indicator = get_status_indicator(status)
        booking_url = generate_booking_url(flight, dep_code, arr_code)
        booking_link = create_booking_link(airline, booking_url, flight_number)

        card_lines = [
            f"**{index}. Flight {flight_number}** - {airline}",
            f"- **Departure:** {dep_time} (Terminal {dep_terminal})",
            f"- **Arrival:** {arr_time} (Terminal {arr_terminal})",
            f"- **Status:** {status_indicator} {status}",
            f"- **Booking:** {booking_link}",
        ]

        if flight["flight"].get("codeshared"):
            codeshare = flight["flight"]["codeshared"]
            card_lines.append(
                f"- **Codeshare:** {codeshare['airline_name']} {codeshare['flight_iata']}"
            )

        return "\n".join(card_lines)

    except (KeyError, TypeError) as e:
        print(
            f"Error formatting upcoming flight data for flight {flight.get('flight', {}).get('iata', 'N/A')}: {e}"
        )
        return f"**{index}. Flight Details Unavailable**"


def format_flight_info(flights_data: List[Dict], flight_date: date) -> str:
    """Format today's flight information in a structured way."""
    if not flights_data:
        return "No flights found for today."

    first_flight = flights_data[0]
    dep_city = first_flight["departure"]["airport"]
    dep_code = first_flight["departure"]["iata"]
    arr_city = first_flight["arrival"]["airport"]
    arr_code = first_flight["arrival"]["iata"]
    formatted_date = format_date(flight_date)

    header = [
        "# FLIGHT SEARCH RESULTS",
        f"## TODAY'S FLIGHTS - {formatted_date}",
        f"### {dep_city} ({dep_code}) to {arr_city} ({arr_code})",
        "---",
    ]

    flight_cards = [
        _format_single_flight_card(flight, dep_code, arr_code, i)
        for i, flight in enumerate(flights_data, 1)
    ]

    full_response = "\n".join(header) + "\n" + "\n---\n".join(flight_cards)
    return full_response


def format_upcoming_flights_info(
    flights_data: List[Dict], dep_code: str, arr_code: str
) -> str:
    """Format upcoming flights information when no flights are available today"""
    if not flights_data:
        return format_no_flights_message(dep_code, arr_code)

    first_flight = flights_data[0]
    dep_city = first_flight["departure"]["airport"]
    arr_city = first_flight["arrival"]["airport"]
    today_formatted = format_date(date.today())

    response_parts = [
        "# FLIGHT SEARCH RESULTS",
        f"## NO FLIGHTS TODAY - {today_formatted}",
        f"### {dep_city} ({dep_code}) to {arr_city} ({arr_code})",
        "",
        "*No flights available for today. Here are the next available flights:*",
        "---",
        "## UPCOMING FLIGHTS",
    ]

    flights_by_date = {}
    for flight in flights_data:
        date_key = flight.get("flight_date")
        if not date_key:
            flight_date_obj = flight.get("search_date", date.today())
            date_key = flight_date_obj.isoformat()

        if date_key not in flights_by_date:
            flights_by_date[date_key] = []
        flights_by_date[date_key].append(flight)

    # Display flights grouped by date
    for date_str in sorted(flights_by_date.keys()):
        flights_for_date = flights_by_date[date_str]
        try:
            flight_date_obj = datetime.fromisoformat(date_str).date()
            formatted_date = format_date(flight_date_obj)
            response_parts.append(f"\n### {formatted_date}\n")
        except ValueError:
            response_parts.append(f"\n### {date_str}\n")

        for i, flight in enumerate(flights_for_date, 1):
            response_parts.append(
                _format_single_upcoming_flight_card(flight, dep_code, arr_code, i)
            )
            response_parts.append("")  # Add a newline for spacing

    response_parts.extend(
        ["---", "\n**Tip:** Click on any 'Book' button to proceed with your booking!"]
    )

    return "\n".join(response_parts)


def format_no_flights_message(dep_code: str, arr_code: str) -> str:
    """Format message when no flights are found at all"""
    today_formatted = format_date(date.today())

    message = f"""
    # FLIGHT SEARCH RESULTS

    ## NO FLIGHTS FOUND
    ### {dep_code} to {arr_code}

    **Search Period:** {today_formatted} - Next 7 days

    ---

    ### What you can try:

    1.  **Double-check airport codes** - Make sure the airports are correct
    2.  **Try different dates** - This route might not operate daily
    3.  **Check nearby airports** - Some cities have multiple airports
    4.  **Contact airline directly** - For the most up-to-date schedules

    ---

    **Need help?** Just ask me to search for flights from different cities or airports!
    """
    return textwrap.dedent(message).strip()
