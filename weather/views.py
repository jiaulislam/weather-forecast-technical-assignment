import asyncio
from enum import StrEnum

import httpx
from django.http import HttpRequest, JsonResponse
from django.views import View

from .services import DistrictService, WeatherForecast


class TemperatureDataModeEnum(StrEnum):
    CSV = "csv"
    JSON = "json"


class TopDistrictListView(View):
    """Top 10 Cool Districts List View API"""

    authentication_classes = []
    permission_classes = []
    pagination_class = []

    async def get(self, request: HttpRequest) -> JsonResponse:
        """
        Handles GET requests to fetch and return the 10 coolest districts based on average temperature.

        Parameters:
        request (HttpRequest): The HTTP request object.

        Returns:
        JsonResponse: JSON response containing data of the 10 coolest districts.
        """
        ds = DistrictService()

        districts = await ds.get()

        # Initialize an async HTTP client session
        async with httpx.AsyncClient() as session:
            results = []
            chunk_size = 4

            # Process districts in chunks to avoid overwhelming the system with concurrent requests
            for i in range(0, len(districts), chunk_size):
                chunk = districts[i : i + chunk_size]
                tasks = [
                    WeatherForecast(district).fetch_and_process(session)
                    for district in chunk
                ]

                # Gather and await results for each chunk of districts
                chunk_results = await asyncio.gather(*tasks)
                results.extend(chunk_results)

            results.sort(key=lambda x: x["average_temperature"])

            # Return JSON response with data of the 10 coolest districts
            return JsonResponse(results[:10], safe=False)
