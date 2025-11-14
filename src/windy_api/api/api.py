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
    ) -> WindyForecastResponse:
        """Fetch point weather forecast data.

        Args:
            latitude (float): Latitude coordinate between -90 and 90.
            longitude (float): Longitude coordinate between -180 and 180.
            model (str): Weather model to use for the forecast.
            parameters (list[str]): List of weather parameters to include in the forecast.

        Returns:
            WindyForecastResponse: Weather forecast response data.
        """
        request_data = WindyPointRequest(
            lat=latitude,
            lon=longitude,
            model=model,
            parameters=parameters,
            key=self.api_key,
        )
        response = httpx.post(self.point_forecast_url, json=request_data.model_dump())
        response.raise_for_status()
        return WindyForecastResponse(**response.json())

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
            latitude (float): Latitude coordinate between -90 and 90.
            longitude (float): Longitude coordinate between -180 and 180.
            model (str): Weather model to use for the forecast.
            parameters (list[str]): List of weather parameters to include in the forecast.
            levels (list[Levels], optional): List of atmospheric levels.

        Returns:
            WindyForecastResponse: Weather forecast response data.
        """
        if levels is None:
            levels = [Levels.SURFACE]

        request_data = WindyPointRequest(
            lat=latitude,
            lon=longitude,
            model=model,
            parameters=parameters,
            levels=levels,
            key=self.api_key,
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(self.point_forecast_url, json=request_data.model_dump())
        response.raise_for_status()
        return WindyForecastResponse(**response.json())
