# Local verification

Verified on 9 September 2026 with Python 3.12.14 on Windows, in an isolated virtual environment.

| Check | Result |
| --- | --- |
| Install package and development dependencies | Passed |
| `python -m unittest discover -s tests -q` | 53 tests passed |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed |
| `python -m pip check` | No broken requirements |
| Offline demo | Ran successfully, no API keys or network calls |
| README sample vs executable formatter output | Exact match |
| Original tracked files in parent repository | Unchanged |

The tests cover forecast parsing, units, advice thresholds, cache expiry/eviction, API errors, query parameter encoding, configuration, per-chat state, cancellation, duplicate notifications, blocked destinations, fake Telegram dispatch and application startup/shutdown.

## Not yet verified

- Live WeatherAPI or Telegram requests with real credentials.
- A continuously hosted service or delivery of real notifications.
- The Linux/systemd deployment template.
- The GitHub Actions workflow running on GitHub. It is prepared for Ubuntu/Python 3.11 and Windows/Python 3.12, but has not been published or executed there.
- Route/grid functionality, which is not implemented in this package.

This report is a local verification snapshot, not evidence of production usage or historical deployment of the refactored version.
