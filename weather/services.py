from datetime import datetime, timedelta
from io import StringIO
from typing import Dict, List

import httpx
import pandas as pd
from django.core.cache import cache
from rest_framework import status

from weather.exceptions import RemoteCallException

DISTRICT_CALL_URL = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
TWO_HOUR_CACHE_TIME = 60 * 60 * 2


class DistrictService:
    def __init__(self, url: str = DISTRICT_CALL_URL) -> None:
        """
        Initializes the Districts instance with the URL to fetch district data.

        Parameters:
        url (str): The URL to fetch district data. Defaults to DISTRICT_CALL_URL.
        """
        if url is None:
            raise ValueError("URL is required to fetch districts")
        self.url = url

    async def get(self) -> List[Dict[str, str]]:
        """
        Fetches the list of districts from the API or cache.

        Returns:
        List[Dict[str, str]]: A list of dictionaries containing district data.

        Raises:
        RemoteCallException: If the API call fails to fetch the district data.
        """
        # Check if the district data is available in the cache
        cached_districts = cache.get("districts_data")
        if cached_districts is not None:
            return cached_districts

        # If not cached, fetch the data from the remote API
        async with httpx.AsyncClient() as session:
            response = await session.get(self.url)

            if response.status_code != status.HTTP_200_OK:
                raise RemoteCallException("Couldn't Fetch Data for Districts API")
            # Parse the response JSON to extract district data
            districts_data = response.json().get("districts", [])

        # Cache the fetched district data for 2 hours
        cache.set("districts_data", districts_data, timeout=TWO_HOUR_CACHE_TIME)

        return districts_data


class WeatherForecast:
    def __init__(self, district):
        """
        Initializes the WeatherForecast instance with district data and constructs the API URL.

        Parameters:
        district (dict): A dictionary containing district information including latitude and longitude.
        """
        self.district = district
        # Calculate the start and end dates for the weather forecast (7-day period)
        start_day = datetime.today()
        end_day = start_day + timedelta(days=7)
        start_day_str = start_day.strftime("%Y-%m-%d")
        end_day_str = end_day.strftime("%Y-%m-%d")

        # Construct the API URL with the required parameters for the specified date range and location
        self.api_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.district['lat']}"
            f"&longitude={self.district['long']}&start_date={start_day_str}"
            f"&end_date={end_day_str}&hourly=temperature_2m&timezone=Asia/Dhaka&format=csv"
        )

    async def _download_csv_data(self, session):
        """
        Downloads the weather forecast data in CSV format asynchronously.

        Parameters:
        session (httpx.AsyncClient): The HTTP client session used for making requests.

        Returns:
        str: The CSV data as a string.
        """
        response = await session.get(self.api_url)
        response.raise_for_status()
        return response.text

    def _get_2pm_rows(self, csv_data):
        """
        Filters the CSV data to extract rows corresponding to 2 PM.

        Parameters:
        csv_data (str): The CSV data as a string.

        Returns:
        pandas.DataFrame: A DataFrame containing only the rows for 2 PM.
        """
        two_pm_digit = 14
        df = pd.read_csv(StringIO(csv_data), skiprows=3)
        df["time"] = pd.to_datetime(df["time"])
        return df[df["time"].dt.hour == two_pm_digit]

    def _get_avg_forcast(self, _data):
        """
        Calculates the average temperature at 2 PM over the next 7 days.

        Parameters:
        _data (pandas.DataFrame): DataFrame containing 2 PM temperature data.

        Returns:
        float: The average temperature rounded to two decimal places.
        """
        average_temp = _data["temperature_2m (°C)"][:7].mean()
        return float(round(average_temp, 2))

    async def fetch_and_process(self, session):
        """
        Fetches the weather data, processes it to calculate the average temperature, and returns the result.

        Parameters:
        session (httpx.AsyncClient): The HTTP client session used for making requests.

        Returns:
        dict: A dictionary containing the district name and the average temperature at 2 PM.
        """
        csv_data = await self._download_csv_data(session)
        _data = self._get_2pm_rows(csv_data)
        avg_temp = self._get_avg_forcast(_data)
        return {
            "district": self.district["name"],
            "average_temperature": avg_temp,
        }
