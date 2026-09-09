# Weather Assistant

**Turn a city forecast into a practical answer: what should I wear, and should I bring an umbrella?**

A Python messaging bot that combines WeatherAPI forecasts with rule-based clothing guidance and opt-in weather notifications. It focuses on making everyday weather information easier to act on.

**Python 3.11+ · aiogram 3 · asyncio · HTTPX · WeatherAPI · Linux/systemd**

## What works in this version

- Look up a city and return current conditions, feels-like temperature, wind, humidity and pressure.
- Suggest clothing layers using feels-like temperature.
- Explain today's precipitation probability, including the 40% and 70% boundary cases.
- Remember a selected city for the current process and send opt-in updates, every four hours by default.
- Stop notifications or clear the selected city with a command.
- Handle unknown cities, unavailable APIs and malformed responses without exposing API keys.
- Reuse recent successful forecasts with a bounded, five-minute, in-memory cache.

This is a **city-level portfolio prototype**, not a live hosted service. No route analysis, city grid, evening-specific forecast, AI/ML model or severe-weather alerting is implemented in this release. The later route-aware experiment described in the broader project history is not included: its source is no longer available.

## Try the offline demo

The demo uses explicitly synthetic fixture data. It makes **no network requests** and requires **no API keys**.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m weather_assistant.demo
```

Example output from the fixture (not a live forecast):

```text
Waterford, Ireland
Local time: 2026-09-09 08:00
Light rain
Temperature: 13 C (feels like 11 C)
Wind: 5.0 m/s | Humidity: 82%
Pressure: 1012 hPa
Today's chance of rain: 70%

Consider a light jacket or sweater.
Rain is likely today; bring an umbrella or waterproof layer.

General guidance from a city-level forecast, not route-specific or safety advice.
```

## Run the bot

1. Create a bot with [Telegram's BotFather](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) and obtain a [WeatherAPI key](https://www.weatherapi.com/docs/).
2. Copy `.env.example` to `.env` in this directory (`cp .env.example .env`, or `Copy-Item .env.example .env` in PowerShell).
3. Fill in `TELEGRAM_BOT_TOKEN` and `WEATHER_API_KEY` **locally**. Never send or commit these values.
4. From this directory, run:

```bash
python -m weather_assistant
```

Open your bot in a **private chat** and try:

```text
/start
/weather Waterford, Ireland
/weather
/notify
/stop
/forget
```

A city can also be sent as plain text. `/notify` does not send immediately: the first update follows the configured interval. A successful new city lookup updates the notification destination city. Group messages are ignored. Only one process should poll a bot token at a time; see the [aiogram polling guide](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html).

### Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Telegram credential | Required |
| `WEATHER_API_KEY` | WeatherAPI credential | Required |
| `NOTIFICATION_INTERVAL_SECONDS` | Time between opted-in updates | `14400` (4 hours) |

Notification intervals must be between 60 seconds and 7 days. Consider provider quotas before reducing the interval. Package versions in `pyproject.toml` pin direct dependencies; they are not a complete transitive lockfile.

## Design

```text
Private chat
    |
    v
aiogram dispatcher -> Assistant (commands + per-chat state)
                          |                    |
                          v                    v
                   WeatherClient       NotificationManager
                   async HTTP + TTL     one task per chat
                          |
                          v
                  WeatherAPI forecast
                          |
                          v
                  Weather -> guidance -> plain-text reply
```

- `weather.py`: validates provider data, converts units, caches successful requests and formats recommendations.
- `bot.py`: keeps Telegram-specific handlers separate from forecast parsing and guidance; serializes commands within each chat.
- `notifications.py`: owns recurring task lifecycles, prevents duplicates, cancels on opt-out/shutdown and stops after a blocked-bot response.
- `config.py`: reads and validates environment variables without including credential values in errors.

### Engineering changes from the original prototype

This 2026 portfolio refactor is based on [`Weather3.0.py` in Justyvevo/TelegramBot](https://github.com/Justyvevo/TelegramBot/blob/40a2647c7fe01d239c93d12a106be3e3109276b6/Weather3.0.py). The original project predates this refactor; the new package and tests should not be presented as the original 2023 implementation.

- Replaced blocking `requests.get()` inside async handlers with HTTPX's async client and a request timeout.
- Replaced list comparisons for precipitation with numeric thresholds, including exactly 40% and 70%.
- Corrected pressure units: WeatherAPI's `pressure_mb` is equivalent to hPa, not mmHg.
- Made the previously unused cache functional and bounded its capacity.
- Removed duplicate weather fetches per notification and made notification tasks explicitly owned and cancellable.
- Replaced untracked `env.py` / `enw.py` dependencies with a documented `.env` contract.
- Migrated the curated version from aiogram 2 to aiogram 3 and separated responsibilities for testing.

The root-level scripts are historical learning examples, not the supported entry point. A separate 2026 cleanup removed unrelated meme handlers, clarified two filenames, moved legacy API configuration to environment variables and made the learning downloader preserve existing files. Legacy runtime behaviour has not been fully validated. Previously exposed credentials still require owner rotation; this cleanup does not erase Git history.

## Verification

```bash
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
```

Tests use fake HTTP responses, controlled notification timing and a fake Telegram session. They do not use credentials or send messages to real accounts. Automated checks validate local behaviour, not live provider connectivity or Linux deployment. A credentialed private-chat smoke test is still required before hosting.

## Limits and privacy

- General clothing guidance is subjective and deliberately simple; it is not safety advice.
- Daily rain probability is not the probability of rain at an exact time or along a route.
- Chat preferences and subscriptions are in memory, limited to 1,000 chat sessions. Restarting clears them; `/forget` clears a chat's selection and stops its notifications.
- The forecast cache holds up to 256 normalized city queries for reuse; `/forget` does not purge shared cached forecasts. Cached values are not linked to chat IDs.
- The bot has no database, route tracking or persistent user analytics. Telegram and WeatherAPI still process requests under their own terms.
- No distributed scheduling, durable subscriptions, global API-rate limiter, request coalescing or production monitoring is provided.
- Don't enable HTTP debug logs: provider request URLs can contain API keys. Never publish `.env`, chat exports or user data. Rotate any credentials that have been exposed.

## Linux deployment

See [deploy/README.md](deploy/README.md) for a systemd example. It is a deployment template, not evidence that this version is hosted.

## Next improvements

- Credentialed private-chat smoke test and a short recording of the running bot.
- Durable opt-in preferences and explicit data-retention controls.
- Rate limiting and request coalescing before opening a public service.
- Rebuild route-aware precipitation as a separately tested feature if the project is extended.

## References

- [WeatherAPI documentation](https://www.weatherapi.com/docs/) - forecast fields, units and errors.
- [aiogram documentation](https://docs.aiogram.dev/en/latest/) - messaging framework.
- [Original source](https://github.com/Justyvevo/TelegramBot) - project provenance.
