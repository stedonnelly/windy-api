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
        ("model", "parameters"),
        [
            (ModelTypes.AROME, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.AROME_Antilles, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.AROME_France, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.AROME_Reunion, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.ICONEU, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.ICON, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.ICOND2, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.GFS, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.GFS_WAVE, [ValidParameters.WAVES, ValidParameters.SWELL1]),
            (ModelTypes.ICON_WAVE, [ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1]),
            (ModelTypes.ICONEU_WAVE, [ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1]),
            (ModelTypes.CAN_RDWPS_WAVE, [ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1]),
            (ModelTypes.CMEMS_WAVE, [ValidParameters.CURRENTS, ValidParameters.CURRENTS_TIDE]),
            (ModelTypes.NAMCONUS, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.NAMHAWAII, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.NAMALASKA, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.HRRR_CONUS, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.HRRR_ALASKA, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.CAN_HRDPS, [ValidParameters.TEMP, ValidParameters.WIND]),
            (ModelTypes.CAMS, [ValidParameters.COSC, ValidParameters.DUSTSM]),
            (ModelTypes.CAMS_EU, [ValidParameters.COSC, ValidParameters.POLLEN_GRASS]),
        ],
    )
    def test_all_model_types(self, model, parameters, mock_api_key):
        """Test that all ModelTypes enum values are accepted."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=model,
            parameters=parameters,
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

    def test_icon_eu_supports_additional_surface_parameters(self, mock_api_key):
        """Test that iconEu accepts cbase, visibility, and weatherWarnings."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.ICONEU,
            parameters=[
                ValidParameters.CBASE,
                ValidParameters.VISIBILITY,
                ValidParameters.WEATHER_WARNINGS,
            ],
            key=mock_api_key,
        )
        assert "cbase" in request.parameters
        assert "visibility" in request.parameters
        assert "weatherWarnings" in request.parameters

    def test_icon_d2_supports_additional_surface_parameters(self, mock_api_key):
        """Test that iconD2 accepts cbase, visibility, and weatherWarnings."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.ICOND2,
            parameters=[
                ValidParameters.CBASE,
                ValidParameters.VISIBILITY,
                ValidParameters.WEATHER_WARNINGS,
            ],
            key=mock_api_key,
        )
        assert "cbase" in request.parameters
        assert "visibility" in request.parameters
        assert "weatherWarnings" in request.parameters

    def test_visibility_filtered_for_unsupported_model(self, mock_api_key):
        """Test that visibility is removed when requested for unsupported models."""
        with pytest.warns(UserWarning, match="not available for model 'gfs'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.GFS,
                parameters=[ValidParameters.VISIBILITY, ValidParameters.TEMP],
                key=mock_api_key,
            )
            assert "temp" in request.parameters
            assert "visibility" not in request.parameters

    def test_wave_parameters_valid_for_gfs_wave(self, mock_api_key):
        """Test that wave parameters are accepted for GFS Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.GFS_WAVE,
            parameters=[
                ValidParameters.WAVES,
                ValidParameters.WAVES_POWER,
                ValidParameters.WIND_WAVES,
                ValidParameters.SWELL1,
            ],
            key=mock_api_key,
        )
        assert "waves" in request.parameters
        assert "wavesPower" in request.parameters
        assert "windWaves" in request.parameters
        assert "swell1" in request.parameters

    def test_wave_parameters_valid_for_icon_wave(self, mock_api_key):
        """Test that wave parameters are accepted for ICON Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.ICON_WAVE,
            parameters=[ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1],
            key=mock_api_key,
        )
        assert "waves" in request.parameters
        assert "wavesPower" in request.parameters
        assert "swell1" in request.parameters

    def test_wave_parameters_valid_for_iconeu_wave(self, mock_api_key):
        """Test that wave parameters are accepted for ICON EU Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.ICONEU_WAVE,
            parameters=[ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1],
            key=mock_api_key,
        )
        assert "waves" in request.parameters
        assert "wavesPower" in request.parameters
        assert "swell1" in request.parameters

    def test_wave_parameters_valid_for_can_rdwps_wave(self, mock_api_key):
        """Test that wave parameters are accepted for CAN RDWPS Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CAN_RDWPS_WAVE,
            parameters=[ValidParameters.WAVES, ValidParameters.WAVES_POWER, ValidParameters.SWELL1],
            key=mock_api_key,
        )
        assert "waves" in request.parameters
        assert "wavesPower" in request.parameters
        assert "swell1" in request.parameters

    def test_current_parameters_valid_for_cmems_wave(self, mock_api_key):
        """Test that current parameters are accepted for CMEMS Wave model."""
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CMEMS_WAVE,
            parameters=[ValidParameters.CURRENTS, ValidParameters.CURRENTS_TIDE],
            key=mock_api_key,
        )
        assert "currents" in request.parameters
        assert "currentsTide" in request.parameters

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
        """Test that truly common parameters work for standard weather models."""
        # These parameters are available across standard weather models
        # (excluding specialized models like GFS_WAVE and CAMS)
        common_params = [ValidParameters.TEMP, ValidParameters.WIND, ValidParameters.RH]

        # Standard weather models that support common meteorological parameters
        standard_models = [
            ModelTypes.AROME,
            ModelTypes.ICONEU,
            ModelTypes.GFS,
            ModelTypes.NAMCONUS,
            ModelTypes.NAMHAWAII,
            ModelTypes.NAMALASKA,
        ]

        for model in standard_models:
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


class TestAirQualityParameters:
    """Test air quality model parameter availability."""

    def test_cams_supports_all_air_quality_params(self, mock_api_key):
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CAMS,
            parameters=[
                ValidParameters.AQI,
                ValidParameters.SO2SM,
                ValidParameters.DUSTSM,
                ValidParameters.COSC,
                ValidParameters.GO3,
                ValidParameters.NO2,
                ValidParameters.PM10,
                ValidParameters.PM2P5,
            ],
            key=mock_api_key,
        )
        assert "aqi" in request.parameters
        assert "so2sm" in request.parameters
        assert "dustsm" in request.parameters
        assert "cosc" in request.parameters
        assert "go3" in request.parameters
        assert "no2" in request.parameters
        assert "pm10" in request.parameters
        assert "pm2p5" in request.parameters

    def test_cams_does_not_support_pollen(self, mock_api_key):
        with pytest.warns(UserWarning, match="not available for model 'cams'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.CAMS,
                parameters=[ValidParameters.COSC, ValidParameters.POLLEN_GRASS],
                key=mock_api_key,
            )
        assert "cosc" in request.parameters
        assert "pollenGrass" not in request.parameters

    def test_cams_eu_supports_pollen(self, mock_api_key):
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CAMS_EU,
            parameters=[
                ValidParameters.POLLEN_ALDER,
                ValidParameters.POLLEN_BIRCH,
                ValidParameters.POLLEN_GRASS,
                ValidParameters.POLLEN_MUGWORT,
                ValidParameters.POLLEN_OLIVE,
                ValidParameters.POLLEN_RAGWEED,
            ],
            key=mock_api_key,
        )
        assert "pollenAlder" in request.parameters
        assert "pollenBirch" in request.parameters
        assert "pollenGrass" in request.parameters
        assert "pollenMugwort" in request.parameters
        assert "pollenOlive" in request.parameters
        assert "pollenRagweed" in request.parameters

    def test_cams_eu_supports_all_cams_params(self, mock_api_key):
        request = WindyPointRequest(
            lat=0,
            lon=0,
            model=ModelTypes.CAMS_EU,
            parameters=[ValidParameters.AQI, ValidParameters.GO3, ValidParameters.NO2],
            key=mock_api_key,
        )
        assert "aqi" in request.parameters
        assert "go3" in request.parameters
        assert "no2" in request.parameters

    def test_pollen_invalid_for_cams(self, mock_api_key):
        with pytest.warns(UserWarning, match="not available for model 'cams'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.CAMS,
                parameters=[ValidParameters.DUSTSM, ValidParameters.POLLEN_BIRCH],
                key=mock_api_key,
            )
        assert "dustsm" in request.parameters
        assert "pollenBirch" not in request.parameters

    def test_air_quality_params_invalid_for_gfs(self, mock_api_key):
        with pytest.warns(UserWarning, match="not available for model 'gfs'"):
            request = WindyPointRequest(
                lat=0,
                lon=0,
                model=ModelTypes.GFS,
                parameters=[ValidParameters.TEMP, ValidParameters.AQI],
                key=mock_api_key,
            )
        assert "temp" in request.parameters
        assert "aqi" not in request.parameters
