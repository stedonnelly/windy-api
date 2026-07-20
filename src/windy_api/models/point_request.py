import warnings
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelTypes(str, Enum):
    """Available weather forecast models"""

    AROME = "arome"
    ICONEU = "iconEu"
    GFS = "gfs"
    GFS_WAVE = "gfsWave"
    NAMCONUS = "namConus"
    NAMHAWAII = "namHawaii"
    NAMALASKA = "namAlaska"
    CAMS = "cams"
    CAMS_EU = "camsEu"


class ValidParameters(str, Enum):
    """Available forecast parameters"""

    # Common parameters (available across all models)
    TEMP = "temp"
    DEWPOINT = "dewpoint"
    PRECIP = "precip"
    CONV_PRECIP = "convPrecip"
    WIND = "wind"
    WIND_GUST = "windGust"
    CAPE = "cape"
    PTYPE = "ptype"
    LCLOUDS = "lclouds"
    MCLOUDS = "mclouds"
    HCLOUDS = "hclouds"
    RH = "rh"

    # Valid for all except AROME, gfsWave, cams
    SNOW_PRECIP = "snowPrecip"
    GH = "gh"
    PRESSURE = "pressure"

    # Wave-specific parameters (GFS Wave only)
    WAVES = "waves"
    WIND_WAVES = "windWaves"
    SWELL1 = "swell1"
    SWELL2 = "swell2"

    # Air quality parameters (CAMS / camsEu)
    AQI = "aqi"  # Air Quality Index (US standard, 0-500)
    SO2SM = "so2sm"  # Sulfur dioxide surface mass
    DUSTSM = "dustsm"  # Dust surface mass
    COSC = "cosc"  # Carbon monoxide concentration
    GO3 = "go3"  # Ground-level ozone concentration
    NO2 = "no2"  # Nitrogen dioxide concentration
    PM10 = "pm10"  # Particulate matter ≤10 µm
    PM2P5 = "pm2p5"  # Fine particulate matter ≤2.5 µm

    # Pollen parameters (camsEu only)
    POLLEN_ALDER = "pollenAlder"
    POLLEN_BIRCH = "pollenBirch"
    POLLEN_GRASS = "pollenGrass"
    POLLEN_MUGWORT = "pollenMugwort"
    POLLEN_OLIVE = "pollenOlive"
    POLLEN_RAGWEED = "pollenRagweed"


class Levels(str, Enum):
    SURFACE = "surface"
    H1000 = "1000h"
    H950 = "950h"
    H925 = "925h"
    H900 = "900h"
    H850 = "850h"
    H800 = "800h"
    H700 = "700h"
    H600 = "600h"
    H500 = "500h"
    H400 = "400h"
    H300 = "300h"
    H200 = "200h"
    H150 = "150h"


# Common parameters available across all models
COMMON_PARAMETERS = {
    ValidParameters.TEMP,
    ValidParameters.DEWPOINT,
    ValidParameters.PRECIP,
    ValidParameters.CONV_PRECIP,
    ValidParameters.SNOW_PRECIP,
    ValidParameters.WIND,
    ValidParameters.WIND_GUST,
    ValidParameters.CAPE,
    ValidParameters.PTYPE,
    ValidParameters.LCLOUDS,
    ValidParameters.MCLOUDS,
    ValidParameters.HCLOUDS,
    ValidParameters.RH,
    ValidParameters.GH,
    ValidParameters.PRESSURE,
}

# Wave parameters only available for GFS Wave model
WAVE_PARAMETERS = {
    ValidParameters.WAVES,
    ValidParameters.WIND_WAVES,
    ValidParameters.SWELL1,
    ValidParameters.SWELL2,
}

AROME_PARAMETERS = {
    ValidParameters.TEMP,
    ValidParameters.DEWPOINT,
    ValidParameters.PRECIP,
    ValidParameters.CONV_PRECIP,
    ValidParameters.WIND,
    ValidParameters.WIND_GUST,
    ValidParameters.CAPE,
    ValidParameters.PTYPE,
    ValidParameters.LCLOUDS,
    ValidParameters.MCLOUDS,
    ValidParameters.HCLOUDS,
    ValidParameters.RH,
}

# Atmospheric composition parameters
ATMOSPHERIC_PARAMETERS = {
    ValidParameters.AQI,
    ValidParameters.SO2SM,
    ValidParameters.DUSTSM,
    ValidParameters.COSC,
    ValidParameters.GO3,
    ValidParameters.NO2,
    ValidParameters.PM10,
    ValidParameters.PM2P5,
}

POLLEN_PARAMETERS = {
    ValidParameters.POLLEN_ALDER,
    ValidParameters.POLLEN_BIRCH,
    ValidParameters.POLLEN_GRASS,
    ValidParameters.POLLEN_MUGWORT,
    ValidParameters.POLLEN_OLIVE,
    ValidParameters.POLLEN_RAGWEED,
}

CAMS_EU_PARAMETERS = ATMOSPHERIC_PARAMETERS | POLLEN_PARAMETERS


