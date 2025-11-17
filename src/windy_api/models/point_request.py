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


class ValidParameters(str, Enum):
    """Available forecast parameters"""

    # Common parameters (available across all models)
    TEMP = "temp"
    DEWPOINT = "dewpoint"
    PRECIP = "precip"
    CONV_PRECIP = "convPrecip"
    SNOW_PRECIP = "snowPrecip"
    WIND = "wind"
    WIND_GUST = "windGust"
    CAPE = "cape"
    PTYPE = "ptype"
    LCLOUDS = "lclouds"
    MCLOUDS = "mclouds"
    HCLOUDS = "hclouds"
    RH = "rh"
    GH = "gh"
    PRESSURE = "pressure"

    # Wave-specific parameters (GFS Wave only)
    WAVES = "waves"
    WIND_WAVES = "windWaves"
    SWELL1 = "swell1"
    SWELL2 = "swell2"
    SWELL3 = "swell3"

    # Additional atmospheric parameters (CAMS and other models)
    SO2SM = "so2sm"  # Sulfur dioxide
    DUSTSM = "dustsm"
    COSC = "cosc"  # Carbon monoxide


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
    ValidParameters.SWELL3,
}

# Atmospheric composition parameters
ATMOSPHERIC_PARAMETERS = {
    ValidParameters.SO2SM,
    ValidParameters.DUSTSM,
    ValidParameters.COSC,
}

# Model-specific parameter availability mapping
MODEL_PARAMETER_MAP: dict[ModelTypes, set[ValidParameters]] = {
    ModelTypes.AROME: COMMON_PARAMETERS,
    ModelTypes.ICONEU: COMMON_PARAMETERS,
    ModelTypes.GFS: COMMON_PARAMETERS,
    ModelTypes.GFS_WAVE: COMMON_PARAMETERS | WAVE_PARAMETERS,
    ModelTypes.NAMCONUS: COMMON_PARAMETERS,
    ModelTypes.NAMHAWAII: COMMON_PARAMETERS,
    ModelTypes.NAMALASKA: COMMON_PARAMETERS,
    ModelTypes.CAMS: COMMON_PARAMETERS | ATMOSPHERIC_PARAMETERS,
}


class WindyPointRequest(BaseModel):
    """Request model for Windy Point Forecast API"""

    model_config = ConfigDict(use_enum_values=True)

    lat: float = Field(ge=-90, le=90, description="Latitude coordinate")
    lon: float = Field(ge=-180, le=180, description="Longitude coordinate")
    model: ModelTypes = Field(default=ModelTypes.GFS, description="Forecast model to use")
    parameters: list[ValidParameters] = Field(
        default_factory=lambda: [ValidParameters.TEMP, ValidParameters.WIND],
        description="Parameters to retrieve from the forecast",
    )
    levels: list[Levels] = Field(
        default_factory=lambda: [Levels.SURFACE],
        description="Atmospheric levels (e.g., 'surface', '850h')",
    )
    key: str = Field(description="Your Windy API key")

    @model_validator(mode="after")
    def validate_parameters_for_model(self):
        """Validate that requested parameters are available for the selected model"""
        # With use_enum_values=True, model is stored as string, convert back to enum
        model = ModelTypes(self.model) if isinstance(self.model, str) else self.model

        # Get available parameters for this model
        available_params = MODEL_PARAMETER_MAP.get(model, COMMON_PARAMETERS)

        # With use_enum_values=True, parameters are stored as strings, convert back to enums
        requested_params = []
        for param in self.parameters:
            # At this point, all parameters are strings due to use_enum_values=True
            try:
                requested_params.append(ValidParameters(param))
            except ValueError as e:
                # If conversion fails, the parameter is invalid
                err_msg = (
                    f"Parameter '{param}' is not a valid ValidParameters enum value. "
                    f"Available parameters: {[p.value for p in available_params]}"
                )
                raise ValueError(err_msg) from e

        # Check if any requested parameter is not available for this model
        invalid_params = [p for p in requested_params if p not in available_params]

        if invalid_params:
            invalid_names = [p.value for p in invalid_params]
            available_names = sorted([p.value for p in available_params])
            err_msg = (
                f"Parameters {invalid_names} are not available for model '{model.value}'. "
                f"Available parameters: {available_names}"
            )
            raise ValueError(err_msg)
        return self
