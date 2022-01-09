"""Solis PV Inverter integration API."""
import asyncio
import json
import logging
import re

import aiohttp

_LOGGER = logging.getLogger(__name__)


class Solis:
    """Solis PV Inverter integration API."""

    POWER_REGEX = re.compile(r'var webdata_now_p = "(\d+(\.\d+)*)"')
    TODAY_REGEX = re.compile(r'var webdata_today_e = "(\d+(\.\d+)*)"')
    TOTAL_REGEX = re.compile(r'var webdata_total_e = "(\d+(\.\d+)*)"')

    def __init__(self, url, username, password):
        """Initialize Solis PV Inverter integration."""
        self._url = f"{url}/status.html"
        self._username = username
        self._password = password
        _LOGGER.debug("Initialize an empty model")
        self._model = SolisModel.empty_model()

    async def retrieve(self):
        """Retrieve the model from the Solis PV Inverter internal website."""
        _LOGGER.debug("Retrieve data from %s", self._url)
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self._username, self._password)
        ) as session:
            try:
                async with session.get(
                    self._url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if not response.ok:
                        self._model = SolisModel.http_error(
                            response.status,
                            f"http-{response.status}: {response.reason}",
                        )
                    html = await response.text()
                    self._model = Solis._extract_model(html)
            except asyncio.TimeoutError:
                self._model = SolisModel.unreachable()
            except aiohttp.ClientConnectionError:
                self._model = SolisModel.connection_error()
        _LOGGER.debug(
            "Retrieved from %s: %s", self._url, json.dumps(self._model.__dict__)
        )
        return self._model

    def get_value(self, key):
        """Retrieve the requested value from the latest model or default to 0."""
        return getattr(self._model, key, 0)

    @staticmethod
    def _extract_model(html):
        """Extract the complete model from the HTML using regex."""
        power = Solis._extract_regex_value(Solis.POWER_REGEX, html)
        today = Solis._extract_regex_value(Solis.TODAY_REGEX, html)
        total = Solis._extract_regex_value(Solis.TOTAL_REGEX, html)
        return SolisModel.create(power, today, total)

    @staticmethod
    def _extract_regex_value(regex, html):
        """Extract the value from the HTML using regex."""
        match = regex.search(html)
        if match:
            return match.group(1)
        return 0


class SolisModel:
    """Solis PV Converter integration Model."""

    @classmethod
    def empty_model(cls):
        """Create an error model with the http status code."""
        return cls("Empty", 0, False, True, 0, 0, 0)

    @classmethod
    def unreachable(cls):
        """Create an error model for Host unreachable."""
        return cls("Host unreachable", 0, False, True, 0, 0, 0)

    @classmethod
    def create(cls, power, today, total):
        """Create a valid model with given data."""
        return cls("OK", 200, True, False, power, today, total)

    @classmethod
    def connection_error(cls):
        """Create an error model for a connection error."""
        return cls("Connection error", 0, False, True, 0, 0, 0)

    @classmethod
    def http_error(cls, http_code, reason):
        """Create an error model with the http status code."""
        return cls(reason, http_code, True, True, 0, 0, 0)

    def __init__(self, status, http_code, reachable, error, power, today, total):
        """Initialize Solis Model."""
        self.reachable = reachable
        self.error = error
        self.current_power = int(power)
        self.current_power_kw = float(power) / 1000
        self.yield_tody = float(today)
        self.yield_total = float(total)
        self.http_code = http_code
        self.status = status
        self.available = reachable and not error
