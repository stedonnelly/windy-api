"""Tests for WindyPointRequest model."""

import pytest
from pydantic import ValidationError

from windy_api.models.point_request import (
    Levels,
    ModelTypes,
    ValidParameters,
    WindyPointRequest,
)


class TestWindyPointRequestValidation:
    """Test coordinate and field validation."""

    def test_valid_coordinates(self, mock_api_key, valid_coordinates):
        """Test that valid coordinates are accepted."""
        request = WindyPointRequest(
            lat=valid_coordinates["lat"],
            lon=valid_coordinates["lon"],
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        assert request.lat == valid_coordinates["lat"]
        assert request.lon == valid_coordinates["lon"]

    @pytest.mark.parametrize(
        "lat",
        [-90, -45.5, 0, 45.5, 90],
    )
    def test_latitude_boundary_values(self, lat, mock_api_key):
        """Test latitude accepts values from -90 to 90."""
        request = WindyPointRequest(
            lat=lat,
            lon=0,
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        assert request.lat == lat

    @pytest.mark.parametrize(
        "lat",
        [-90.1, -100, 90.1, 100],
    )
    def test_invalid_latitude(self, lat, mock_api_key):
        """Test that invalid latitudes raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            WindyPointRequest(
                lat=lat,
                lon=0,
                model=ModelTypes.GFS,
                api_key=mock_api_key,
            )
        assert "lat" in str(exc_info.value).lower()

    @pytest.mark.parametrize(
        "lon",
        [-180, -90, 0, 90, 180],
    )
    def test_longitude_boundary_values(self, lon, mock_api_key):
        """Test longitude accepts values from -180 to 180."""
        request = WindyPointRequest(
            lat=0,
            lon=lon,
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        assert request.lon == lon

    @pytest.mark.parametrize(
        "lon",
        [-180.1, -200, 180.1, 200],
    )
    def test_invalid_longitude(self, lon, mock_api_key):
        """Test that invalid longitudes raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            WindyPointRequest(
                lat=0,
                lon=lon,
                model=ModelTypes.GFS,
                api_key=mock_api_key,
            )
        assert "lon" in str(exc_info.value).lower()


class TestModelNormalization:
    """Test model name normalization."""

    @pytest.mark.parametrize(
        ("input_model", "expected"),
        [
            ("GFS", "gfs"),
            ("gfs", "gfs"),
            ("Gfs", "gfs"),
            ("icon-eu", "iconeu"),
            ("icon_eu", "iconeu"),
            ("ICON-EU", "iconeu"),
            ("ICONEU", "iconeu"),
            ("gfs-wave", "gfs_wave"),
            ("GFS_WAVE", "gfs_wave"),
            ("nam-conus", "namconus"),
            ("NAM_CONUS", "namconus"),
        ],
    )
    def test_model_normalization(self, input_model, expected, mock_api_key):
        """Test that model names are normalized correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=input_model,
            api_key=mock_api_key,
        )
        assert request.model == expected

    def test_invalid_model_name(self, mock_api_key):
        """Test that invalid model names raise ValueError."""
        with pytest.raises(ValueError, match="(?i)unknown model"):
            WindyPointRequest(
                lat=0,
                lon=0,
                model="invalid_model",
                api_key=mock_api_key,
            )

    def test_model_enum_usage(self, mock_api_key):
        """Test using ModelTypes enum directly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.ICONEU,
            api_key=mock_api_key,
        )
        assert request.model == "iconeu"


class TestParameterHandling:
    """Test parameter normalization and defaults."""

    def test_default_parameters(self, mock_api_key):
        """Test that default parameters are set correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        # Check defaults are set
        assert request.parameters is not None
        assert len(request.parameters) > 0

    def test_single_parameter_string(self, mock_api_key):
        """Test passing a single parameter as string."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            parameters=["temp"],
            api_key=mock_api_key,
        )
        assert "temp" in request.parameters

    def test_multiple_parameters_list(self, mock_api_key):
        """Test passing multiple parameters as list."""
        params = ["temp", "wind", "precip"]
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            parameters=params,
            api_key=mock_api_key,
        )
        for param in params:
            assert param in request.parameters

    def test_parameters_enum_usage(self, mock_api_key):
        """Test using ValidParameters enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            parameters=[ValidParameters.TEMP, ValidParameters.DEWPOINT],
            api_key=mock_api_key,
        )
        assert "temp" in request.parameters
        assert "dewpoint" in request.parameters

    @pytest.mark.parametrize(
        "param",
        [
            "temp",
            "wind",
            "dewpoint",
            "rh",
            "pressure",
            "cloudcover",
            "precip",
            "ptype",
            "snowcover",
            "lclouds",
            "mclouds",
            "hclouds",
            "visibility",
            "gust",
        ],
    )
    def test_all_valid_parameters(self, param, mock_api_key):
        """Test that all valid parameters are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            parameters=[param],
            api_key=mock_api_key,
        )
        assert param in request.parameters


class TestLevelsHandling:
    """Test atmospheric level handling."""

    def test_default_levels(self, mock_api_key):
        """Test that default level is set correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        # Check defaults are set
        assert request.levels is not None

    def test_single_level_string(self, mock_api_key):
        """Test passing a single level as string."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            levels=["surface"],
            api_key=mock_api_key,
        )
        assert "surface" in request.levels

    def test_multiple_levels_list(self, mock_api_key):
        """Test passing multiple levels as list."""
        levels = ["surface", "850h", "500h"]
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            levels=levels,
            api_key=mock_api_key,
        )
        for level in levels:
            assert level in request.levels

    def test_levels_enum_usage(self, mock_api_key):
        """Test using Levels enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            levels=[Levels.SURFACE, Levels.H850, Levels.H500],
            api_key=mock_api_key,
        )
        assert "surface" in request.levels
        assert "850h" in request.levels
        assert "500h" in request.levels

    @pytest.mark.parametrize(
        "level",
        [
            "surface",
            "1000h",
            "950h",
            "925h",
            "900h",
            "850h",
            "800h",
            "700h",
            "600h",
            "500h",
            "300h",
            "200h",
            "150h",
        ],
    )
    def test_all_valid_levels(self, level, mock_api_key):
        """Test that all valid levels are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            levels=[level],
            api_key=mock_api_key,
        )
        assert level in request.levels


class TestAPIKeyHandling:
    """Test API key handling."""

    def test_api_key_required(self):
        """Test that API key is required."""
        with pytest.raises(ValidationError) as exc_info:
            WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.GFS,
            )
        assert "api_key" in str(exc_info.value).lower()

    def test_api_key_stored(self, mock_api_key):
        """Test that API key is stored correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS,
            api_key=mock_api_key,
        )
        assert request.api_key == mock_api_key
