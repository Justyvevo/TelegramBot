import unittest

import httpx

from weather_assistant.demo import sample_payload
from weather_assistant.weather import (
    Weather,
    WeatherClient,
    WeatherError,
    clothing_advice,
    format_weather,
    rain_advice,
)


class WeatherParsingTests(unittest.TestCase):
    def test_units_and_values(self):
        weather = Weather.from_payload(sample_payload())
        self.assertEqual(weather.wind_m_s, 5)
        self.assertEqual(weather.pressure_hpa, 1012)
        self.assertEqual(weather.rain_chance, 70)
        self.assertEqual(weather.city, "Waterford")

    def test_numeric_strings_are_supported(self):
        payload = sample_payload()
        payload["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"] = "70"
        self.assertEqual(Weather.from_payload(payload).rain_chance, 70)

    def test_missing_data_is_rejected(self):
        for payload in ({}, {"location": []}, None, [], {"location": None}):
            with self.subTest(payload=payload), self.assertRaises(WeatherError):
                Weather.from_payload(payload)

    def test_empty_forecast_is_rejected(self):
        payload = sample_payload()
        payload["forecast"]["forecastday"] = []
        with self.assertRaises(WeatherError):
            Weather.from_payload(payload)

    def test_non_finite_temperature_is_rejected(self):
        for value in (float("nan"), float("inf"), "-inf", True, None):
            payload = sample_payload()
            payload["current"]["temp_c"] = value
            with self.subTest(value=value), self.assertRaises(WeatherError):
                Weather.from_payload(payload)

    def test_invalid_probability_is_rejected(self):
        for value in (-1, 101, "invalid"):
            payload = sample_payload()
            payload["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"] = value
            with self.subTest(value=value), self.assertRaises(WeatherError):
                Weather.from_payload(payload)

    def test_invalid_labels_are_rejected(self):
        for value in (None, "", "x" * 201):
            payload = sample_payload()
            payload["location"]["name"] = value
            with self.subTest(value=value), self.assertRaises(WeatherError):
                Weather.from_payload(payload)

    def test_clothing_thresholds(self):
        expected = [
            (9.9, "warm jacket"),
            (10, "light jacket"),
            (19.9, "light jacket"),
            (20, "Light clothing"),
        ]
        for value, phrase in expected:
            with self.subTest(value=value):
                self.assertIn(phrase, clothing_advice(value))

    def test_rain_thresholds_including_exact_boundaries(self):
        expected = [
            (0, "low"),
            (39, "low"),
            (40, "possible today"),
            (69, "possible today"),
            (70, "likely today"),
            (100, "likely today"),
        ]
        for value, phrase in expected:
            with self.subTest(value=value):
                self.assertIn(phrase, rain_advice(value))

    def test_formatted_output_and_qualifications(self):
        result = format_weather(Weather.from_payload(sample_payload()))
        for phrase in ("1012 hPa", "5.0 m/s", "chance of rain: 70%", "not route-specific"):
            self.assertIn(phrase, result)
        self.assertNotIn("mmHg", result)
        self.assertNotIn("[70]", result)


class WeatherClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.calls = []
        self.now = 0.0
        self.response = httpx.Response(200, json=sample_payload())

        def handler(request):
            self.calls.append(request)
            if isinstance(self.response, Exception):
                raise self.response
            return self.response

        self.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        self.client = WeatherClient(self.http, "fixture-secret", clock=lambda: self.now)

    async def asyncTearDown(self):
        await self.http.aclose()

    async def test_request_uses_https_query_parameters_and_timeout(self):
        await self.client.get("Waterford, Ireland")
        request = self.calls[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.params["q"], "Waterford, Ireland")
        self.assertEqual(request.url.params["days"], "1")
        self.assertEqual(request.extensions["timeout"]["read"], 10)

    async def test_city_cannot_inject_query_parameters(self):
        await self.client.get("Waterford&key=another-key")
        params = self.calls[0].url.params
        self.assertEqual(params["key"], "fixture-secret")
        self.assertEqual(params["q"], "Waterford&key=another-key")

    async def test_cache_normalizes_city(self):
        first = await self.client.get(" Waterford   Ireland ")
        second = await self.client.get("waterford ireland")
        self.assertIs(first, second)
        self.assertEqual(len(self.calls), 1)

    async def test_cache_expires_at_boundary(self):
        await self.client.get("Waterford")
        self.now = 299
        await self.client.get("Waterford")
        self.assertEqual(len(self.calls), 1)
        self.now = 300
        await self.client.get("Waterford")
        self.assertEqual(len(self.calls), 2)

    async def test_cache_evicts_least_recently_used(self):
        self.client = WeatherClient(self.http, "fixture-secret", max_entries=2)
        for city in ("A", "B", "A", "C", "B"):
            await self.client.get(city)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(len(self.client._cache), 2)

    async def test_failures_are_not_cached(self):
        self.response = httpx.Response(500)
        with self.assertRaises(WeatherError):
            await self.client.get("Waterford")
        self.response = httpx.Response(200, json=sample_payload())
        await self.client.get("Waterford")
        self.assertEqual(len(self.calls), 2)

    async def test_unknown_city_is_friendly(self):
        self.response = httpx.Response(400, json={"error": {"code": 1006}})
        with self.assertRaisesRegex(WeatherError, "City not found"):
            await self.client.get("Unknown")

    async def test_error_does_not_expose_secret_or_raw_response(self):
        self.response = httpx.Response(401, text="credential fixture-secret was rejected")
        with self.assertRaises(WeatherError) as caught:
            await self.client.get("Waterford")
        self.assertNotIn("fixture-secret", str(caught.exception))
        self.assertNotIn("http", str(caught.exception))

    async def test_network_timeout_is_friendly(self):
        self.response = httpx.ReadTimeout("URL contains fixture-secret")
        with self.assertRaisesRegex(WeatherError, "unavailable") as caught:
            await self.client.get("Waterford")
        self.assertNotIn("fixture-secret", str(caught.exception))

    async def test_invalid_json_is_friendly(self):
        self.response = httpx.Response(200, text="not JSON")
        with self.assertRaisesRegex(WeatherError, "invalid response"):
            await self.client.get("Waterford")

    async def test_invalid_cities_do_not_make_requests(self):
        for city in ("", "  ", "x" * 101, "City\x00"):
            with self.subTest(city=city), self.assertRaises(WeatherError):
                await self.client.get(city)
        self.assertEqual(self.calls, [])
