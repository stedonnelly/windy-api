import warnings
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelTypes(str, Enum):
    """Available weather forecast models"""

    # Weather forecast models
    AROME = "arome"
    ICONEU = "iconEu"
    GFS = "gfs"
    NAMCONUS = "namConus"
    NAMHAWAII = "namHawaii"
    NAMALASKA = "namAlaska"
    # Sea and wave forecast models
    GFS_WAVE = "gfsWave"
    ICON_WAVE = "iconWave"
    ICONEU_WAVE = "iconEuWave"
    CAN_RDWPS_WAVE = "canRdwpsWave"
    CMEMS_WAVE = "cmems"
    # Atmospheric composition model
    CAMS = "cams"


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

    # Additional atmospheric parameters (CAMS only)
    SO2SM = "so2sm"  # Sulfur dioxide
    DUSTSM = "dustsm"
    COSC = "cosc"  # Carbon monoxide

    # Wave-specific parameters
    WAVES = "waves"
    WAVES_POWER = "wavesPower"
    WIND_WAVES = "windWaves"
    SWELL1 = "swell1"
    SWELL2 = "swell2"
    CURRENTS = "currents"
    CURRENTS_TIDE = "currentsTide"


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

GFS_WAVE_PARAMETERS = {
    ValidParameters.WAVES,
    ValidParameters.WAVES_POWER,
    ValidParameters.WIND_WAVES,
    ValidParameters.SWELL1,
    ValidParameters.SWELL2,
}

ICON_WAVE_PARAMETERS = {ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1}

CAN_RDWPS_WAVE_PARAMETERS = {
    ValidParameters.WAVES,
    ValidParameters.WAVES_POWER,
    ValidParameters.SWELL1,
    ValidParameters.SWELL2,
}

CMEMS_WAVE_PARAMETERS = {
    ValidParameters.CURRENTS,
    ValidParameters.CURRENTS_TIDE,
}

# Atmospheric composition parameters
ATMOSPHERIC_PARAMETERS = {
    ValidParameters.SO2SM,
    ValidParameters.DUSTSM,
    ValidParameters.COSC,
}


# Model-specific parameter availability mapping
MODEL_PARAMETER_MAP: dict[ModelTypes, set[ValidParameters]] = {
    # Weather forecast models
    ModelTypes.AROME: AROME_PARAMETERS,
    ModelTypes.ICONEU: COMMON_PARAMETERS,
    ModelTypes.GFS: COMMON_PARAMETERS,
    ModelTypes.NAMCONUS: COMMON_PARAMETERS,
    ModelTypes.NAMHAWAII: COMMON_PARAMETERS,
    ModelTypes.NAMALASKA: COMMON_PARAMETERS,
    # Sea and wave forecast models
    ModelTypes.GFS_WAVE: GFS_WAVE_PARAMETERS,
    ModelTypes.ICON_WAVE: ICON_WAVE_PARAMETERS,
    ModelTypes.ICONEU_WAVE: ICON_WAVE_PARAMETERS,
    ModelTypes.CAN_RDWPS_WAVE: CAN_RDWPS_WAVE_PARAMETERS,
    ModelTypes.CMEMS_WAVE: CMEMS_WAVE_PARAMETERS,
    # Atmospheric composition model
    ModelTypes.CAMS: ATMOSPHERIC_PARAMETERS,
}

MODEL_LEVELS_MAP: dict[ModelTypes, set[Levels]] = {
    # Weather forecast models
    ModelTypes.AROME: set(Levels),
    ModelTypes.ICONEU: set(Levels),
    ModelTypes.GFS: set(Levels),
    ModelTypes.NAMCONUS: set(Levels),
    ModelTypes.NAMHAWAII: set(Levels),
    ModelTypes.NAMALASKA: set(Levels),
    # Sea and wave forecast models
    ModelTypes.GFS_WAVE: {Levels.SURFACE},
    ModelTypes.ICON_WAVE: {Levels.SURFACE},
    ModelTypes.ICONEU_WAVE: {Levels.SURFACE},
    ModelTypes.CAN_RDWPS_WAVE: {Levels.SURFACE},
    ModelTypes.CMEMS_WAVE: {Levels.SURFACE},
    # Atmospheric composition model
    ModelTypes.CAMS: {Levels.SURFACE},
}


class WindyPointRequest(BaseModel):
    """Request model for Windy Point Forecast API.

    Supports multiple weather models with model-specific parameter availability:
    - GFS, ICONEU, NAM*: Common parameters only
    - AROME: Arome-specific parameters
    - GFS_WAVE: Common + wave parameters (waves, windWaves, swell1-3)
    - CAMS: Common + atmospheric parameters (so2sm, dustsm, cosc)
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
            "GFS_WAVE: waves, wavesPower, windWaves, swell1, swell2."
            "ICON_WAVE: waves, wavesPower, swell1."
            "CAN_RDWPS_WAVE: waves, wavesPower, swell1, swell2."
            "CMEMS_WAVE: currents, currentsTide."
            "Atmospheric (cams only): so2sm, dustsm, cosc"
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
