"""Tests for accessor classes in WindyForecastResponse."""

import pytest

from windy_api.schema.schema import WindyForecastResponse


class TestParameterAccessor:
    """Test ParameterAccessor for multi-level parameters."""

    def test_getitem_access(self):
        """Test accessing data at specific level using bracket notation."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K", "temp-850h": "K"},
            "temp-surface": [299.0],
            "temp-850h": [285.0],
        }
        response = WindyForecastResponse(**data)

        assert response.temp["surface"] == [299.0]
        assert response.temp["850h"] == [285.0]

    def test_get_method_with_default(self):
        """Test get method with default value."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K"},
            "temp-surface": [299.0],
        }
        response = WindyForecastResponse(**data)

        # Existing level returns data
        assert response.temp.get("surface") == [299.0]

        # Non-existing level returns None by default
        assert response.temp.get("850h") is None

        # Non-existing level returns custom default
        assert response.temp.get("850h", []) == []

    def test_levels_method(self):
        """Test getting list of available levels."""
        data = {
            "ts": [1700000000000],
            "units": {
                "temp-surface": "K",
                "temp-1000h": "K",
                "temp-850h": "K",
            },
            "temp-surface": [299.0],
            "temp-1000h": [295.0],
            "temp-850h": [285.0],
        }
        response = WindyForecastResponse(**data)

        levels = response.temp.levels()
        assert "surface" in levels
        assert "1000h" in levels
        assert "850h" in levels
        assert len(levels) == 3

    def test_items_method(self):
        """Test iterating over level-data pairs."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K", "temp-850h": "K"},
            "temp-surface": [299.0],
            "temp-850h": [285.0],
        }
        response = WindyForecastResponse(**data)

        items = response.temp.items()
        assert len(items) == 2
        assert ("surface", [299.0]) in items
        assert ("850h", [285.0]) in items

    def test_units_property(self):
        """Test getting unit for parameter."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K", "temp-850h": "K"},
            "temp-surface": [299.0],
            "temp-850h": [285.0],
        }
        response = WindyForecastResponse(**data)

        assert response.temp.units == "K"

    def test_units_with_no_levels(self):
        """Test units property when no levels exist."""
        data = {
            "ts": [1700000000000],
            "units": {},
        }
        response = WindyForecastResponse(**data)

        # Create a parameter accessor for non-existent parameter
        try:
            _ = response.nonexistent
            pytest.fail("Should have raised AttributeError")
        except AttributeError:
            pass

    def test_repr(self):
        """Test ParameterAccessor string representation."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K", "temp-850h": "K"},
            "temp-surface": [299.0],
            "temp-850h": [285.0],
        }
        response = WindyForecastResponse(**data)

        repr_str = repr(response.temp)
        assert "ParameterAccessor" in repr_str
        assert "temp" in repr_str
        assert "levels=" in repr_str


class TestWindAccessor:
    """Test WindAccessor for wind components."""

    def test_wind_u_component(self):
        """Test accessing wind U component."""
        data = {
            "ts": [1700000000000],
            "units": {"wind_u-surface": "m*s-1", "wind_u-850h": "m*s-1"},
            "wind_u-surface": [5.0],
            "wind_u-850h": [15.0],
        }
        response = WindyForecastResponse(**data)

        assert response.wind.u["surface"] == [5.0]
        assert response.wind.u["850h"] == [15.0]
        assert response.wind.u.units == "m*s-1"

    def test_wind_v_component(self):
        """Test accessing wind V component."""
        data = {
            "ts": [1700000000000],
            "units": {"wind_v-surface": "m*s-1", "wind_v-850h": "m*s-1"},
            "wind_v-surface": [3.0],
            "wind_v-850h": [10.0],
        }
        response = WindyForecastResponse(**data)

        assert response.wind.v["surface"] == [3.0]
        assert response.wind.v["850h"] == [10.0]
        assert response.wind.v.units == "m*s-1"

    def test_wind_repr(self):
        """Test WindAccessor string representation."""
        data = {
            "ts": [1700000000000],
            "units": {"wind_u-surface": "m*s-1", "wind_v-surface": "m*s-1"},
            "wind_u-surface": [5.0],
            "wind_v-surface": [3.0],
        }
        response = WindyForecastResponse(**data)

        repr_str = repr(response.wind)
        assert "WindAccessor" in repr_str


class TestSurfaceDataAccessor:
    """Test SurfaceDataAccessor for surface-only parameters."""

    def test_precip_values(self):
        """Test accessing precipitation values."""
        data = {
            "ts": [1700000000000],
            "units": {"past3hprecip-surface": "m"},
            "past3hprecip-surface": [0.002],
        }
        response = WindyForecastResponse(**data)

        assert response.precip.values == [0.002]
        assert response.precip.units == "m"

    def test_precip_repr(self):
        """Test Past3hPrecip representation."""
        data = {
            "ts": [1700000000000],
            "units": {"past3hprecip-surface": "m"},
            "past3hprecip-surface": [0.002],
        }
        response = WindyForecastResponse(**data)

        repr_str = repr(response.precip)
        assert "Past3hprecip" in repr_str

    def test_snow_precip(self):
        """Test accessing snow precipitation."""
        data = {
            "ts": [1700000000000],
            "units": {"past3hsnow-surface": "m"},
            "past3hsnow-surface": [0.001],
        }
        response = WindyForecastResponse(**data)

        assert response.snowPrecip.values == [0.001]
        assert response.snowPrecip.units == "m"

    def test_conv_precip(self):
        """Test accessing convective precipitation."""
        data = {
            "ts": [1700000000000],
            "units": {"past3hconvprecip-surface": "m"},
            "past3hconvprecip-surface": [0.0005],
        }
        response = WindyForecastResponse(**data)

        assert response.convPrecip.values == [0.0005]
        assert response.convPrecip.units == "m"

    def test_wind_gust(self):
        """Test accessing wind gust."""
        data = {
            "ts": [1700000000000],
            "units": {"gust-surface": "m*s-1"},
            "gust-surface": [12.5],
        }
        response = WindyForecastResponse(**data)

        assert response.windGust.values == [12.5]
        assert response.windGust.units == "m*s-1"

    def test_cape(self):
        """Test accessing CAPE."""
        data = {
            "ts": [1700000000000],
            "units": {"cape-surface": "J*kg-1"},
            "cape-surface": [1500.0],
        }
        response = WindyForecastResponse(**data)

        assert response.cape.values == [1500.0]
        assert response.cape.units == "J*kg-1"

    def test_ptype(self):
        """Test accessing precipitation type."""
        data = {
            "ts": [1700000000000],
            "units": {"ptype-surface": None},
            "ptype-surface": [1],
        }
        response = WindyForecastResponse(**data)

        assert response.ptype.values == [1]
        assert response.ptype.units is None

    def test_lclouds(self):
        """Test accessing low clouds."""
        data = {
            "ts": [1700000000000],
            "units": {"lclouds-surface": "%"},
            "lclouds-surface": [45.0],
        }
        response = WindyForecastResponse(**data)

        assert response.lclouds.values == [45.0]
        assert response.lclouds.units == "%"

    def test_mclouds(self):
        """Test accessing medium clouds."""
        data = {
            "ts": [1700000000000],
            "units": {"mclouds-surface": "%"},
            "mclouds-surface": [30.0],
        }
        response = WindyForecastResponse(**data)

        assert response.mclouds.values == [30.0]
        assert response.mclouds.units == "%"

    def test_hclouds(self):
        """Test accessing high clouds."""
        data = {
            "ts": [1700000000000],
            "units": {"hclouds-surface": "%"},
            "hclouds-surface": [60.0],
        }
        response = WindyForecastResponse(**data)

        assert response.hclouds.values == [60.0]
        assert response.hclouds.units == "%"

    def test_pressure(self):
        """Test accessing pressure."""
        data = {
            "ts": [1700000000000],
            "units": {"pressure-surface": "Pa"},
            "pressure-surface": [101325.0],
        }
        response = WindyForecastResponse(**data)

        assert response.pressure.values == [101325.0]
        assert response.pressure.units == "Pa"

    def test_so2sm(self):
        """Test accessing SO2 surface mass."""
        data = {
            "ts": [1700000000000],
            "units": {"so2sm-surface": "kg*m-2"},
            "so2sm-surface": [0.0001],
        }
        response = WindyForecastResponse(**data)

        assert response.so2sm.values == [0.0001]
        assert response.so2sm.units == "kg*m-2"

    def test_dustsm(self):
        """Test accessing dust surface mass."""
        data = {
            "ts": [1700000000000],
            "units": {"dustsm-surface": "kg*m-2"},
            "dustsm-surface": [0.0002],
        }
        response = WindyForecastResponse(**data)

        assert response.dustsm.values == [0.0002]
        assert response.dustsm.units == "kg*m-2"

    def test_cosc(self):
        """Test accessing CO surface concentration."""
        data = {
            "ts": [1700000000000],
            "units": {"cosc-surface": "kg*m-3"},
            "cosc-surface": [0.00001],
        }
        response = WindyForecastResponse(**data)

        assert response.cosc.values == [0.00001]
        assert response.cosc.units == "kg*m-3"


class TestWaveAccessors:
    """Test wave-related accessors."""

    def test_waves_height(self):
        """Test accessing wave height."""
        data = {
            "ts": [1700000000000],
            "units": {"waves_height-surface": "m"},
            "waves_height-surface": [2.5],
        }
        response = WindyForecastResponse(**data)

        assert response.waves.height.values == [2.5]
        assert response.waves.height.units == "m"

    def test_waves_period(self):
        """Test accessing wave period."""
        data = {
            "ts": [1700000000000],
            "units": {
                "waves_height-surface": "m",
                "waves_period-surface": "s",
            },
            "waves_height-surface": [2.5],
            "waves_period-surface": [8.0],
        }
        response = WindyForecastResponse(**data)

        assert response.waves.period.values == [8.0]
        assert response.waves.period.units == "s"

    def test_waves_direction(self):
        """Test accessing wave direction."""
        data = {
            "ts": [1700000000000],
            "units": {
                "waves_height-surface": "m",
                "waves_direction-surface": "deg",
            },
            "waves_height-surface": [2.5],
            "waves_direction-surface": [180.0],
        }
        response = WindyForecastResponse(**data)

        assert response.waves.direction.values == [180.0]
        assert response.waves.direction.units == "deg"

    def test_waves_repr(self):
        """Test WaveAccessor representation."""
        data = {
            "ts": [1700000000000],
            "units": {"waves_height-surface": "m"},
            "waves_height-surface": [2.5],
        }
        response = WindyForecastResponse(**data)

        repr_str = repr(response.waves)
        assert "WaveAccessor" in repr_str

    def test_wind_waves(self):
        """Test accessing wind waves."""
        data = {
            "ts": [1700000000000],
            "units": {
                "wwaves_height-surface": "m",
                "wwaves_period-surface": "s",
                "wwaves_direction-surface": "deg",
            },
            "wwaves_height-surface": [1.5],
            "wwaves_period-surface": [6.0],
            "wwaves_direction-surface": [170.0],
        }
        response = WindyForecastResponse(**data)

        assert response.windWaves.height.values == [1.5]
        assert response.windWaves.period.values == [6.0]
        assert response.windWaves.direction.values == [170.0]

    def test_swell1(self):
        """Test accessing swell1."""
        data = {
            "ts": [1700000000000],
            "units": {
                "swell1_height-surface": "m",
                "swell1_period-surface": "s",
                "swell1_direction-surface": "deg",
            },
            "swell1_height-surface": [1.2],
            "swell1_period-surface": [10.0],
            "swell1_direction-surface": [190.0],
        }
        response = WindyForecastResponse(**data)

        assert response.swell1.height.values == [1.2]
        assert response.swell1.period.values == [10.0]
        assert response.swell1.direction.values == [190.0]

    def test_swell2(self):
        """Test accessing swell2."""
        data = {
            "ts": [1700000000000],
            "units": {
                "swell2_height-surface": "m",
                "swell2_period-surface": "s",
                "swell2_direction-surface": "deg",
            },
            "swell2_height-surface": [0.8],
            "swell2_period-surface": [12.0],
            "swell2_direction-surface": [200.0],
        }
        response = WindyForecastResponse(**data)

        assert response.swell2.height.values == [0.8]
        assert response.swell2.period.values == [12.0]
        assert response.swell2.direction.values == [200.0]


class TestAvailableParameters:
    """Test available_parameters method."""

    def test_available_parameters_basic(self):
        """Test getting available parameters."""
        data = {
            "ts": [1700000000000],
            "units": {"temp-surface": "K", "wind_u-surface": "m*s-1"},
            "temp-surface": [299.0],
            "wind_u-surface": [5.0],
        }
        response = WindyForecastResponse(**data)

        params = response.available_parameters()
        assert "temp" in params
        assert "wind" in params

    def test_available_parameters_wave(self):
        """Test available parameters includes wave parameters."""
        data = {
            "ts": [1700000000000],
            "units": {
                "waves_height-surface": "m",
                "windWaves_height-surface": "m",
            },
            "waves_height-surface": [2.5],
            "wwaves_height-surface": [1.5],
        }
        response = WindyForecastResponse(**data)

        params = response.available_parameters()
        assert "waves" in params
        assert "windWaves" in params

    def test_available_parameters_atmospheric(self):
        """Test available parameters includes atmospheric composition."""
        data = {
            "ts": [1700000000000],
            "units": {
                "so2sm-surface": "kg*m-2",
                "dustsm-surface": "kg*m-2",
                "cosc-surface": "kg*m-3",
            },
            "so2sm-surface": [0.0001],
            "dustsm-surface": [0.0002],
            "cosc-surface": [0.00001],
        }
        response = WindyForecastResponse(**data)

        params = response.available_parameters()
        assert "so2sm" in params
        assert "dustsm" in params
        assert "cosc" in params
