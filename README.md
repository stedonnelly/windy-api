# Windy API

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
[![PyPi downloads][pypi-downloads]][pypi-link]

Python Windy API package for interacting with the Windy API. Currently only supports access to the point forecast API.

## Features

- **Point Forecast API**: Get detailed weather forecasts for any geographic location using latitude/longitude coordinates
- **Multiple Weather Models**: Support for 7+ weather forecast models including GFS, ICON EU, GFS Wave, NAM regional models, and CAMS air quality
- **Comprehensive Parameters**: Access 20+ weather parameters including temperature, wind, precipitation, humidity, clouds, pressure, CAPE, and more
- **Automatic Validation**: Built-in parameter validation ensures only compatible parameters are requested for each model
- **Async Support**: Full async/await support for concurrent API requests with `get_point_forecast_async()`
- **Type Safety**: Strongly typed with Pydantic models for reliable data validation and IDE autocomplete
- **Intuitive Data Access**: Clean accessor pattern for accessing forecast data - use `response.temp["surface"]`
- **Clean Representations**: Response objects display in a clean, readable format showing only high-level parameters
- **Error Handling**: Clear error messages and exceptions for robust application development



## Installation

```bash
python -m pip install windy_api
```

From source:
```bash
git clone https://github.com/stedonnelly/windy-api
cd windy-api
python -m pip install .
```

## Usage

### Quick Start

```python
from windy_api import WindyAPI

# Initialize the client with your API key
api = WindyAPI(api_key="your_api_key_here")

# Get point forecast for San Francisco
response = api.get_point_forecast(
    latitude=37.7749,
    longitude=-122.4194,
    model="gfs",
    parameters=["temp", "wind"]
)

# View the response structure
print(response)
# WindyForecastResponse(
#   timestamps=37 entries,
#   parameters=[temp, wind]
# )

# Access forecast data using clean accessor pattern
print(f"Timestamps: {response.ts}")
print(f"Temperature data: {response.temp['surface']}")
print(f"Temperature unit: {response.temp.units}")
print(f"Available levels: {response.temp.levels()}")

# Access wind components
print(f"Wind U component: {response.wind.u['surface']}")
print(f"Wind V component: {response.wind.v['surface']}")
print(f"Wind unit: {response.wind.u.units}")
```

### Available Weather Models

The following weather forecast models are supported:

- `gfs` - Global Forecast System (default)
- `iconeu` - ICON EU regional model
- `gfs_wave` - GFS Wave model
- `namconus` - NAM CONUS regional model
- `namhawaii` - NAM Hawaii regional model
- `namalaska` - NAM Alaska regional model
- `cams` - CAMS air quality model

### Available Parameters

Common weather parameters you can request:

- `temp` - Temperature
- `wind` - Wind speed and direction (returns `wind_u` and `wind_v` components)
- `windGust` - Wind gusts
- `dewpoint` - Dew point temperature
- `precip` - Precipitation
- `convPrecip` - Convective precipitation
- `snowPrecip` - Snow precipitation
- `cape` - Convective Available Potential Energy
- `pressure` - Atmospheric pressure
- `rh` - Relative humidity
- `lclouds`, `mclouds`, `hclouds` - Low/medium/high clouds
- `gh` - Geopotential height
- `ptype` - Precipitation type

### Model Parameter Checking

Upon submitting a request to the Windy API the request is validated. If a parameter is requested for a model that does not support it, the incompatible parameters will automatically be removed from the request on validation.

### Accessing Response Data

The response object provides a clean, intuitive accessor pattern for retrieving forecast data:

#### Parameter Accessors

For parameters with multiple levels (e.g., temperature at different altitudes):

```python
# Access data at specific levels
temp_surface = response.temp["surface"]  # Temperature at surface
temp_850h = response.temp["850h"]        # Temperature at 850 hPa

# Get the unit (same across all levels)
print(response.temp.units)  # "K" (Kelvin)

# List all available levels
print(response.temp.levels())  # ["surface", "1000h", "950h", ...]

# Iterate over all levels
for level, data in response.temp.items():
    print(f"{level}: {data}")
```

#### Surface-Only Parameters

For parameters that only have surface data:

```python
# Access values and units directly
precip_values = response.precip.values
precip_unit = response.precip.units

pressure_values = response.pressure.values
pressure_unit = response.pressure.units
```

#### Complex Parameters (Wind, Waves)

Some parameters have multiple components:

```python
# Wind has u (east-west) and v (north-south) components
wind_u = response.wind.u["surface"]
wind_v = response.wind.v["surface"]
print(response.wind.u.units)  # "m*s-1"

# Waves have height, period, and direction
wave_height = response.waves.height.values
wave_period = response.waves.period.values
wave_direction = response.waves.direction.values
print(response.waves.height.units)  # "m"
```

### Detailed Examples

#### Multiple Parameters

```python
# Request multiple weather parameters
response = api.get_point_forecast(
    latitude=40.7128,
    longitude=-74.0060,
    model="gfs",
    parameters=["temp", "dewpoint", "pressure", "rh", "precip"]
)

# View available parameters
print(f"Available parameters: {response.available_parameters()}")

# Access each parameter using the clean accessor pattern
for i, timestamp in enumerate(response.ts):
    print(f"Time: {timestamp}")
    print(f"  Temperature: {response.temp['surface'][i]} {response.temp.units}")
    print(f"  Dewpoint: {response.dewpoint['surface'][i]} {response.dewpoint.units}")
    print(f"  Pressure: {response.pressure.values[i]} {response.pressure.units}")
    print(f"  Relative Humidity: {response.rh['surface'][i]} {response.rh.units}")
    print(f"  Precipitation: {response.precip.values[i]} {response.precip.units}")
```

#### Working with Wind Data

