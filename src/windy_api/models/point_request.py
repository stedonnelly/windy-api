from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelTypes(str, Enum):
    """Available weather forecast models"""

    ICONEU = "iconeu"
    GFS = "gfs"
    GFS_WAVE = "gfs_wave"
    NAMCONUS = "namconus"
    NAMHAWAII = "namhawaii"
    NAMALASKA = "namalaska"
    CAMS = "cams"


class ValidParameters(str, Enum):
    """Available forecast parameters"""

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
    H300 = "300h"
    H200 = "200h"
    H150 = "150h"


class WindyPointRequest(BaseModel):
    """Request model for Windy Point Forecast API"""

    model_config = ConfigDict(use_enum_values=True)

    lat: float = Field(ge=-90, le=90, description="Latitude coordinate")
    lon: float = Field(ge=-180, le=180, description="Longitude coordinate")
    model: str | ModelTypes = Field(
        default=ModelTypes.GFS, description="Forecast model to use"
    )
    parameters: list[str] = Field(
        default_factory=lambda: ["temp", "wind"],
        description="Parameters to retrieve from the forecast",
    )
    levels: list[Levels] = Field(
        default_factory=lambda: [Levels.SURFACE],
        description="Atmospheric levels (e.g., 'surface', '850h')",
    )
    key: str = Field(description="Your Windy API key")

    @field_validator("model", mode="before")
    @classmethod
    def normalize_model(cls, v):
        """Accept case-insensitive model names and common variations"""
        if isinstance(v, ModelTypes):
            return v

        # Create mapping of common variations to enum values
        model_map = {
            "iconeu": ModelTypes.ICONEU,
            "icon_eu": ModelTypes.ICONEU,
            "icon eu": ModelTypes.ICONEU,
            "gfs": ModelTypes.GFS,
            "gfs_wave": ModelTypes.GFS_WAVE,
            "gfswave": ModelTypes.GFS_WAVE,
            "gfs wave": ModelTypes.GFS_WAVE,
            "namconus": ModelTypes.NAMCONUS,
            "nam_conus": ModelTypes.NAMCONUS,
            "nam conus": ModelTypes.NAMCONUS,
            "namhawaii": ModelTypes.NAMHAWAII,
            "nam_hawaii": ModelTypes.NAMHAWAII,
            "nam hawaii": ModelTypes.NAMHAWAII,
            "namalaska": ModelTypes.NAMALASKA,
            "nam_alaska": ModelTypes.NAMALASKA,
            "nam alaska": ModelTypes.NAMALASKA,
            "cams": ModelTypes.CAMS,
        }

        normalized = model_map.get(str(v).lower().replace("-", " "))
        if not normalized:
            valid_models = ", ".join(f"'{e.value}'" for e in ModelTypes)
            err_str = f"Unknown model: '{v}'. Valid options: {valid_models}"
            raise ValueError(err_str)
        return normalized

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, v):
        """Accept parameter strings and normalize them"""
        if not v:
            return ["temp", "wind"]

        normalized = []
        for param in v:
            # If it's already a ValidParameters enum, extract the value
            if isinstance(param, ValidParameters):
                normalized.append(param.value)
            else:
                # Accept the string as-is and let the model validator check compatibility
                normalized.append(str(param).lower())
        return normalized
