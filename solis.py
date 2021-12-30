"""Solis PV Converter integration API."""
import logging

import aiohttp
import asyncio
import re

_LOGGER = logging.getLogger(__name__)


class Solis:
    """Solis PV Converter integration API."""

    POWER_REGEX = re.compile(r'var webdata_now_p = "([0-9]+(\.[0-9]+)?)"')
    TODAY_REGEX = re.compile(r'var webdata_today_e = "([0-9]+(\.[0-9]+)?)"')
    TOTAL_REGEX = re.compile(r'var webdata_total_e = "([0-9]+(\.[0-9]+)?)"')

    def __init__(self, url, username, password):
        self._url = f"{url}/status.html"
        self._username = username
        self._password = password

    async def retrieve(self):
        """Retrieves the model from the Solis PV internal website."""
        _LOGGER.debug("Retrieve data from %s", self._url)
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self._username, self._password)
        ) as session:
            try:
                async with session.get(
                    self._url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if not response.ok:
                        return SolisModel.http_error(
                            response.status,
                            f"http-{response.status}: {response.reason}",
                        )
                    html = await response.text()
                    return Solis._extract_model(html)
            except asyncio.TimeoutError:
                return SolisModel.unreachable()
            except aiohttp.ClientConnectionError:
                return SolisModel.connection_error()

    @staticmethod
    def _extract_model(html):
        """Extract the complete model from the HTML using regex"""
        power = Solis._extract_regex_value(Solis.POWER_REGEX, html)
        today = Solis._extract_regex_value(Solis.TODAY_REGEX, html)
        total = Solis._extract_regex_value(Solis.TOTAL_REGEX, html)
        return SolisModel.create(power, today, total)

    @staticmethod
    def _extract_regex_value(regex, html):
        """Extract the value from the HTML using regex"""
        match = regex.search(html)
        if match:
            return match.group(1)
        return 0


class SolisModel:
    """Solis PV Converter integration Model."""

    @classmethod
    def unreachable(cls):
        """Creates an error model for Host unreachable."""
        return cls("Host unreachable", 0, False, True, 0, 0, 0)

    @classmethod
    def create(cls, power, today, total):
        """Creates a valid model with given data."""
        return cls("OK", 200, True, False, power, today, total)

    @classmethod
    def connection_error(cls):
        """Creates an error model for a connection error."""
        return cls("Connection error", 0, False, True, 0, 0, 0)

    @classmethod
    def http_error(cls, http_code, reason):
        """Creates an error model with the http status code."""
        return cls(reason, http_code, True, True, 0, 0, 0)

    def __init__(self, status, http_code, reachable, error, power, today, total):
        self.reachable = reachable
        self.error = error
        self.current_power = power
        self.current_power_kw = float(power) / 1000
        self.yield_tody = today
        self.yield_total = total
        self.http_code = http_code
        self.status = status
