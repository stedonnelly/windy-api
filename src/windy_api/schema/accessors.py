from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from windy_api.schema.schema import WindyForecastResponse


class SurfaceDataAccessor:
    """
    Accessor for surface-only parameter data.

    Provides access to both values and units for a surface parameter:
        accessor.values - list of data values
        accessor.units - unit string (e.g., 'm', 's', 'deg')
    """

    def __init__(self, response: "WindyForecastResponse", parameter_key: str):
        self._response = response
        self._parameter_key = parameter_key

    @property
    def values(self) -> list[float | None] | None:
        """Get the data values for this parameter."""
        return self._response.get_data(self._parameter_key)

    @property
    def units(self) -> str | None:
        """Get the unit for this parameter."""
        return self._response.get_unit(self._parameter_key)

    def __repr__(self) -> str:
        return f"SurfaceDataAccessor(parameter='{self._parameter_key}', values='{self.values}', units='{self.units}')"


class ParameterAccessor:
    """
    Accessor for grouped parameter data across multiple levels.

    Allows accessing parameter data like: response.temp["surface"] or response.wind_u["850h"]
    Also provides units for all levels of this parameter via .units property
    """

    def __init__(self, response: "WindyForecastResponse", parameter: str):
        self._response = response
        self._parameter = parameter

    def __getitem__(self, level: str) -> list[float | None] | None:
        """Get data for parameter at specific level."""
        key = f"{self._parameter}-{level}"
        return self._response.get_data(key)

    def get(self, level: str, default: Any = None) -> list[float | None] | None:
        """Get data for parameter at specific level with optional default."""
        result = self[level]
        return result if result is not None else default

    def levels(self) -> list[str]:
        """Get all available levels for this parameter."""
        prefix = f"{self._parameter}-"
        extra = getattr(self._response, "__pydantic_extra__", {}) or {}
        return [key.replace(prefix, "") for key in extra if key.startswith(prefix)]

    def items(self) -> list[tuple[str, list[float | None] | None]]:
        """Get all level-data pairs for this parameter."""
        return [(level, self[level]) for level in self.levels()]

    @property
    def units(self) -> str | None:
        """
        Get the unit for this parameter (same across all levels).

        Returns:
            Unit string (e.g., "°C", "m/s", "%") or None if not available.
            Since units are consistent across levels, we just return the unit
            from the first available level.
        """
        levels = self.levels()
        if not levels:
            return None

        # Get unit from first level (units are the same across all levels)
        key = f"{self._parameter}-{levels[0]}"
        return self._response.get_unit(key)

    def __repr__(self) -> str:
        levels = self.levels()
        return f"ParameterAccessor(parameter='{self._parameter}', levels={levels})"


class WindAccessor:
    """
    Accessor for wind parameter with u and v components.

    Provides access to wind components like:
        response.wind.u["surface"] - wind U component at surface
        response.wind.v["850h"] - wind V component at 850 hPa
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response
        self._u_accessor: ParameterAccessor | None = None
        self._v_accessor: ParameterAccessor | None = None

    @property
    def u(self) -> ParameterAccessor:
        """Access wind U component (west-east direction)."""
        if self._u_accessor is None:
            self._u_accessor = ParameterAccessor(self._response, "wind_u")
        return self._u_accessor

    @property
    def v(self) -> ParameterAccessor:
        """Access wind V component (south-north direction)."""
        if self._v_accessor is None:
            self._v_accessor = ParameterAccessor(self._response, "wind_v")
        return self._v_accessor

    def __repr__(self) -> str:
        return f"WindAccessor(u={self.u.levels()}, v={self.v.levels()})"


class WaveAccessor:
    """
    Accessor for wave parameter with height, period, and direction components.

    Waves are surface-only parameters, so data is accessed directly without level specification.

    Provides access to wave components like:
        response.waves.height.values - wave height data (surface)
        response.waves.height.units - wave height unit (e.g., 'm')
        response.waves.period.values - wave period data (surface)
        response.waves.period.units - wave period unit (e.g., 's')
        response.waves.direction.values - wave direction data (surface)
        response.waves.direction.units - wave direction unit (e.g., 'deg')
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response
        self._height_accessor: SurfaceDataAccessor | None = None
        self._period_accessor: SurfaceDataAccessor | None = None
        self._direction_accessor: SurfaceDataAccessor | None = None

    @property
    def height(self) -> SurfaceDataAccessor:
        """Access wave height at surface."""
        if self._height_accessor is None:
            self._height_accessor = SurfaceDataAccessor(self._response, "waves_height-surface")
        return self._height_accessor

    @property
    def period(self) -> SurfaceDataAccessor:
        """Access wave period at surface."""
        if self._period_accessor is None:
            self._period_accessor = SurfaceDataAccessor(self._response, "waves_period-surface")
        return self._period_accessor

    @property
    def direction(self) -> SurfaceDataAccessor:
        """Access wave direction at surface."""
        if self._direction_accessor is None:
            self._direction_accessor = SurfaceDataAccessor(self._response, "waves_direction-surface")
        return self._direction_accessor

    def __repr__(self) -> str:
        return (
            f"WaveAccessor(height={self.height.values is not None}, "
            f"period={self.period.values is not None}, "
            f"direction={self.direction.values is not None})"
        )


