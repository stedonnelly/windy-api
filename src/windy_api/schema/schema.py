from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WindyForecastResponse(BaseModel):
    """
    Response from Windy API forecast endpoint.

    The response contains timestamps, units, and dynamic parameter-level data.
    Access data using get_data() method or directly via attributes.

    Example:
        >>> response = WindyForecastResponse(**api_response)
        >>> response.ts  # List of datetime objects
        >>> response.units  # Dict of units for each parameter-level
        >>> response.get_data("temp-surface")  # Get temperature data
    """

    model_config = ConfigDict(extra="allow")  # Allow dynamic parameter-level fields

    ts: list[datetime] = Field(description="Timestamps converted from milliseconds since epoch")
    units: dict[str, str | None] = Field(description="Units for each parameter-level combination")

    @field_validator("ts", mode="before")
    @classmethod
    def convert_timestamps(cls, v):
        """Convert millisecond timestamps to UTC datetime objects"""
        if not v:
            return v
        if isinstance(v[0], datetime):
            return v
        # Convert from milliseconds to seconds and create UTC datetime objects
        return [datetime.fromtimestamp(ts / 1000, tz=timezone.utc) for ts in v]

    def get_data(self, parameter_level: str) -> list[float | None] | None:
        """
        Get data for a specific parameter-level combination.

        Args:
            parameter_level: e.g., "temp-surface", "wind_u-surface"

        Returns:
            List of values or None if not present
        """
        # Extra fields in Pydantic v2 are stored in __pydantic_extra__
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            return self.__pydantic_extra__.get(parameter_level)
        return None

    def get_unit(self, parameter_level: str) -> str | None:
        """Get unit for a parameter-level combination."""
        return self.units.get(parameter_level)