```python
# Wind returns u and v components
response = api.get_point_forecast(
    latitude=51.5074,
    longitude=-0.1278,
    model="gfs",
    parameters=["wind", "windGust"]
)

# Access wind components using the accessor pattern
wind_u_data = response.wind.u["surface"]  # East-west component
wind_v_data = response.wind.v["surface"]  # North-south component
wind_gust_data = response.windGust.values  # Wind gusts

# Get units
print(f"Wind unit: {response.wind.u.units}")
print(f"Gust unit: {response.windGust.units}")

# Check available levels for wind
print(f"Available wind levels: {response.wind.u.levels()}")
```

#### Async Usage

```python
import asyncio
from windy_api import WindyAPI

async def get_forecasts():
    api = WindyAPI(api_key="your_api_key_here")

    # Fetch multiple locations concurrently
    responses = await asyncio.gather(
        api.get_point_forecast_async(37.7749, -122.4194, "gfs", ["temp"]),
        api.get_point_forecast_async(40.7128, -74.0060, "gfs", ["temp"]),
        api.get_point_forecast_async(51.5074, -0.1278, "gfs", ["temp"])
    )

    return responses

# Run the async function
responses = asyncio.run(get_forecasts())
```

#### Using Environment Variables for API Key

```python
import os
from dotenv import load_dotenv
from windy_api import WindyAPI

# Load API key from .env file
load_dotenv()
api = WindyAPI(api_key=os.getenv("WINDY_API_KEY"))

response = api.get_point_forecast(
    latitude=48.8566,
    longitude=2.3522,
    model="iconeu",  # Use ICON EU model for Europe
    parameters=["temp", "precip", "wind"]
)
```

#### Error Handling

```python
from httpx import HTTPStatusError

try:
    response = api.get_point_forecast(
        latitude=37.7749,
        longitude=-122.4194,
        model="gfs",
        parameters=["temp"]
    )
except HTTPStatusError as e:
    print(f"API request failed: {e.response.status_code}")
    print(f"Response: {e.response.text}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

### Getting Your API Key

To use this library, you need a Windy API key. Visit [Windy API](https://api.windy.com/) to register and obtain your API key.

## Compliance & Terms of Use

**Important:** This library is not affiliated with or endorsed by Windy.com. It is an unofficial Python wrapper for the Windy Map & Point Forecast API.

By using this library, you agree to comply with all of [Windy's official Terms of Use](https://account.windy.com/agreements/windy-api-map-and-point-forecast-terms-of-use) for their Map & Point Forecast API. This wrapper does not modify or relax any of Windy's terms — it simply provides Python bindings for easier integration.

### Key Requirements You Must Follow

#### 1. API Key Security

- **You must keep your API key confidential** — Never commit it to GitHub, share it publicly, or embed it in client-side applications
- **Private Application keys** must be held exclusively and cannot be shared with third parties
- **Use environment variables** to store your key securely (see example above)

From Windy's Terms: *"API Keys for the Private Application are considered confidential and must be held exclusively. Allowing use of an API Key to a Private Application by any third party is forbidden. Usage of an API Key to a Private Application by any third party shall be considered a material breach of the Agreement."*

#### 2. No Data Storage or Extraction

Windy explicitly prohibits storing, extracting, or creating derivative weather databases:

- ❌ No long-term storage of weather data
- ❌ No creating weather databases or derived datasets
- ❌ No bulk downloading or archiving forecast data
- ❌ No reconstructing original meteorological model data

From Windy's Terms: *"Users cannot store, extract, modify, distribute, use the weather data or other content of the Services, create any weather works or databases derived therefrom"*

#### 3. Attribution Requirements

If you build an application that displays weather data to end users, you must include:

- The **Windy logo** (unscaled, 100% opacity, clickable with hyperlink to https://www.windy.com)
- **Text attribution**: "Contains data from the Windy database"
- Additional data source credits in Help or About sections

**Example Attribution (HTML):**
```html
<a href="https://www.windy.com" target="_blank">
  <img src="https://www.windy.com/img/logo300.png" alt="Windy Logo" />
</a>
<p>Contains data from the Windy database</p>
```

#### 4. No Replicating Windy Services

You cannot create applications that:

- ❌ Replicate Windy's services or aim to compete directly with Windy
- ❌ Provide Windy API data as a service to third parties
- ❌ Act as an API proxy or forwarding service

From Windy's Terms: *"The User is not allowed to create User Applications that would aim to replicate the Services or other services of the Provider."*

#### 5. Usage Limits

- **Trial Version**: 500 sessions/day maximum (development purposes only, not for production)
- **Professional Version**: 10,000 sessions/day (expandable upon request, requires paid plan)

### License Notice

The code in this repository is licensed under the [MIT License](LICENSE), but **the Windy API data is not**. All weather data remains the property of Windy.com and is governed by their [Terms of Use](https://account.windy.com/agreements/windy-api-map-and-point-forecast-terms-of-use).

### Best Practices for Compliance

1. **Use environment variables** for API keys (never hardcode them)
2. **Cache responsibly** — keep cached data in-memory or with very short TTL
3. **Add attribution** if you display data to users
4. **Respect rate limits** — implement backoff strategies for failed requests
5. **Review Windy's terms** before deploying to production

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.

## License

Distributed under the terms of the [MIT license](LICENSE).


<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/stedonnelly/windy-api/workflows/CI/badge.svg
[actions-link]:             https://github.com/stedonnelly/windy-api/actions
[pypi-link]:                https://pypi.org/project/windy-api/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/windy-api
[pypi-version]:             https://img.shields.io/pypi/v/windy-api
[pypi-downloads]:           https://img.shields.io/pypi/dm/windy-api
<!-- prettier-ignore-end -->
