"""Tests for WindyAPI client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from windy_api.api.api import WindyAPI
from windy_api.models.point_request import ModelTypes
from windy_api.schema.schema import WindyForecastResponse


class TestWindyAPIInitialization:
    """Test API client initialization."""

    def test_init_with_api_key(self, mock_api_key):
        """Test initialization with API key."""
        client = WindyAPI(api_key=mock_api_key)
        assert client.api_key == mock_api_key
        assert client.point_forecast_url is not None

    def test_init_with_custom_url(self, mock_api_key):
        """Test initialization with custom URL."""
        custom_url = "https://custom.api.windy.com/point-forecast"
        client = WindyAPI(api_key=mock_api_key, point_forecast_url=custom_url)
        assert client.api_key == mock_api_key
        assert client.point_forecast_url == custom_url

    def test_default_url_is_set(self, mock_api_key):
        """Test that default URL is set when not provided."""
        client = WindyAPI(api_key=mock_api_key)
        assert (
            "api.windy.com" in client.point_forecast_url
            or "windy" in client.point_forecast_url.lower()
        )


class TestSyncGetPointForecast:
    """Test synchronous get_point_forecast method."""

    @patch("httpx.post")
    def test_successful_request(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_data
    ):
        """Test successful API request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Make request
        client = WindyAPI(api_key=mock_api_key)
        result = client.get_point_forecast(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            parameters=["temp", "wind"],
        )

        # Verify result
        assert isinstance(result, WindyForecastResponse)
        assert len(result.ts) == 3
        assert result.get_data("temp-surface") == [15.2, 14.8, 14.3]

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert mock_api_key in str(call_args)

    @patch("httpx.post")
    def test_request_with_all_parameters(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_data
    ):
        """Test request with all possible parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        result = client.get_point_forecast(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.ICONEU,
            parameters=["temp", "wind", "precip", "cloudcover"],
        )

        assert isinstance(result, WindyForecastResponse)
        mock_post.assert_called_once()

    @patch("httpx.post")
    def test_http_error_handling(self, mock_post, mock_api_key, valid_coordinates):
        """Test handling of HTTP errors."""
        # Setup mock to raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=mock_response
        )
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)

        with pytest.raises(httpx.HTTPStatusError):
            client.get_point_forecast(
                latitude=valid_coordinates["lat"],
                longitude=valid_coordinates["lon"],
                model=ModelTypes.GFS,
                parameters=["temp"],
            )

    @patch("httpx.post")
    def test_network_error_handling(self, mock_post, mock_api_key, valid_coordinates):
        """Test handling of network errors."""
        # Setup mock to raise network error
        mock_post.side_effect = httpx.RequestError("Connection failed", request=Mock())

        client = WindyAPI(api_key=mock_api_key)

        with pytest.raises(httpx.RequestError):
            client.get_point_forecast(
                latitude=valid_coordinates["lat"],
                longitude=valid_coordinates["lon"],
                model=ModelTypes.GFS,
                parameters=["temp"],
            )

    @patch("httpx.post")
    def test_invalid_json_response(self, mock_post, mock_api_key, valid_coordinates):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)

        with pytest.raises(ValueError, match="Invalid JSON"):
            client.get_point_forecast(
                latitude=valid_coordinates["lat"],
                longitude=valid_coordinates["lon"],
                model=ModelTypes.GFS,
                parameters=["temp"],
            )

    @patch("httpx.post")
    def test_coordinates_passed_correctly(self, mock_post, mock_api_key, mock_api_response_data):
        """Test that coordinates are passed correctly in the request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        lat, lon = 45.5, -122.6

        client.get_point_forecast(
            latitude=lat,
            longitude=lon,
            model=ModelTypes.GFS,
            parameters=["temp"],
        )

        # Check that coordinates were included in request
        call_args = mock_post.call_args
        request_json = call_args.kwargs.get("json", {})
        assert request_json.get("lat") == lat
        assert request_json.get("lon") == lon


