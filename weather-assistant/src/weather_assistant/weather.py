"""Async WeatherAPI adapter, bounded cache and independently testable guidance."""

import math
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx


class WeatherError(Exception):
    """A safe, user-facing error. Never include provider URLs or credentials."""


def _number(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("Boolean is not a weather measurement")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite measurement")
    return number


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError("Invalid weather label")
    return " ".join(value.split())


@dataclass(frozen=True)
class Weather:
    city: str
    country: str
    local_time: str
    condition: str
    temperature_c: float
    feels_like_c: float
    wind_m_s: float
    humidity: float
    pressure_hpa: float
    rain_chance: float

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Weather":
        try:
            location, current = payload["location"], payload["current"]
            day = payload["forecast"]["forecastday"][0]["day"]
            rain, humidity = _number(day["daily_chance_of_rain"]), _number(current["humidity"])
            wind, pressure = _number(current["wind_kph"]), _number(current["pressure_mb"])
            if not (0 <= rain <= 100 and 0 <= humidity <= 100 and wind >= 0 and pressure > 0):
                raise ValueError("Out-of-range measurement")
            return cls(
                city=_text(location["name"]),
                country=_text(location["country"]),
                local_time=_text(location["localtime"]),
                condition=_text(current["condition"]["text"]),
                temperature_c=_number(current["temp_c"]),
                feels_like_c=_number(current["feelslike_c"]),
                wind_m_s=wind / 3.6,
                humidity=humidity,
                pressure_hpa=pressure,  # 1 millibar = 1 hectopascal, not 1 mmHg.
                rain_chance=rain,
            )
        except (KeyError, IndexError, TypeError, ValueError, OverflowError):
            raise WeatherError("The weather service returned incomplete or invalid data.") from None


def clothing_advice(feels_like_c: float) -> str:
    if feels_like_c < 10:
        return "Consider a warm jacket and extra layers."
    if feels_like_c < 20:
        return "Consider a light jacket or sweater."
    return "Light clothing may be comfortable."


def rain_advice(chance: float) -> str:
    if chance >= 70:
        return "Rain is likely today; bring an umbrella or waterproof layer."
    if chance >= 40:
        return "Rain is possible today; consider carrying an umbrella."
    return "The daily chance of rain is low, but rain is still possible."


def format_weather(weather: Weather) -> str:
    return (
        f"{weather.city}, {weather.country}\n"
        f"Local time: {weather.local_time}\n"
        f"{weather.condition}\n"
        f"Temperature: {weather.temperature_c:g} C (feels like {weather.feels_like_c:g} C)\n"
        f"Wind: {weather.wind_m_s:.1f} m/s | Humidity: {weather.humidity:g}%\n"
        f"Pressure: {weather.pressure_hpa:g} hPa\n"
        f"Today's chance of rain: {weather.rain_chance:g}%\n\n"
        f"{clothing_advice(weather.feels_like_c)}\n"
        f"{rain_advice(weather.rain_chance)}\n\n"
        "General guidance from a city-level forecast, not route-specific or safety advice."
    )


class WeatherClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        api_key: str,
        *,
        cache_ttl: float = 300,
        max_entries: int = 256,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if cache_ttl < 0 or max_entries < 1:
            raise ValueError("Cache TTL must be non-negative and capacity positive.")
        self._http, self._api_key = http, api_key
        self._ttl, self._max_entries, self._clock = cache_ttl, max_entries, clock
        self._cache: OrderedDict[str, tuple[float, Weather]] = OrderedDict()

    async def get(self, city: str) -> Weather:
        city = " ".join(city.split())
        if not city or len(city) > 100 or any(ord(c) < 32 for c in city):
            raise WeatherError("Enter a city name between 1 and 100 characters.")
        key = city.casefold()
        cached = self._cache.get(key)
        if cached and self._clock() < cached[0]:
            self._cache.move_to_end(key)
            return cached[1]
        try:
            response = await self._http.get(
                "https://api.weatherapi.com/v1/forecast.json",
                params={"key": self._api_key, "q": city, "days": 1, "aqi": "no", "alerts": "no"},
                timeout=10.0,
            )
        except httpx.RequestError:
            raise WeatherError(
                "The weather service is unavailable. Please try again later."
            ) from None
        if response.is_error:
            try:
                code = response.json().get("error", {}).get("code")
            except (ValueError, AttributeError):
                code = None
            if code == 1006:
                raise WeatherError("City not found. Try adding a country, e.g. Waterford, Ireland.")
            raise WeatherError(
                "The weather service could not process this request. Try again later."
            )
        try:
            weather = Weather.from_payload(response.json())
        except ValueError:
            raise WeatherError("The weather service returned an invalid response.") from None
        self._cache[key] = (self._clock() + self._ttl, weather)
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)
        return weather
