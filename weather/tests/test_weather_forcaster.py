from datetime import datetime

import httpx
import pandas as pd
import pytest
import responses

from weather.services import (
    WeatherForecast,
)

# Mock district data
mock_district = {"name": "Mock District", "lat": 23.8103, "long": 90.4125}


# Helper function to generate mock CSV data
def generate_mock_csv():
    dates = pd.date_range(start=datetime.today(), periods=7, freq="D")
    times = [f"{date.strftime('%Y-%m-%d')} 14:00:00" for date in dates]
    temperatures = [30, 32, 31, 33, 34, 35, 36]
    data = {"time": times, "temperature_2m (°C)": temperatures}
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    return csv_data


@pytest.fixture
def mock_weather_forecast():
    return WeatherForecast(district=mock_district)


@pytest.mark.asyncio
@responses.activate
async def test_fetch_and_process(mock_weather_forecast):
    mock_csv = generate_mock_csv()
    responses.add(
        responses.GET, mock_weather_forecast.api_url, body=mock_csv, status=200
    )

    async with httpx.AsyncClient() as client:
        result = await mock_weather_forecast.fetch_and_process(client)

    assert result["district"] == "Mock District"
