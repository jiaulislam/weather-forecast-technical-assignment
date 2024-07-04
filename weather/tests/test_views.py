# tests/test_views.py
import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from django.http import JsonResponse
from django.test import RequestFactory

from weather.views import TopDistrictListView

mock_districts = [
    {"name": f"District {i}", "lat": 23.0 + i, "long": 90.0 + i} for i in range(12)
]

mock_weather_data = [
    {"district": f"District {i}", "average_temperature": 25.0 + i} for i in range(12)
]


@pytest.mark.asyncio
@patch("weather.views.DistrictService")
@patch("weather.views.WeatherForecast")
async def test_top_district_list_view(mock_weather_forecast, mock_district_service):
    mock_district_service.return_value.get.return_value = asyncio.Future()
    mock_district_service.return_value.get.return_value.set_result(mock_districts)

    mock_weather_forecast.side_effect = [
        AsyncMock(fetch_and_process=AsyncMock(return_value=data))
        for data in mock_weather_data
    ]

    factory = RequestFactory()
    request = factory.get("/api/top-districts/")
    view = TopDistrictListView.as_view()

    response = await view(request)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    response_data = json.loads(response.content)

    assert len(response_data) == 10
