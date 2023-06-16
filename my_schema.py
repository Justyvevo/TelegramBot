from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class Astro:
    sunrise: str
    sunset: str

    @staticmethod
    def from_dict(obj: Any) -> 'Astro':
        _sunrise = str(obj.get("sunrise"))
        _sunset = str(obj.get("sunset"))
        return Astro(_sunrise, _sunset)

@dataclass
class Condition:
    code: int
    text: str
    icon: str

    @staticmethod
    def from_dict(obj: Any) -> 'Condition':
        _code = int(obj.get("code"))
        _text = str(obj.get("text"))
        _icon = str(obj.get("icon"))
        return Condition(_code, _text, _icon)

@dataclass
class Current:
    cloud: int
    condition: Condition
    feelslike_c: float
    feelslike_f: float
    humidity: int
    is_day: int
    last_updated: str
    last_updated_epoch: int
    precip_in: float
    precip_mm: float
    pressure_in: float
    pressure_mb: float
    temp_c: float
    uv: float
    wind_degree: int
    wind_dir: str
    wind_kph: float
    wind_mph: float

    @staticmethod
    def from_dict(obj: Any) -> 'Current':
        _cloud = int(obj.get("cloud"))
        _condition = Condition.from_dict(obj.get("condition"))
        _feelslike_c = float(obj.get("feelslike_c"))
        _feelslike_f = float(obj.get("feelslike_f"))
        _humidity = int(obj.get("humidity"))
        _is_day = int(obj.get("is_day"))
        _last_updated = str(obj.get("last_updated"))
        _last_updated_epoch = int(obj.get("last_updated_epoch"))
        _precip_in = float(obj.get("precip_in"))
        _precip_mm = float(obj.get("precip_mm"))
        _pressure_in = float(obj.get("pressure_in"))
        _pressure_mb = float(obj.get("pressure_mb"))
        _temp_c = float(obj.get("temp_c"))
        _uv = float(obj.get("uv"))
        _wind_degree = int(obj.get("wind_degree"))
        _wind_dir = str(obj.get("wind_dir"))
        _wind_kph = float(obj.get("wind_kph"))
        _wind_mph = float(obj.get("wind_mph"))
        return Current(_cloud, _condition, _feelslike_c, _feelslike_f, _humidity, _is_day, _last_updated, _last_updated_epoch, _precip_in, _precip_mm, _pressure_in, _pressure_mb, _temp_c, _uv, _wind_degree, _wind_dir, _wind_kph, _wind_mph)

@dataclass
class Day:
    condition: Condition
    daily_chance_of_rain: int
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    totalsnow_cm: float

    @staticmethod
    def from_dict(obj: Any) -> 'Day':
        _condition = Condition.from_dict(obj.get("condition"))
        _daily_chance_of_rain = int(obj.get("daily_chance_of_rain"))
        _maxtemp_c = float(obj.get("maxtemp_c"))
        _maxtemp_f = float(obj.get("maxtemp_f"))
        _mintemp_c = float(obj.get("mintemp_c"))
        _mintemp_f = float(obj.get("mintemp_f"))
        _totalsnow_cm = float(obj.get("totalsnow_cm"))
        return Day(_condition, _daily_chance_of_rain, _maxtemp_c, _maxtemp_f, _mintemp_c, _mintemp_f, _totalsnow_cm)

@dataclass
class Forecast:
    forecastday: List['Forecastday']

    @staticmethod
    def from_dict(obj: Any) -> 'Forecast':
        _forecastday = [Forecastday.from_dict(y) for y in obj.get("forecastday")]
        return Forecast(_forecastday)

@dataclass
class Forecastday:
    astro: Astro
    date: str
    date_epoch: int
    day: Day
    hour: List['Hour']

    @staticmethod
    def from_dict(obj: Any) -> 'Forecastday':
        _astro = Astro.from_dict(obj.get("astro"))
        _date = str(obj.get("date"))
        _date_epoch = int(obj.get("date_epoch"))
        _day = Day.from_dict(obj.get("day"))
        _hour = [Hour.from_dict(y) for y in obj.get("hour")]
        return Forecastday(_astro, _date, _date_epoch, _day, _hour)

@dataclass
class Hour:
    chance_of_rain: int
    condition: Condition
    feelslike_c: float
    gust_mph: float
    humidity: int
    precip_mm: float
    pressure_mb: float
    wind_dir: str
    wind_kph: float

    @staticmethod
    def from_dict(obj: Any) -> 'Hour':
        _chance_of_rain = int(obj.get("chance_of_rain"))
        _condition = Condition.from_dict(obj.get("condition"))
        _feelslike_c = float(obj.get("feelslike_c"))
        _gust_mph = float(obj.get("gust_mph"))
        _humidity = int(obj.get("humidity"))
        _precip_mm = float(obj.get("precip_mm"))
        _pressure_mb = float(obj.get("pressure_mb"))
        _wind_dir = str(obj.get("wind_dir"))
        _wind_kph = float(obj.get("wind_kph"))
        return Hour(_chance_of_rain, _condition, _feelslike_c, _gust_mph, _humidity, _precip_mm, _pressure_mb, _wind_dir, _wind_kph)

@dataclass
class Location:
    country: str
    lat: float
    localtime: str
    localtime_epoch: int
    lon: float
    name: str
    region: str
    tz_id: str

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        _country = str(obj.get("country"))
        _lat = float(obj.get("lat"))
        _localtime = str(obj.get("localtime"))
        _localtime_epoch = int(obj.get("localtime_epoch"))
        _lon = float(obj.get("lon"))
        _name = str(obj.get("name"))
        _region = str(obj.get("region"))
        _tz_id = str(obj.get("tz_id"))
        return Location(_country, _lat, _localtime, _localtime_epoch, _lon, _name, _region, _tz_id)

@dataclass
class Root:
    current: Current
    forecast: Forecast
    location: Location

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _current = Current.from_dict(obj.get("current"))
        _forecast = Forecast.from_dict(obj.get("forecast"))
        _location = Location.from_dict(obj.get("location"))
        return Root(_current, _forecast, _location)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)