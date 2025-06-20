from datetime import datetime, date
from typing import Dict


def format_flight_time(time_str: str) -> str:
    """Format flight time to a more readable format"""
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.strftime("%I:%M %p")
    except:
        return time_str


def format_date(date_obj) -> str:
    """Format date to a readable format"""
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj).date()
        return date_obj.strftime("%A, %B %d, %Y")
    except:
        return str(date_obj)


def generate_booking_url(flight: Dict, dep_code: str, arr_code: str) -> str:
    """Generate booking URL based on airline or use travel aggregator"""
    try:
        airline_code = flight["airline"]["iata"].upper()
        flight_number = flight["flight"]["iata"]

        # Airline-specific booking URLs
        airline_urls = {
            "EK": f"https://www.emirates.com/english/book/flight-search/?adults=1&children=0&infants=0&from={dep_code}&to={arr_code}",
            "PK": f"https://www.piac.com.pk/book-flight/?from={dep_code}&to={arr_code}&adults=1",
            "QR": f"https://www.qatarairways.com/en/book-flights.html?origin={dep_code}&destination={arr_code}&pax=1:0:0",
            "EY": f"https://www.etihad.com/en/book/flights?origin={dep_code}&destination={arr_code}&passengers=1",
            "FZ": f"https://www.flydubai.com/en/book/search?from={dep_code}&to={arr_code}&adult=1",
            "SV": f"https://www.saudia.com/en/book/flights/multi-city?from={dep_code}&to={arr_code}&adults=1",
            "MS": f"https://www.egyptair.com/en/fly/book-a-flight/flight-search?from={dep_code}&to={arr_code}&adult=1",
            "TK": f"https://www.turkishairlines.com/en-int/booking/flight/availability?origin={dep_code}&destination={arr_code}&adult=1",
        }

        # If we have airline-specific URL, use it
        if airline_code in airline_urls:
            return airline_urls[airline_code]

        # Otherwise, use travel aggregator with pre-filled details
        return f"https://www.skyscanner.com/flights/{dep_code.lower()}/{arr_code.lower()}?adults=1&children=0&adultsv2=1&childrenv2=&infants=0&cabinclass=economy&rtn=0&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false"

    except:
        # Fallback to generic search
        return f"https://www.google.com/flights?q=flights+from+{dep_code}+to+{arr_code}"


def get_status_indicator(status: str) -> str:
    """Get status indicator without emojis"""
    status_lower = status.lower()
    if status_lower in ["scheduled", "active"]:
        return "[ON TIME]"
    elif status_lower == "delayed":
        return "[DELAYED]"
    else:
        return "[CANCELLED]"