# Model-specific parameter availability mapping
MODEL_PARAMETER_MAP: dict[ModelTypes, set[ValidParameters]] = {
    ModelTypes.AROME: AROME_PARAMETERS,
    ModelTypes.ICONEU: COMMON_PARAMETERS,
    ModelTypes.GFS: COMMON_PARAMETERS,
    ModelTypes.GFS_WAVE: WAVE_PARAMETERS,
    ModelTypes.NAMCONUS: COMMON_PARAMETERS,
    ModelTypes.NAMHAWAII: COMMON_PARAMETERS,
    ModelTypes.NAMALASKA: COMMON_PARAMETERS,
    ModelTypes.CAMS: ATMOSPHERIC_PARAMETERS,
    ModelTypes.CAMS_EU: CAMS_EU_PARAMETERS,
}

MODEL_LEVELS_MAP: dict[ModelTypes, set[Levels]] = {
    ModelTypes.AROME: set(Levels),
    ModelTypes.ICONEU: set(Levels),
    ModelTypes.GFS: set(Levels),
    ModelTypes.GFS_WAVE: {Levels.SURFACE},
    ModelTypes.NAMCONUS: set(Levels),
    ModelTypes.NAMHAWAII: set(Levels),
    ModelTypes.NAMALASKA: set(Levels),
    ModelTypes.CAMS: {Levels.SURFACE},
    ModelTypes.CAMS_EU: {Levels.SURFACE},
}


class WindyPointRequest(BaseModel):
    """Request model for Windy Point Forecast API.

    Supports multiple weather models with model-specific parameter availability:
    - GFS, ICONEU, NAM*: Common parameters only
    - AROME: Arome-specific parameters
    - GFS_WAVE: Common + wave parameters (waves, windWaves, swell1-3)
    - CAMS: Air quality parameters (aqi, so2sm, dustsm, cosc, go3, no2, pm10, pm2p5)
    - CAMS_EU: All CAMS parameters + pollen (alder, birch, grass, mugwort, olive, ragweed)
    """

    model_config = ConfigDict(use_enum_values=True)

    lat: float = Field(ge=-90, le=90, description="Latitude coordinate")
    lon: float = Field(ge=-180, le=180, description="Longitude coordinate")
    model: ModelTypes = Field(
        default=ModelTypes.GFS,
        description=(
            "Weather forecast model. "
            "Available: gfs (global), gfsWave (waves), cams (atmospheric), "
            "arome (France), iconEu (Europe), namConus/namHawaii/namAlaska"
        ),
    )
    parameters: list[ValidParameters] = Field(
        default_factory=lambda: [ValidParameters.TEMP, ValidParameters.WIND],
        description=(
            "Weather parameters to retrieve. "
            "Common (all models except AROME, gfsWave, cams): temp, dewpoint, precip, convPrecip, "
            "snowPrecip, wind, windGust, cape, ptype, lclouds, mclouds, hclouds, rh, gh, pressure. "
            "Arome-specific: temp, dewpoint, precip, convPrecip, wind, windGust, cape, ptype, "
            "lclouds, mclouds, hclouds, rh."
            "Wave (gfsWave only): waves, windWaves, swell1, swell2, swell3. "
            "Atmospheric (cams): aqi, so2sm, dustsm, cosc, go3, no2, pm10, pm2p5. "
            "Pollen (camsEu only): pollenAlder, pollenBirch, pollenGrass, pollenMugwort, pollenOlive, pollenRagweed."
        ),
    )
    levels: list[Levels] = Field(
        default_factory=lambda: [Levels.SURFACE],
        description="Atmospheric levels (e.g., 'surface', '850h', '500h')",
    )
    key: str = Field(description="Your Windy API key")

    @model_validator(mode="after")
    def validate_parameters_for_model(self) -> "WindyPointRequest":
        """Validate and filter parameters to only those available for the selected model."""
        available_params = MODEL_PARAMETER_MAP[ModelTypes(self.model)]
        invalid_params = [p for p in self.parameters if ValidParameters(p) not in available_params]

        if invalid_params:
            # Issue warning about invalid parameters
            warnings.warn(
                f"Parameters {invalid_params} are not available for model '{self.model}' "
                f"and will be removed. Available parameters: {sorted([p.value for p in available_params])}",
                UserWarning,
                stacklevel=2,
            )
            # Filter to only valid parameters
            self.parameters = [p for p in self.parameters if ValidParameters(p) in available_params]

        return self

    @model_validator(mode="after")
    def validate_levels_for_model(self) -> "WindyPointRequest":
        """Validate levels for the selected model."""
        available_levels = MODEL_LEVELS_MAP[ModelTypes(self.model)]
        invalid_levels = [level for level in self.levels if Levels(level) not in available_levels]
        if invalid_levels:
            warnings.warn(
                f"Levels {invalid_levels} are not available for model '{self.model}' "
                f"and will be removed. Available levels: {sorted([level.value for level in available_levels])}",
                UserWarning,
                stacklevel=2,
            )
            self.levels = [level for level in self.levels if Levels(level) in available_levels]
        if not self.levels:
            # Ensure at least one level remains
            err_msg = (
                f"After validation, no valid levels remain for model '{self.model}'. "
                f"Available levels: {sorted([level.value for level in available_levels])}"
            )
            raise ValueError(err_msg)

        return self
