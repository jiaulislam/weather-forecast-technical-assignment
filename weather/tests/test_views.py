# tests/test_views.py
import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from django.http import JsonResponse
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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
    mock_district_service.return_value.aget.return_value = asyncio.Future()
    mock_district_service.return_value.aget.return_value.set_result(mock_districts)

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


districts_data = [
    {"id": "1", "name": "Dhaka", "lat": "23.8103", "long": "90.4125"},
    {"id": "2", "name": "Chittagong", "lat": "22.3569", "long": "91.7832"},
]

weather_response = {
    "hourly": {
        "temperature_2m": [
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
        ]
    }
}


@patch("weather.views.httpx.Client.get")
@patch("weather.views.DistrictService.get")
def test_travel_decision(mock_districts_get, mock_httpx_get):
    mock_districts_get.return_value = districts_data
    mock_httpx_get.return_value.json.return_value = weather_response
    mock_httpx_get.return_value.status_code = status.HTTP_200_OK
    url = reverse("travel-decision")  # Replace with your actual URL name

    client = APIClient()
    url = reverse("travel-decision")

    data = {
        "current_district_id": 1,
        "dest_district_id": 2,
        "travel_date": "2024-07-10",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "decision" in response.data
    assert response.data["decision"] in ["Can Visit", "Shouldn't visit"]
    assert response.data["travel_date"] == "2024-07-10"
