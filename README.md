# Python Projects | Artemii Gubin

Independent Python experiments in messaging automation, weather data and API integration.

## Start here: Weather Assistant

The [curated Weather Assistant package](weather-assistant/README.md) turns a city forecast into practical clothing and rain guidance, with opt-in periodic notifications.

**Python · asyncio · aiogram · HTTPX · API integration · Linux/systemd**

It includes an offline demo, environment-based setup, tests and a deployment template. This is a 2026 refactor of the original city-level prototype, not a claim that the later improvements existed in the 2023 code.

```bash
cd weather-assistant
python -m venv .venv
# Activate .venv for your operating system, then:
python -m pip install -e ".[dev]"
python -m weather_assistant.demo
python -m unittest discover -s tests -v
```

## Original experiments

The root-level `Weather1.0.py`, `Weather2.0.py`, `Weather3.0.py`, other bot scripts and lesson files are preserved as historical learning work. They are not the entry point for the curated package and may require legacy dependencies or local configuration that is not included here.

The route-aware version discussed in the broader project history is not present; its source was lost. The runnable package documents only the city-level functionality available here.

## About

Artemii Gubin - BSc (Hons) Computer Science student at SETU, Cloud & Networks pathway, interested in software engineering internships.

[LinkedIn](https://www.linkedin.com/in/artemii-gubin-514a07386/)
