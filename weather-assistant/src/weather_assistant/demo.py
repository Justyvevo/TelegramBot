"""Synthetic, offline example: not live or observed weather data."""

from weather_assistant.weather import Weather, format_weather


def sample_payload() -> dict:
    return {
        "location": {"name": "Waterford", "country": "Ireland", "localtime": "2026-09-09 08:00"},
        "current": {
            "temp_c": 13,
            "feelslike_c": 11,
            "condition": {"text": "Light rain"},
            "wind_kph": 18,
            "humidity": 82,
            "pressure_mb": 1012,
        },
        "forecast": {"forecastday": [{"day": {"daily_chance_of_rain": 70}}]},
    }


def main() -> None:
    print("OFFLINE DEMO - synthetic data, not a live forecast\n")
    print(format_weather(Weather.from_payload(sample_payload())))


if __name__ == "__main__":
    main()
