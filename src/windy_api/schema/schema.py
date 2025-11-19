from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .accessors import (
    COSC,
    SO2SM,
    DustSM,
    ParameterAccessor,
    Past3hConvPrecip,
    Past3hPrecip,
    Past3hSnowPrecip,
    Pressure,
    Swell1Accessor,
    Swell2Accessor,
    WaveAccessor,
    WindAccessor,
    WindGust,
    WindWaveAccessor,
    cape,
    hclouds,
    lclouds,
    mclouds,
    ptype,
)


class WindyForecastResponse(BaseModel):
    """
    Response from Windy API forecast endpoint.

    The response contains timestamps, units, and dynamic parameter-level data.
    Access data using get_data() method, ParameterAccessor, or directly via attributes.

    Example:
        >>> response = WindyForecastResponse(**api_response)
        >>> response.ts  # List of datetime objects
        >>> response.units  # Dict of units for each parameter-level

        # Direct access with level key
        >>> response.get_data("temp-surface")  # Get temperature data

        # Parameter accessor (automatically created)
        >>> response.temp["surface"]  # Get temperature data for surface level
        >>> response.temp.units  # Get unit for temp (e.g., "°C")
        >>> response.temp.levels()  # List all available temp levels

        # Wind has nested structure with u and v components
        >>> response.wind.u["850h"]  # Wind U component at 850 hPa
        >>> response.wind.v["surface"]  # Wind V component at surface
        >>> response.wind.u.units  # Get unit for wind U (e.g., "m/s")
        >>> response.wind.v.levels()  # List available levels for wind V
    """

    model_config = ConfigDict(extra="allow")  # Allow dynamic parameter-level fields

    ts: list[datetime] = Field(description="Timestamps converted from milliseconds since epoch")
    units: dict[str, str | None] = Field(description="Units for each parameter-level combination")

    def __init__(self, **data):
        super().__init__(**data)
        # Cache for accessor instances (ParameterAccessor or WindAccessor)
        self._accessor_cache: dict[
            str,
            ParameterAccessor
            | WindAccessor
            | WaveAccessor
            | WindWaveAccessor
            | Swell1Accessor
            | Swell2Accessor
            | Past3hPrecip
            | Past3hConvPrecip
            | Past3hSnowPrecip
            | WindGust
            | cape
            | ptype
            | lclouds
            | mclouds
            | hclouds
            | Pressure
            | SO2SM
            | DustSM
            | COSC,
        ] = {}

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

    def __dir__(self):
        """Return list of available attributes for IDE autocomplete."""
        # Start with base attributes from the parent class
        base_attrs = list(super().__dir__())

        # Add available parameters
        params = self._get_available_parameters()

        return sorted(set(base_attrs + params))

    def _get_available_parameters(self) -> list[str]:
        """
        Get list of high-level parameter names (clean parameter names for accessors).

        Returns:
            List of clean parameter names like ["temp", "wind", "waves", "windWaves"]
        """
        extra = getattr(self, "__pydantic_extra__", {}) or {}
        parameters = set()

        # Map of raw parameter prefixes to clean parameter names
        special_mappings = {
            "wind_u": "wind",
            "wind_v": "wind",
            "waves_height": "waves",
            "waves_period": "waves",
            "waves_direction": "waves",
            "wwaves_height": "windWaves",
            "wwaves_period": "windWaves",
            "wwaves_direction": "windWaves",
            "swell1_height": "swell1",
            "swell1_period": "swell1",
            "swell1_direction": "swell1",
            "swell2_height": "swell2",
            "swell2_period": "swell2",
            "swell2_direction": "swell2",
            "past3hprecip": "precip",
            "past3hconvprecip": "convPrecip",
            "past3hsnowprecip": "snowPrecip",
            "gust": "windGust",
        }

        for key in extra:
            if "-" in key:
                param = key.split("-", 1)[0]
                # Use special mapping if available, otherwise use the param as-is
                clean_param = special_mappings.get(param, param)
                parameters.add(clean_param)

        return sorted(parameters)

    def __getattr__(
        self, name: str
    ) -> (
        ParameterAccessor
        | WindAccessor
        | WaveAccessor
        | WindWaveAccessor
        | Swell1Accessor
        | Swell2Accessor
        | Past3hPrecip
        | Past3hConvPrecip
        | Past3hSnowPrecip
        | WindGust
        | cape
        | ptype
        | lclouds
        | mclouds
        | hclouds
        | Pressure
        | SO2SM
        | DustSM
        | COSC
    ):
        """
        Dynamically create accessors for parameter names.

        When you access response.temp, response.wind, etc., this method
        automatically creates and caches the appropriate accessor.

        Args:
            name: The parameter name (e.g., "temp", "wind", "rh")

        Returns:
            ParameterAccessor for simple parameters or specialized accessors for complex parameters

        Raises:
            AttributeError: If the attribute is not a valid parameter or if trying to access raw keys
        """
        # Prevent direct access to raw parameter-level keys (e.g., "temp-surface")
        if "-" in name:
            err_str = (
                f"Direct access to '{name}' is not allowed. "
                f"Use the accessor pattern instead (e.g., response.temp['surface'] for level-based parameters, "
                f"or response.waves.height.values for surface-only parameters)."
            )
            raise AttributeError(err_str)

        # Special case for wind - return composite accessor
        if name == "wind":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_wind_u = any(key.startswith("wind_u-") for key in extra)
            has_wind_v = any(key.startswith("wind_v-") for key in extra)

            if has_wind_u or has_wind_v:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = WindAccessor(self)
                return self._accessor_cache[name]

        elif name == "waves":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_waves_height = any(key.startswith("waves_height-") for key in extra)
            has_waves_direction = any(key.startswith("waves_direction-") for key in extra)

            if has_waves_height or has_waves_direction:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = WaveAccessor(self)
                return self._accessor_cache[name]

        elif name == "windWaves":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_wwaves_height = any(key.startswith("wwaves_height-") for key in extra)
            has_wwaves_direction = any(key.startswith("wwaves_direction-") for key in extra)

            if has_wwaves_height or has_wwaves_direction:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = WindWaveAccessor(self)
                return self._accessor_cache[name]

        elif name == "swell1":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_swell1_height = any(key.startswith("swell1_height-") for key in extra)
            has_swell1_direction = any(key.startswith("swell1_direction-") for key in extra)

            if has_swell1_height or has_swell1_direction:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Swell1Accessor(self)
                return self._accessor_cache[name]

        elif name == "swell2":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_swell2_height = any(key.startswith("swell2_height-") for key in extra)
            has_swell2_direction = any(key.startswith("swell2_direction-") for key in extra)

            if has_swell2_height or has_swell2_direction:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Swell2Accessor(self)
                return self._accessor_cache[name]

        elif name == "precip":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_precip = any(key.startswith("past3hprecip-") for key in extra)

            if has_precip:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Past3hPrecip(self)
                return self._accessor_cache[name]

        elif name == "convPrecip":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_conv_precip = any(key.startswith("past3hconvprecip-") for key in extra)

            if has_conv_precip:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Past3hConvPrecip(self)
                return self._accessor_cache[name]

        elif name == "snowPrecip":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_snow_precip = any(key.startswith("past3hsnowprecip-") for key in extra)

            if has_snow_precip:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Past3hSnowPrecip(self)
                return self._accessor_cache[name]

        elif name == "windGust":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_wind_gust = any(key.startswith("windGust-") for key in extra)

            if has_wind_gust:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = WindGust(self)
                return self._accessor_cache[name]

        elif name == "cape":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_cape = any(key.startswith("cape-") for key in extra)

            if has_cape:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = cape(self)
                return self._accessor_cache[name]

        elif name == "ptype":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_ptype = any(key.startswith("ptype-") for key in extra)

            if has_ptype:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = ptype(self)
                return self._accessor_cache[name]

        elif name == "lclouds":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_lclouds = any(key.startswith("lclouds-") for key in extra)

            if has_lclouds:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = lclouds(self)
                return self._accessor_cache[name]

        elif name == "mclouds":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_mclouds = any(key.startswith("mclouds-") for key in extra)

            if has_mclouds:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = mclouds(self)
                return self._accessor_cache[name]

        elif name == "hclouds":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_hclouds = any(key.startswith("hclouds-") for key in extra)

            if has_hclouds:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = hclouds(self)
                return self._accessor_cache[name]

        elif name == "pressure":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_pressure = any(key.startswith("pressure-") for key in extra)

            if has_pressure:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = Pressure(self)
                return self._accessor_cache[name]

        elif name == "so2sm":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_so2sm = any(key.startswith("so2sm-") for key in extra)

            if has_so2sm:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = SO2SM(self)
                return self._accessor_cache[name]

        elif name == "dustsm":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_dustsm = any(key.startswith("dustsm-") for key in extra)

            if has_dustsm:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = DustSM(self)
                return self._accessor_cache[name]

        elif name == "cosc":
            extra = getattr(self, "__pydantic_extra__", {}) or {}
            has_cosc = any(key.startswith("cosc-") for key in extra)

            if has_cosc:
                if name not in self._accessor_cache:
                    self._accessor_cache[name] = COSC(self)
                return self._accessor_cache[name]

        # Check if this is a parameter by looking for matching keys in extra data
        extra = getattr(self, "__pydantic_extra__", {}) or {}
        prefix = f"{name}-"

        # Check if any keys start with this parameter name
        has_parameter = any(key.startswith(prefix) for key in extra)

        if has_parameter:
            # Check cache first
            if name not in self._accessor_cache:
                self._accessor_cache[name] = ParameterAccessor(self, name)
            return self._accessor_cache[name]

        # If not a parameter, raise AttributeError with helpful message
        err_str = (
            f"'{self.__class__.__name__}' object has no attribute '{name}'. "
            f"Available parameters: {self.available_parameters()}"
        )
        raise AttributeError(err_str)

    def available_parameters(self) -> list[str]:
        """
        Get list of all available parameter names in this response.

        Returns:
            List of clean parameter names (accessor names)
            Example: ["temp", "wind", "waves", "windWaves", "rh"]
        """
        return self._get_available_parameters()

    def __repr__(self) -> str:
        """
        Clean representation of the response showing only high-level accessors.

        This hides the raw parameter-level data and shows the cleaner accessor structure.
        """
        params = self.available_parameters()
        param_str = ", ".join(params)

        return (
            f"WindyForecastResponse(\n" f"  timestamps={len(self.ts)} entries,\n" f"  parameters=[{param_str}]\n" f")"
        )

    def __str__(self) -> str:
        """String representation matching __repr__."""
        return self.__repr__()