class WindWaveAccessor:
    """
    Accessor for wind wave parameter with height, period, and direction components.

    Wind waves are surface-only parameters, so data is accessed directly without level specification.

    Provides access to wind wave components like:
        response.windWaves.height.values - wind wave height data (surface)
        response.windWaves.height.units - wind wave height unit (e.g., 'm')
        response.windWaves.period.values - wind wave period data (surface)
        response.windWaves.period.units - wind wave period unit (e.g., 's')
        response.windWaves.direction.values - wind wave direction data (surface)
        response.windWaves.direction.units - wind wave direction unit (e.g., 'deg')
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response
        self._height_accessor: SurfaceDataAccessor | None = None
        self._period_accessor: SurfaceDataAccessor | None = None
        self._direction_accessor: SurfaceDataAccessor | None = None

    @property
    def height(self) -> SurfaceDataAccessor:
        """Access wind wave height at surface."""
        if self._height_accessor is None:
            self._height_accessor = SurfaceDataAccessor(self._response, "wwaves_height-surface")
        return self._height_accessor

    @property
    def period(self) -> SurfaceDataAccessor:
        """Access wind wave period at surface."""
        if self._period_accessor is None:
            self._period_accessor = SurfaceDataAccessor(self._response, "wwaves_period-surface")
        return self._period_accessor

    @property
    def direction(self) -> SurfaceDataAccessor:
        """Access wind wave direction at surface."""
        if self._direction_accessor is None:
            self._direction_accessor = SurfaceDataAccessor(self._response, "wwaves_direction-surface")
        return self._direction_accessor

    def __repr__(self) -> str:
        return (
            f"WindWaveAccessor(height={self.height.values is not None}, "
            f"period={self.period.values is not None}, "
            f"direction={self.direction.values is not None})"
        )


class Swell1Accessor:
    """
    Accessor for swell1 parameter with height, period, and direction components.

    Swell1 are surface-only parameters, so data is accessed directly without level specification.

    Provides access to swell1 components like:
        response.swell1.height.values - swell1 height data (surface)
        response.swell1.height.units - swell1 height unit (e.g., 'm')
        response.swell1.period.values - swell1 period data (surface)
        response.swell1.period.units - swell1 period unit (e.g., 's')
        response.swell1.direction.values - swell1 direction data (surface)
        response.swell1.direction.units - swell1 direction unit (e.g., 'deg')
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response
        self._height_accessor: SurfaceDataAccessor | None = None
        self._period_accessor: SurfaceDataAccessor | None = None
        self._direction_accessor: SurfaceDataAccessor | None = None

    @property
    def height(self) -> SurfaceDataAccessor:
        """Access swell1 height at surface."""
        if self._height_accessor is None:
            self._height_accessor = SurfaceDataAccessor(self._response, "swell1_height-surface")
        return self._height_accessor

    @property
    def period(self) -> SurfaceDataAccessor:
        """Access swell1 period at surface."""
        if self._period_accessor is None:
            self._period_accessor = SurfaceDataAccessor(self._response, "swell1_period-surface")
        return self._period_accessor

    @property
    def direction(self) -> SurfaceDataAccessor:
        """Access swell1 direction at surface."""
        if self._direction_accessor is None:
            self._direction_accessor = SurfaceDataAccessor(self._response, "swell1_direction-surface")
        return self._direction_accessor

    def __repr__(self) -> str:
        return (
            f"Swell1Accessor(height={self.height.values is not None}, "
            f"period={self.period.values is not None}, "
            f"direction={self.direction.values is not None})"
        )


