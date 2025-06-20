from datetime import date, datetime
from typing import Dict, List
from utils import (
    format_flight_time,
    format_date,
    generate_booking_url,
    get_status_indicator,
)


def create_booking_button(airline: str, booking_url: str, flight_number: str) -> str:
    """Create a booking button with proper formatting"""
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


def format_flight_info(flights_data: List[Dict], flight_date) -> str:
    """Format today's flight information in a structured way"""
    if not flights_data:
        return "No flights found for today."

    # Get departure and arrival cities
    first_flight = flights_data[0]
    dep_city = first_flight["departure"]["airport"]
    dep_code = first_flight["departure"]["iata"]
    arr_city = first_flight["arrival"]["airport"]
    arr_code = first_flight["arrival"]["iata"]

    formatted_date = format_date(flight_date)

    # Header
    result = f"""
# FLIGHT SEARCH RESULTS

## TODAY'S FLIGHTS - {formatted_date}
### {dep_city} ({dep_code}) to {arr_city} ({arr_code})

---
"""

    for i, flight in enumerate(flights_data, 1):
        try:
            # Extract flight information
            flight_number = flight["flight"]["iata"]
            airline = flight["airline"]["name"]
            airline_code = flight["airline"]["iata"]

            # Departure info
            dep_time = format_flight_time(flight["departure"]["scheduled"])
            dep_terminal = flight["departure"].get("terminal", "N/A")
            dep_delay = flight["departure"].get("delay", 0)

            # Arrival info
            arr_time = format_flight_time(flight["arrival"]["scheduled"])
            arr_terminal = flight["arrival"].get("terminal", "N/A")

            # Flight status
            status = flight["flight_status"].title()
            status_indicator = get_status_indicator(status)

            # Generate booking URL and button
            booking_url = generate_booking_url(flight, dep_code, arr_code)
            booking_button = create_booking_button(airline, booking_url, flight_number)

            # Build flight card
            result += f"""
### {i}. Flight {flight_number} - {airline}

**DEPARTURE**
- Terminal: {dep_terminal}
- Time: {dep_time}"""

            if dep_delay and dep_delay > 0:
                result += f"\n- Delay: {dep_delay} minutes"

            result += f"""

**ARRIVAL**
- Terminal: {arr_terminal}  
- Time: {arr_time}

**STATUS:** {status_indicator} {status}

**BOOKING:**
{booking_button}
"""

            # Add codeshare info if available
            if flight["flight"].get("codeshared"):
                codeshare = flight["flight"]["codeshared"]
                result += f"**CODESHARE:** {codeshare['airline_name']} {codeshare['flight_iata']}\n"

            result += "\n---\n"

        except Exception as e:
            result += f"\n### {i}. Flight Details Unavailable\n---\n"

    return result


def format_upcoming_flights_info(
    flights_data: List[Dict], dep_code: str, arr_code: str
) -> str:
    """Format upcoming flights information when no flights are available today"""
    if not flights_data:
        return format_no_flights_message(dep_code, arr_code)

    # Get departure and arrival cities from first flight
    first_flight = flights_data[0]
    dep_city = first_flight["departure"]["airport"]
    arr_city = first_flight["arrival"]["airport"]

    today_formatted = format_date(date.today())

    # Group flights by date
    flights_by_date = {}
    for flight in flights_data:
        flight_date = flight.get("search_date", date.today())
        date_key = flight_date.isoformat()
        if date_key not in flights_by_date:
            flights_by_date[date_key] = []
        flights_by_date[date_key].append(flight)

    # Header
    result = f"""
# FLIGHT SEARCH RESULTS

## NO FLIGHTS TODAY - {today_formatted}
### {dep_city} ({dep_code}) to {arr_city} ({arr_code})

*No flights available for today. Here are the next available flights:*

---

## UPCOMING FLIGHTS
"""

    # Display flights grouped by date
    for date_str in sorted(flights_by_date.keys()):
        flights_for_date = flights_by_date[date_str]
        flight_date = datetime.fromisoformat(date_str).date()
        formatted_date = format_date(flight_date)

        result += f"\n### {formatted_date}\n"

        for i, flight in enumerate(flights_for_date, 1):
            try:
                # Extract flight information
                flight_number = flight["flight"]["iata"]
                airline = flight["airline"]["name"]

                # Departure and arrival times
                dep_time = format_flight_time(flight["departure"]["scheduled"])
                arr_time = format_flight_time(flight["arrival"]["scheduled"])

                dep_terminal = flight["departure"].get("terminal", "N/A")
                arr_terminal = flight["arrival"].get("terminal", "N/A")

                # Flight status
                status = flight["flight_status"].title()
                status_indicator = get_status_indicator(status)

                # Generate booking URL and button
                booking_url = generate_booking_url(flight, dep_code, arr_code)
                booking_button = create_booking_button(
                    airline, booking_url, flight_number
                )

                result += f"""
**{i}. Flight {flight_number}** - {airline}
- **Departure:** {dep_time} (Terminal {dep_terminal})
- **Arrival:** {arr_time} (Terminal {arr_terminal})
- **Status:** {status_indicator} {status}
- **Booking:** 
{booking_button}
"""

                # Add codeshare info if available
                if flight["flight"].get("codeshared"):
                    codeshare = flight["flight"]["codeshared"]
                    result += f"- **Codeshare:** {codeshare['airline_name']} {codeshare['flight_iata']}\n"

            except Exception as e:
                result += f"**{i}. Flight Details Unavailable**\n"

        result += "\n"

    result += "---\n\n**Tip:** Click on any 'Book' button to proceed with your booking!"

    return result


def format_no_flights_message(dep_code: str, arr_code: str) -> str:
    """Format message when no flights are found at all"""
    today_formatted = format_date(date.today())

    return f"""
# FLIGHT SEARCH RESULTS

## NO FLIGHTS FOUND
### {dep_code} to {arr_code}

**Search Period:** {today_formatted} - Next 7 days

---

### What you can try:

1. **Double-check airport codes** - Make sure the airports are correct
2. **Try different dates** - This route might not operate daily
3. **Check nearby airports** - Some cities have multiple airports
4. **Contact airline directly** - For the most up-to-date schedules

---

**Need help?** Just ask me to search for flights from different cities or airports!
"""
