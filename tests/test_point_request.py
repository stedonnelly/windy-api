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
            key=mock_api_key,
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
            key=mock_api_key,
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
                key=mock_api_key,
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
            key=mock_api_key,
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
                key=mock_api_key,
            )
        assert "lon" in str(exc_info.value).lower()


class TestModelValidation:
    """Test model validation."""

    @pytest.mark.parametrize(
        "model",
        [
            ModelTypes.AROME,
            ModelTypes.ICONEU,
            ModelTypes.GFS,
            ModelTypes.GFS_WAVE,
            ModelTypes.NAMCONUS,
            ModelTypes.NAMHAWAII,
            ModelTypes.NAMALASKA,
            ModelTypes.CAMS,
        ],
    )
    def test_all_model_types(self, model, mock_api_key):
        """Test that all ModelTypes enum values are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=model,
            key=mock_api_key,
        )
        assert request.model == model.value


class TestParameterHandling:
    """Test parameter normalization and defaults."""

    def test_default_parameters(self, mock_api_key):
        """Test that default parameters are set correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            key=mock_api_key,
        )
        # Check defaults are set
        assert request.parameters is not None
        assert len(request.parameters) > 0

    def test_single_parameter_enum(self, mock_api_key):
        """Test passing a single parameter as enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            parameters=[ValidParameters.TEMP],
            key=mock_api_key,
        )
        assert "temp" in request.parameters

    def test_multiple_parameters_list(self, mock_api_key):
        """Test passing multiple parameters as list."""
        params = [ValidParameters.TEMP, ValidParameters.WIND, ValidParameters.PRECIP]
        request = WindyPointRequest(
            lat=0,
            lon=0,
            parameters=params,
            key=mock_api_key,
        )
        assert "temp" in request.parameters
        assert "wind" in request.parameters
        assert "precip" in request.parameters

    def test_parameters_enum_usage(self, mock_api_key):
        """Test using ValidParameters enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            parameters=[ValidParameters.TEMP, ValidParameters.DEWPOINT],
            key=mock_api_key,
        )
        assert "temp" in request.parameters
        assert "dewpoint" in request.parameters

    @pytest.mark.parametrize(
        "param",
        [
            ValidParameters.TEMP,
            ValidParameters.WIND,
            ValidParameters.DEWPOINT,
            ValidParameters.RH,
            ValidParameters.PRESSURE,
            ValidParameters.PRECIP,
            ValidParameters.CONV_PRECIP,
            ValidParameters.SNOW_PRECIP,
            ValidParameters.PTYPE,
            ValidParameters.LCLOUDS,
            ValidParameters.MCLOUDS,
            ValidParameters.HCLOUDS,
            ValidParameters.WIND_GUST,
            ValidParameters.CAPE,
            ValidParameters.GH,
        ],
    )
    def test_all_valid_parameters(self, param, mock_api_key):
        """Test that all valid parameters are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            parameters=[param],
            key=mock_api_key,
        )
        assert param.value in request.parameters


class TestLevelsHandling:
    """Test atmospheric level handling."""

    def test_default_levels(self, mock_api_key):
        """Test that default level is set correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            key=mock_api_key,
        )
        # Check defaults are set
        assert request.levels is not None

    def test_single_level_enum(self, mock_api_key):
        """Test passing a single level as enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            levels=[Levels.SURFACE],
            key=mock_api_key,
        )
        assert "surface" in request.levels

    def test_multiple_levels_list(self, mock_api_key):
        """Test passing multiple levels as list."""
        levels = [Levels.SURFACE, Levels.H850, Levels.H500]
        request = WindyPointRequest(
            lat=0,
            lon=0,
            levels=levels,
            key=mock_api_key,
        )
        assert "surface" in request.levels
        assert "850h" in request.levels
        assert "500h" in request.levels

    def test_levels_enum_usage(self, mock_api_key):
        """Test using Levels enum."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            levels=[Levels.SURFACE, Levels.H850, Levels.H500],
            key=mock_api_key,
        )
        assert "surface" in request.levels
        assert "850h" in request.levels
        assert "500h" in request.levels

    @pytest.mark.parametrize(
        "level",
        [
            Levels.SURFACE,
            Levels.H1000,
            Levels.H950,
            Levels.H925,
            Levels.H900,
            Levels.H850,
            Levels.H800,
            Levels.H700,
            Levels.H600,
            Levels.H500,
            Levels.H400,
            Levels.H300,
            Levels.H200,
            Levels.H150,
        ],
    )
    def test_all_valid_levels(self, level, mock_api_key):
        """Test that all valid levels are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            levels=[level],
            key=mock_api_key,
        )
        assert level.value in request.levels


class TestAPIKeyHandling:
    """Test API key handling."""

    def test_api_key_required(self):
        """Test that API key is required."""
        with pytest.raises(ValidationError) as exc_info:
            WindyPointRequest(
                lat=0,
                lon=0,
            )
        assert "key" in str(exc_info.value).lower()

    def test_api_key_stored(self, mock_api_key):
        """Test that API key is stored correctly."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            key=mock_api_key,
        )
        assert request.key == mock_api_key