class TestAsyncGetPointForecast:
    """Test asynchronous get_point_forecast_async method."""

    @pytest.mark.asyncio()
    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_async_successful_request(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_data
    ):
        """Test successful async API request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Make async request
        client = WindyAPI(api_key=mock_api_key)
        result = await client.get_point_forecast_async(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            parameters=["temp", "wind"],
        )

        # Verify result
        assert isinstance(result, WindyForecastResponse)
        assert len(result.ts) == 3
        assert result.get_data("temp-surface") == [15.2, 14.8, 14.3]

        # Verify request was made
        mock_post.assert_called_once()

    @pytest.mark.asyncio()
    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_async_http_error_handling(self, mock_post, mock_api_key, valid_coordinates):
        """Test async handling of HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Forbidden", request=Mock(), response=mock_response
        )
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_point_forecast_async(
                latitude=valid_coordinates["lat"],
                longitude=valid_coordinates["lon"],
                model=ModelTypes.GFS,
                parameters=["temp"],
            )

    @pytest.mark.asyncio()
    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_async_network_error_handling(self, mock_post, mock_api_key, valid_coordinates):
        """Test async handling of network errors."""
        mock_post.side_effect = httpx.RequestError("Connection timeout", request=Mock())

        client = WindyAPI(api_key=mock_api_key)

        with pytest.raises(httpx.RequestError):
            await client.get_point_forecast_async(
                latitude=valid_coordinates["lat"],
                longitude=valid_coordinates["lon"],
                model=ModelTypes.GFS,
                parameters=["temp"],
            )

    @pytest.mark.asyncio()
    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_async_with_multiple_parameters(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_multiple_levels
    ):
        """Test async request with multiple parameters and levels."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_multiple_levels
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        result = await client.get_point_forecast_async(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            parameters=["temp", "wind"],
        )

        assert isinstance(result, WindyForecastResponse)
        assert result.get_data("temp-surface") is not None
        assert result.get_data("temp-850h") is not None


class TestAPIRequestPayload:
    """Test that API request payload is constructed correctly."""

    @patch("httpx.post")
    def test_request_payload_structure(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_data
    ):
        """Test the structure of the request payload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        client.get_point_forecast(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            parameters=["temp", "wind"],
        )

        # Extract the JSON payload from the call
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs.get("json", {})

        # Verify payload structure
        assert "lat" in payload
        assert "lon" in payload
        assert "model" in payload
        assert "parameters" in payload
        assert "api_key" in payload

        # Verify values
        assert payload["lat"] == valid_coordinates["lat"]
        assert payload["lon"] == valid_coordinates["lon"]
        assert payload["api_key"] == mock_api_key

    @patch("httpx.post")
    def test_model_normalized_in_payload(
        self, mock_post, mock_api_key, valid_coordinates, mock_api_response_data
    ):
        """Test that model names are normalized in the payload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        client.get_point_forecast(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model="ICON-EU",  # Test with hyphenated, uppercase version
            parameters=["temp"],
        )

        # Verify model was normalized
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs.get("json", {})
        assert payload["model"] == "iconeu"  # Should be normalized


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("httpx.post")
    def test_boundary_latitude_values(self, mock_post, mock_api_key, mock_api_response_data):
        """Test with boundary latitude values."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)

        # Test north pole
        result = client.get_point_forecast(
            latitude=90.0,
            longitude=0.0,
            model=ModelTypes.GFS,
            parameters=["temp"],
        )
        assert isinstance(result, WindyForecastResponse)

        # Test south pole
        result = client.get_point_forecast(
            latitude=-90.0,
            longitude=0.0,
            model=ModelTypes.GFS,
            parameters=["temp"],
        )
        assert isinstance(result, WindyForecastResponse)

    @patch("httpx.post")
    def test_boundary_longitude_values(self, mock_post, mock_api_key, mock_api_response_data):
        """Test with boundary longitude values."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response_data
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)

        # Test date line
        result = client.get_point_forecast(
            latitude=0.0,
            longitude=180.0,
            model=ModelTypes.GFS,
            parameters=["temp"],
        )
        assert isinstance(result, WindyForecastResponse)

        result = client.get_point_forecast(
            latitude=0.0,
            longitude=-180.0,
            model=ModelTypes.GFS,
            parameters=["temp"],
        )
        assert isinstance(result, WindyForecastResponse)

    @patch("httpx.post")
    def test_single_parameter_request(self, mock_post, mock_api_key, valid_coordinates):
        """Test request with single parameter."""
        mock_response_single = {
            "ts": [1700000000000],
            "units": {"temp-surface": "°C"},
            "temp-surface": [15.2],
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_single
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = WindyAPI(api_key=mock_api_key)
        result = client.get_point_forecast(
            latitude=valid_coordinates["lat"],
            longitude=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            parameters=["temp"],
        )

        assert isinstance(result, WindyForecastResponse)
        assert result.get_data("temp-surface") == [15.2]
