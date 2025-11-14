"""Tests for WindyForecastResponse model."""

from datetime import datetime, timezone

from windy_api.schema.schema import WindyForecastResponse


class TestTimestampConversion:
    """Test timestamp conversion from milliseconds to datetime."""

    def test_timestamp_conversion(self, mock_api_response_data):
        """Test that millisecond timestamps are converted to datetime objects."""
        response = WindyForecastResponse(**mock_api_response_data)

        assert len(response.ts) == 3
        assert all(isinstance(ts, datetime) for ts in response.ts)

        # Check that timestamps are in UTC
        for ts in response.ts:
            assert ts.tzinfo == timezone.utc

    def test_timestamp_precision(self):
        """Test timestamp conversion accuracy."""
        data = {
            "ts": [1700000000000],  # Nov 14, 2023 22:13:20 UTC
            "units": {},
        }
        response = WindyForecastResponse(**data)

        expected = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
        assert response.ts[0] == expected

    def test_multiple_timestamps(self, mock_api_response_data):
        """Test conversion of multiple timestamps."""
        response = WindyForecastResponse(**mock_api_response_data)

        # Verify timestamps are in order
        for i in range(len(response.ts) - 1):
            assert response.ts[i] < response.ts[i + 1]

    def test_empty_timestamps(self):
        """Test handling of empty timestamp list."""
        data = {
            "ts": [],
            "units": {},
        }
        response = WindyForecastResponse(**data)
        assert response.ts == []


class TestDynamicFields:
    """Test dynamic parameter-level field storage."""

    def test_dynamic_field_storage(self, mock_api_response_data):
        """Test that dynamic fields are stored correctly."""
        response = WindyForecastResponse(**mock_api_response_data)

        # Check that dynamic fields exist
        assert hasattr(response, "temp-surface")
        assert hasattr(response, "wind_u-surface")
        assert hasattr(response, "wind_v-surface")

    def test_dynamic_field_values(self, mock_api_response_data):
        """Test that dynamic field values match input."""
        response = WindyForecastResponse(**mock_api_response_data)

        assert response.model_extra["temp-surface"] == [15.2, 14.8, 14.3]
        assert response.model_extra["wind_u-surface"] == [3.5, 4.2, 4.8]
        assert response.model_extra["wind_v-surface"] == [2.1, 2.3, 2.6]

    def test_multiple_levels(self, mock_api_response_multiple_levels):
        """Test storage of data at multiple pressure levels."""
        response = WindyForecastResponse(**mock_api_response_multiple_levels)

        assert "temp-surface" in response.model_extra
        assert "temp-850h" in response.model_extra
        assert "wind_u-surface" in response.model_extra
        assert "wind_u-850h" in response.model_extra


class TestGetDataMethod:
    """Test the get_data() method."""

    def test_get_data_valid_parameter(self, mock_api_response_data):
        """Test retrieving data for a valid parameter-level."""
        response = WindyForecastResponse(**mock_api_response_data)

        temp_data = response.get_data("temp-surface")
        assert temp_data == [15.2, 14.8, 14.3]

    def test_get_data_all_parameters(self, mock_api_response_data):
        """Test retrieving data for all parameters."""
        response = WindyForecastResponse(**mock_api_response_data)

        assert response.get_data("temp-surface") == [15.2, 14.8, 14.3]
        assert response.get_data("wind_u-surface") == [3.5, 4.2, 4.8]
        assert response.get_data("wind_v-surface") == [2.1, 2.3, 2.6]

    def test_get_data_invalid_parameter(self, mock_api_response_data):
        """Test retrieving data for a non-existent parameter returns None."""
        response = WindyForecastResponse(**mock_api_response_data)

        result = response.get_data("nonexistent-parameter")
        assert result is None

    def test_get_data_different_levels(self, mock_api_response_multiple_levels):
        """Test retrieving data for different pressure levels."""
        response = WindyForecastResponse(**mock_api_response_multiple_levels)

        surface_temp = response.get_data("temp-surface")
        h850_temp = response.get_data("temp-850h")

        assert surface_temp == [15.2, 14.8]
        assert h850_temp == [5.3, 5.1]
        assert surface_temp != h850_temp


