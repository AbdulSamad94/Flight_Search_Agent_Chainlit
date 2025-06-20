import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")
if not AVIATIONSTACK_KEY:
    raise ValueError("AVIATIONSTACK_KEY is not set. Please set it in the .env file.")

# Comprehensive city to airport code mapping
CITY_TO_AIRPORT = {
    # Pakistan
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    "peshawar": "PEW",
    "quetta": "UET",
    "multan": "MUX",
    "faisalabad": "LYP",
    "sialkot": "SKT",
    # UAE
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",
    # Saudi Arabia
    "riyadh": "RUH",
    "jeddah": "JED",
    "dammam": "DMM",
    "medina": "MED",
    # Major International Cities
    "london": "LHR",
    "new york": "JFK",
    "paris": "CDG",
    "tokyo": "NRT",
    "singapore": "SIN",
    "bangkok": "BKK",
    "kuala lumpur": "KUL",
    "istanbul": "IST",
    "doha": "DOH",
    "muscat": "MCT",
    "kuwait": "KWI",
    "bahrain": "BAH",
    "manchester": "MAN",
    "birmingham": "BHX",
    "toronto": "YYZ",
    "chicago": "ORD",
    "los angeles": "LAX",
    "delhi": "DEL",
    "mumbai": "BOM",
    "chennai": "MAA",
    "bangalore": "BLR",
    "hyderabad": "HYD",
    "kolkata": "CCU",
}

# Cities with multiple airports
MULTIPLE_AIRPORTS = {
    "london": [
        {"code": "LHR", "name": "Heathrow Airport"},
        {"code": "LGW", "name": "Gatwick Airport"},
        {"code": "STN", "name": "Stansted Airport"},
        {"code": "LTN", "name": "Luton Airport"},
    ],
    "new york": [
        {"code": "JFK", "name": "John F. Kennedy International Airport"},
        {"code": "LGA", "name": "LaGuardia Airport"},
        {"code": "EWR", "name": "Newark Liberty International Airport"},
    ],
    "tokyo": [
        {"code": "NRT", "name": "Narita International Airport"},
        {"code": "HND", "name": "Haneda Airport"},
    ],
    "paris": [
        {"code": "CDG", "name": "Charles de Gaulle Airport"},
        {"code": "ORY", "name": "Orly Airport"},
    ],
    "dubai": [
        {"code": "DXB", "name": "Dubai International Airport"},
        {"code": "DWC", "name": "Dubai World Central"},
    ],
}

# API Configuration
API_TIMEOUT = 15
MAX_FLIGHT_RESULTS = 10
