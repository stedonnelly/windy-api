"""Pytest configuration and fixtures for Windy API tests."""

from datetime import datetime, timezone

import pytest


@pytest.fixture()
def mock_api_key():
    """Return a test API key."""
    return "test_api_key_12345"


@pytest.fixture()
def valid_coordinates():
    """Return valid lat/lon coordinates."""
    return {"lat": 49.809, "lon": 16.787}


@pytest.fixture()
def mock_api_response_data():
    """
    Mock response data from Windy API.

    This represents a typical response with temperature and wind data
    at surface level for a 3-hour forecast.
    """
    return {
        "ts": [
            1700000000000,  # Millisecond timestamp
            1700010800000,  # +3 hours
            1700021600000,  # +6 hours
        ],
        "units": {
            "temp-surface": "°C",
            "wind_u-surface": "m/s",
            "wind_v-surface": "m/s",
        },
        "temp-surface": [15.2, 14.8, 14.3],
        "wind_u-surface": [3.5, 4.2, 4.8],
        "wind_v-surface": [2.1, 2.3, 2.6],
    }


@pytest.fixture()
def mock_api_response_multiple_levels():
    """
    Mock response with multiple pressure levels.
    """
    return {
        "ts": [1700000000000, 1700010800000],
        "units": {
            "temp-surface": "°C",
            "temp-850h": "°C",
            "wind_u-surface": "m/s",
            "wind_u-850h": "m/s",
        },
        "temp-surface": [15.2, 14.8],
        "temp-850h": [5.3, 5.1],
        "wind_u-surface": [3.5, 4.2],
        "wind_u-850h": [12.3, 13.1],
    }


@pytest.fixture()
def expected_timestamps():
    """Return expected datetime objects from mock timestamps."""
    return [
        datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
        datetime(2023, 11, 15, 1, 13, 20, tzinfo=timezone.utc),
        datetime(2023, 11, 15, 4, 13, 20, tzinfo=timezone.utc),
    ]


@pytest.fixture()
def mock_error_response():
    """Mock error response from API."""
    return {
        "error": "Invalid API key",
        "code": 401,
    }