class TestGetUnitMethod:
    """Test the get_unit() method."""

    def test_get_unit_valid_parameter(self, mock_api_response_data):
        """Test retrieving unit for a valid parameter-level."""
        response = WindyForecastResponse(**mock_api_response_data)

        temp_unit = response.get_unit("temp-surface")
        assert temp_unit == "°C"

    def test_get_unit_all_parameters(self, mock_api_response_data):
        """Test retrieving units for all parameters."""
        response = WindyForecastResponse(**mock_api_response_data)

        assert response.get_unit("temp-surface") == "°C"
        assert response.get_unit("wind_u-surface") == "m/s"
        assert response.get_unit("wind_v-surface") == "m/s"

    def test_get_unit_invalid_parameter(self, mock_api_response_data):
        """Test retrieving unit for a non-existent parameter returns None."""
        response = WindyForecastResponse(**mock_api_response_data)

        result = response.get_unit("nonexistent-parameter")
        assert result is None

    def test_get_unit_different_levels(self, mock_api_response_multiple_levels):
        """Test retrieving units for different pressure levels."""
        response = WindyForecastResponse(**mock_api_response_multiple_levels)

        assert response.get_unit("temp-surface") == "°C"
        assert response.get_unit("temp-850h") == "°C"
        assert response.get_unit("wind_u-surface") == "m/s"

    def test_missing_units_field(self):
        """Test handling when units field is missing for a parameter."""
        data = {
            "ts": [1700000000000],
            "units": {},
            "temp-surface": [15.2],
        }
        response = WindyForecastResponse(**data)

        # Data should still be accessible
        assert response.get_data("temp-surface") == [15.2]
        # But unit should return None
        assert response.get_unit("temp-surface") is None


class TestUnitsField:
    """Test the units field."""

    def test_units_dict_structure(self, mock_api_response_data):
        """Test that units field is a dictionary."""
        response = WindyForecastResponse(**mock_api_response_data)

        assert isinstance(response.units, dict)
        assert len(response.units) == 3

    def test_units_keys_match_data(self, mock_api_response_data):
        """Test that units keys match parameter-level fields."""
        response = WindyForecastResponse(**mock_api_response_data)

        for key in response.units:
            assert key in response.model_extra

    def test_empty_units(self):
        """Test handling of empty units dictionary."""
        data = {
            "ts": [1700000000000],
            "units": {},
        }
        response = WindyForecastResponse(**data)
        assert response.units == {}


class TestResponseIntegration:
    """Integration tests for complete response handling."""

    def test_complete_response_workflow(self, mock_api_response_data):
        """Test complete workflow of parsing and accessing response data."""
        response = WindyForecastResponse(**mock_api_response_data)

        # Check timestamps
        assert len(response.ts) == 3
        assert isinstance(response.ts[0], datetime)

        # Check data retrieval
        temp_data = response.get_data("temp-surface")
        assert len(temp_data) == 3
        assert temp_data[0] == 15.2

        # Check units
        temp_unit = response.get_unit("temp-surface")
        assert temp_unit == "°C"

        # Verify data and timestamps align
        assert len(response.ts) == len(temp_data)

    def test_response_with_all_fields(self, mock_api_response_multiple_levels):
        """Test response with multiple parameters and levels."""
        response = WindyForecastResponse(**mock_api_response_multiple_levels)

        # Verify all data is accessible
        assert response.get_data("temp-surface") is not None
        assert response.get_data("temp-850h") is not None
        assert response.get_data("wind_u-surface") is not None
        assert response.get_data("wind_u-850h") is not None

        # Verify all units are accessible
        assert response.get_unit("temp-surface") is not None
        assert response.get_unit("temp-850h") is not None

    def test_minimal_valid_response(self):
        """Test minimal valid response with only required fields."""
        data = {
            "ts": [1700000000000],
            "units": {},
        }
        response = WindyForecastResponse(**data)

        assert len(response.ts) == 1
        assert isinstance(response.ts[0], datetime)
        assert response.units == {}