class TestModelSpecificParameters:
    """Test model-specific parameter availability validation."""

    def test_wave_parameters_valid_for_gfs_wave(self, mock_api_key):
        """Test that wave parameters are accepted for GFS Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS_WAVE,
            parameters=[
                ValidParameters.TEMP,
                ValidParameters.WAVES,
                ValidParameters.WIND_WAVES,
                ValidParameters.SWELL1,
            ],
            key=mock_api_key,
        )
        assert "waves" in request.parameters
        assert "windWaves" in request.parameters
        assert "swell1" in request.parameters

    def test_wave_parameters_invalid_for_gfs(self, mock_api_key):
        """Test that wave parameters are filtered out for non-wave models."""
        with pytest.warns(UserWarning, match="not available for model 'gfs'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.GFS,
                parameters=[ValidParameters.WAVES, ValidParameters.TEMP],
                key=mock_api_key,
            )
            # Should have filtered out WAVES, keeping only TEMP
            assert "temp" in request.parameters
            assert "waves" not in request.parameters

    def test_wave_parameters_invalid_for_iconeu(self, mock_api_key):
        """Test that wave parameters are filtered out for ICON EU model."""
        with pytest.warns(UserWarning, match="not available for model 'iconEu'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.ICONEU,
                parameters=[
                    ValidParameters.WIND_WAVES,
                    ValidParameters.SWELL2,
                    ValidParameters.WIND,
                ],
                key=mock_api_key,
            )
            # Should have filtered out wave parameters, keeping only WIND
            assert "wind" in request.parameters
            assert "windWaves" not in request.parameters
            assert "swell2" not in request.parameters

    def test_atmospheric_parameters_valid_for_cams(self, mock_api_key):
        """Test that atmospheric parameters are accepted for CAMS model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CAMS,
            parameters=[
                ValidParameters.TEMP,
                ValidParameters.SO2SM,
                ValidParameters.DUSTSM,
                ValidParameters.COSC,
            ],
            key=mock_api_key,
        )
        assert "so2sm" in request.parameters
        assert "dustsm" in request.parameters
        assert "cosc" in request.parameters

    def test_atmospheric_parameters_invalid_for_gfs(self, mock_api_key):
        """Test that atmospheric parameters are filtered out for non-CAMS models."""
        with pytest.warns(UserWarning, match="not available for model 'gfs'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.GFS,
                parameters=[ValidParameters.SO2SM, ValidParameters.PRESSURE],
                key=mock_api_key,
            )
            # Should have filtered out SO2SM, keeping only PRESSURE
            assert "pressure" in request.parameters
            assert "so2sm" not in request.parameters

    def test_common_parameters_valid_for_all_models(self, mock_api_key):
        """Test that truly common parameters work for all models."""
        # These parameters are available across ALL models including AROME
        common_params = [ValidParameters.TEMP, ValidParameters.WIND, ValidParameters.RH]

        for model in ModelTypes:
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=model,
                parameters=common_params,
                key=mock_api_key,
            )
            assert "temp" in request.parameters
            assert "wind" in request.parameters
            assert "rh" in request.parameters

    def test_arome_model_with_common_parameters(self, mock_api_key):
        """Test AROME model accepts common parameters."""
        request = WindyPointRequest(
            lat=48.8566,  # Paris
            lon=2.3522,
            model=ModelTypes.AROME,
            parameters=[ValidParameters.TEMP, ValidParameters.WIND, ValidParameters.RH],
            key=mock_api_key,
        )
        assert request.model == "arome"
        assert "temp" in request.parameters
        assert "wind" in request.parameters
        assert "rh" in request.parameters
