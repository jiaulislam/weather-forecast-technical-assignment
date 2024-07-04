# Create your tests here.
from unittest.mock import patch

import httpx
import pytest
from django.core.cache import cache
from rest_framework import status

from weather.exceptions import RemoteCallException
from weather.services import DistrictService

DISTRICT_CALL_URL = "http://example.com/api/districts"
TWO_HOUR_CACHE_TIME = 60 * 60 * 2


@pytest.fixture
def district_service():
    return DistrictService(DISTRICT_CALL_URL)


@pytest.mark.asyncio
async def test_get_districts_from_api(district_service):
    # Mock the response from the API
    mock_response_data = {
        "districts": [
            {"name": "District 1", "lat": "12.34", "long": "56.78"},
            {"name": "District 2", "lat": "23.45", "long": "67.89"},
        ]
    }

    async def mock_get(*args, **kwargs):
        return httpx.Response(status_code=200, json=mock_response_data)

    with patch("httpx.AsyncClient.get", new=mock_get):
        districts = await district_service.aget()
        assert len(districts) == 2
        assert districts[0]["name"] == "District 1"
        assert cache.get("districts_data") == mock_response_data["districts"]


@pytest.mark.asyncio
async def test_get_districts_from_cache(district_service):
    # Set the cache with mock data
    cached_data = [
        {"name": "Cached District 1", "lat": "12.34", "long": "56.78"},
        {"name": "Cached District 2", "lat": "23.45", "long": "67.89"},
    ]
    cache.set("districts_data", cached_data, timeout=TWO_HOUR_CACHE_TIME)

    districts = await district_service.aget()
    assert len(districts) == 2
    assert districts[0]["name"] == "Cached District 1"


@pytest.mark.asyncio
async def test_get_districts_api_failure(district_service):
    cache.clear()

    async def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, json={}
        )

    with patch("httpx.AsyncClient.get", new=mock_get):
        with pytest.raises(
            RemoteCallException, match="Couldn't Fetch Data for Districts API"
        ):
            await district_service.get()


def test_district_service_no_url():
    with pytest.raises(ValueError, match="URL is required to fetch districts"):
        DistrictService(None)
