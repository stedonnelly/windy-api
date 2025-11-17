import httpx

from windy_api.models.point_request import (
    Levels,
    ModelTypes,
    ValidParameters,
    WindyPointRequest,
)
from windy_api.schema.schema import WindyForecastResponse


class WindyAPI:
    """Windy API client for fetching weather forecast data."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.point_forecast_url = "https://api.windy.com/api/point-forecast/v2"

    def get_point_forecast(
        self,
        latitude: float,
        longitude: float,
        model: ModelTypes,
        parameters: list[ValidParameters],
        levels: list[Levels] | None = None,
    ) -> WindyForecastResponse:
        """Fetch point weather forecast data.

        Args:
            latitude: Latitude coordinate between -90 and 90.
            longitude: Longitude coordinate between -180 and 180.
            model: Weather forecast model to use.
                   - GFS, AROME, ICONEU, NAM*: Common parameters only
                   - GFS_WAVE: Common + wave parameters (waves, windWaves, swell1-3)
                   - CAMS: Common + atmospheric parameters (so2sm, dustsm, cosc)
            parameters: Weather parameters to retrieve.
                       Must be valid for the selected model.
            levels: Atmospheric levels (e.g., surface, 850h).
                   Defaults to [Levels.SURFACE].

        Returns:
            WindyForecastResponse: Weather forecast response data.

        Raises:
            ValueError: If parameters are not available for the selected model.
            httpx.HTTPStatusError: If the API request fails.

        Example:
            >>> api = WindyAPI(api_key="your-key")
            >>> forecast = api.get_point_forecast(
            ...     latitude=37.7749,
            ...     longitude=-122.4194,
            ...     model=ModelTypes.GFS,
            ...     parameters=[ValidParameters.TEMP, ValidParameters.WIND],
            ... )
        """
        request = WindyPointRequest(
            lat=latitude,
            lon=longitude,
            model=model,
            parameters=parameters,
            levels=levels or [Levels.SURFACE],
            key=self.api_key,
        )
        response = httpx.post(self.point_forecast_url, json=request.model_dump())
        response.raise_for_status()
        return WindyForecastResponse(**response.json())

    def get_model_types(self) -> list[str]:
        """Get available weather model types."""
        return [model.value for model in ModelTypes]

    def get_parameters_for_model(self, model: ModelTypes) -> list[str]:
        """Get available parameters for a specific weather model."""
        from windy_api.models.point_request import MODEL_PARAMETER_MAP

        available_params = MODEL_PARAMETER_MAP[model]
        return [param.value for param in available_params]

    def get_levels(self) -> list[str]:
        """Get available atmospheric levels."""
        return [level.value for level in Levels]

    async def get_point_forecast_async(
        self,
        latitude: float,
        longitude: float,
        model: ModelTypes,
        parameters: list[ValidParameters],
        levels: list[Levels] | None = None,
    ) -> WindyForecastResponse:
        """Fetch weather forecast data asynchronously.

        Args:
            latitude: Latitude coordinate between -90 and 90.
            longitude: Longitude coordinate between -180 and 180.
            model: Weather forecast model to use.
                   - GFS, AROME, ICONEU, NAM*: Common parameters only
                   - GFS_WAVE: Common + wave parameters (waves, windWaves, swell1-3)
                   - CAMS: Common + atmospheric parameters (so2sm, dustsm, cosc)
            parameters: Weather parameters to retrieve.
                       Must be valid for the selected model.
            levels: Atmospheric levels (e.g., surface, 850h).
                   Defaults to [Levels.SURFACE].

        Returns:
            WindyForecastResponse: Weather forecast response data.

        Raises:
            ValueError: If parameters are not available for the selected model.
            httpx.HTTPStatusError: If the API request fails.

        Example:
            >>> api = WindyAPI(api_key="your-key")
            >>> forecast = await api.get_point_forecast_async(
            ...     latitude=37.7749,
            ...     longitude=-122.4194,
            ...     model=ModelTypes.GFS,
            ...     parameters=[ValidParameters.TEMP, ValidParameters.WIND],
            ... )
        """
        request = WindyPointRequest(
            lat=latitude,
            lon=longitude,
            model=model,
            parameters=parameters,
            levels=levels or [Levels.SURFACE],
            key=self.api_key,
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(self.point_forecast_url, json=request.model_dump())
        response.raise_for_status()
        return WindyForecastResponse(**response.json())
