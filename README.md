# Windy API

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

Python Windy API package for interacting with the Windy API. Currently only supports access to the point forecast API.

## Features

- **Point Forecast API**: Get detailed weather forecasts for any geographic location using latitude/longitude coordinates
- **Multiple Weather Models**: Support for 7+ weather forecast models including GFS, ICON EU, GFS Wave, NAM regional models, and CAMS air quality
- **Comprehensive Parameters**: Access 20+ weather parameters including temperature, wind, precipitation, humidity, clouds, pressure, CAPE, and more
- **Automatic Validation**: Built-in parameter validation ensures only compatible parameters are requested for each model
- **Async Support**: Full async/await support for concurrent API requests with `get_point_forecast_async()`
- **Type Safety**: Strongly typed with Pydantic models for reliable data validation and IDE autocomplete
- **Easy Data Access**: Intuitive response objects with helper methods like `get_data()` and `get_unit()` for accessing forecast data
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

# Access forecast data
print(f"Timestamps: {response.ts}")
print(f"Temperature data: {response.get_data('temp-surface')}")
print(f"Temperature unit: {response.get_unit('temp-surface')}")
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

# Access each parameter
for timestamp in response.ts:
    print(f"Time: {timestamp}")

temp_data = response.get_data("temp-surface")
dewpoint_data = response.get_data("dewpoint-surface")
pressure_data = response.get_data("pressure-surface")
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

# Get wind components
wind_u = response.get_data("wind_u-surface")  # East-west component
wind_v = response.get_data("wind_v-surface")  # North-south component
wind_gust = response.get_data("windGust-surface")

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
<!-- prettier-ignore-end -->