class Swell2Accessor:
    """
    Accessor for swell2 parameter with height, period, and direction components.

    Swell2 are surface-only parameters, so data is accessed directly without level specification.

    Provides access to swell2 components like:
        response.swell2.height.values - swell2 height data (surface)
        response.swell2.height.units - swell2 height unit (e.g., 'm')
        response.swell2.period.values - swell2 period data (surface)
        response.swell2.period.units - swell2 period unit (e.g., 's')
        response.swell2.direction.values - swell2 direction data (surface)
        response.swell2.direction.units - swell2 direction unit (e.g., 'deg')
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response
        self._height_accessor: SurfaceDataAccessor | None = None
        self._period_accessor: SurfaceDataAccessor | None = None
        self._direction_accessor: SurfaceDataAccessor | None = None

    @property
    def height(self) -> SurfaceDataAccessor:
        """Access swell2 height at surface."""
        if self._height_accessor is None:
            self._height_accessor = SurfaceDataAccessor(self._response, "swell2_height-surface")
        return self._height_accessor

    @property
    def period(self) -> SurfaceDataAccessor:
        """Access swell2 period at surface."""
        if self._period_accessor is None:
            self._period_accessor = SurfaceDataAccessor(self._response, "swell2_period-surface")
        return self._period_accessor

    @property
    def direction(self) -> SurfaceDataAccessor:
        """Access swell2 direction at surface."""
        if self._direction_accessor is None:
            self._direction_accessor = SurfaceDataAccessor(self._response, "swell2_direction-surface")
        return self._direction_accessor

    def __repr__(self) -> str:
        return (
            f"Swell2Accessor(height={self.height.values is not None}, "
            f"period={self.period.values is not None}, "
            f"direction={self.direction.values is not None})"
        )


class Past3hPrecip:
    """
    Accessor for precipitation parameters with rain and snow components.

    Provides access to precipitation components like:
        response.precip.values - total precipitation data
        response.precip.units - precipitation unit (e.g., 'm')
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access total precipitation data."""
        return self._response.get_data("past3hprecip-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for precipitation."""
        return self._response.get_unit("past3hprecip-surface")

    def __repr__(self) -> str:
        return f"Past3hprecip(values={self.values}, units={self.units})"


