import asyncio
from bisect import bisect_left
from enum import StrEnum

import httpx
from django.http import HttpRequest, JsonResponse
from django.views import View
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    TravelDecisionEnum,
    TravelDecisionInSerializer,
    TravelDecisionOutSerializer,
)
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

        districts = await ds.aget()

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


class TravelDecisionView(APIView):
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def _find_district_by_id(self, districts, target_id):
        keys = [int(district["id"]) for district in districts]
        target_id = int(target_id)
        idx = bisect_left(keys, target_id)
        if idx < len(keys) and int(keys[idx]) == target_id:
            return districts[idx]
        return None

    @extend_schema(
        parameters=[TravelDecisionInSerializer],
        responses={200: TravelDecisionOutSerializer},
    )
    def post(self, request: Request) -> Response:
        try:
            in_serialized = TravelDecisionInSerializer(data=request.data)

            in_serialized.is_valid(raise_exception=True)

            ds = DistrictService()
            districts = ds.get()

            current_loc_id = in_serialized.data.get("current_district_id")
            target_loc_id = in_serialized.data.get("dest_district_id")
            travel_date = in_serialized.data.get("travel_date")

            current = self._find_district_by_id(districts, current_loc_id)
            target = self._find_district_by_id(districts, target_loc_id)

            with httpx.Client() as session:
                current_loc_temp = WeatherForecast(
                    current, days=0, mode="json"
                ).fetch_temperature_for_day(travel_date, session)
                target_loc_temp = WeatherForecast(
                    target, days=0, mode="json"
                ).fetch_temperature_for_day(travel_date, session)

                if target_loc_temp > current_loc_temp:
                    decision = TravelDecisionEnum.NO
                else:
                    decision = TravelDecisionEnum.YES

                return Response({"travel_date": travel_date, "decision": decision})
        except Exception as exc:
            return Response({"error": str(exc)}, status=500)