class Past3hSnowPrecip:
    """
    Accessor for snow precipitation parameters.

    Provides access to snow precipitation data like:
        response.precip.snow["surface"] - snow precipitation data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access snow precipitation data."""
        return self._response.get_data("past3hsnow-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for snow precipitation."""
        return self._response.get_unit("past3hsnow-surface")

    def __repr__(self) -> str:
        return f"Past3hSnowPrecip(values={self.values}, units={self.units})"


class Past3hConvPrecip:
    """
    Accessor for convective precipitation parameters.

    Provides access to convective precipitation data like:
        response.precip.convective["surface"] - convective precipitation data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access convective precipitation data."""
        return self._response.get_data("past3hconvprecip-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for convective precipitation."""
        return self._response.get_unit("past3hconvprecip-surface")

    def __repr__(self) -> str:
        return f"Past3hConvPrecip(values={self.values}, units={self.units})"


class WindGust:
    """
    Accessor for wind gust parameters.

    Provides access to wind gust data like:
        response.windGust["surface"] - wind gust data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access wind gust data."""
        return self._response.get_data("gust-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for wind gust."""
        return self._response.get_unit("gust-surface")

    def __repr__(self) -> str:
        return f"WindGust(values={self.values}, units={self.units})"


class cape:
    """
    Accessor for CAPE (Convective Available Potential Energy) parameters.

    Provides access to CAPE data like:
        response.cape["surface"] - CAPE data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access CAPE data."""
        return self._response.get_data("cape-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for CAPE."""
        return self._response.get_unit("cape-surface")

    def __repr__(self) -> str:
        return f"Cape(values={self.values}, units={self.units})"


class ptype:
    """
    Accessor for precipitation type (ptype) parameters.

    Provides access to ptype data like:
        response.ptype["surface"] - precipitation type data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access ptype data."""
        return self._response.get_data("ptype-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for ptype."""
        return self._response.get_unit("ptype-surface")

    def __repr__(self) -> str:
        return f"PType(values={self.values}, units={self.units})"


class lclouds:
    """
    Accessor for low cloud cover (lclouds) parameters.

    Provides access to lclouds data like:
        response.lclouds["surface"] - low cloud cover data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access lclouds data."""
        return self._response.get_data("lclouds-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for lclouds."""
        return self._response.get_unit("lclouds-surface")

    def __repr__(self) -> str:
        return f"LClouds(values={self.values}, units={self.units})"


class mclouds:
    """
    Accessor for medium cloud cover (mclouds) parameters.

    Provides access to mclouds data like:
        response.mclouds["surface"] - medium cloud cover data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access mclouds data."""
        return self._response.get_data("mclouds-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for mclouds."""
        return self._response.get_unit("mclouds-surface")

    def __repr__(self) -> str:
        return f"MClouds(values={self.values}, units={self.units})"


class hclouds:
    """
    Accessor for high cloud cover (hclouds) parameters.

    Provides access to hclouds data like:
        response.hclouds["surface"] - high cloud cover data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access hclouds data."""
        return self._response.get_data("hclouds-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for hclouds."""
        return self._response.get_unit("hclouds-surface")

    def __repr__(self) -> str:
        return f"HClouds(values={self.values}, units={self.units})"


class Pressure:
    """
    Accessor for pressure parameters.

    Provides access to pressure data like:
        response.pressure["surface"] - pressure data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access pressure data."""
        return self._response.get_data("pressure-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for pressure."""
        return self._response.get_unit("pressure-surface")

    def __repr__(self) -> str:
        return f"Pressure(values={self.values}, units={self.units})"


class SO2SM:
    """
    Accessor for SO2 surface mass (so2sm) parameters.

    Provides access to so2sm data like:
        response.so2sm["surface"] - SO2 surface mass data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access so2sm data."""
        return self._response.get_data("so2sm-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for so2sm."""
        return self._response.get_unit("so2sm-surface")

    def __repr__(self) -> str:
        return f"SO2SM(values={self.values}, units={self.units})"


class DustSM:
    """
    Accessor for dust surface mass (dustsm) parameters.

    Provides access to dustsm data like:
        response.dustsm["surface"] - dust surface mass data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access dustsm data."""
        return self._response.get_data("dustsm-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for dustsm."""
        return self._response.get_unit("dustsm-surface")

    def __repr__(self) -> str:
        return f"DustSM(values={self.values}, units={self.units})"


class COSC:
    """
    Accessor for carbon monoxide surface concentration (cosc) parameters.

    Provides access to cosc data like:
        response.cosc["surface"] - carbon monoxide surface concentration data at surface
    """

    def __init__(self, response: "WindyForecastResponse"):
        self._response = response

    @property
    def values(self) -> list[float | None] | None:
        """Access cosc data."""
        return self._response.get_data("cosc-surface")

    @property
    def units(self) -> str | None:
        """Get the unit for cosc."""
        return self._response.get_unit("cosc-surface")

    def __repr__(self) -> str:
        return f"COSC(values={self.values}, units={self.units})"
