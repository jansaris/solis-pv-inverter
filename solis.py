import aiohttp
import asyncio
import re

class Solis:
    POWER_REGEX = re.compile('var webdata_now_p = "([0-9]+(\.[0-9]+)?)"')
    TODAY_REGEX = re.compile('var webdata_today_e = "([0-9]+(\.[0-9]+)?)"')
    TOTAL_REGEX = re.compile('var webdata_total_e = "([0-9]+(\.[0-9]+)?)"')

    def __init__(self, url, username, password):
        self._url = f"{url}/status.html"
        self._username = username
        self._password = password
    
    async def retrieve(self):
        print("Retrieve data from {}".format(self._url))
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self._username, self._password)) as session:
            try:
                async with session.get(self._url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if not response.ok:
                        return SolisModel.httpError(f"http-{response.status}: {response.reason}")
                    html = await response.text()
                    return self.extractModel(html)
            except asyncio.TimeoutError as e:
                return SolisModel.unreachable()
            except aiohttp.ClientConnectionError as e:
                return SolisModel.connectionError()

    def extractModel(self, html):
        power = Solis._extractRegexValue(Solis.POWER_REGEX, html)
        today = Solis._extractRegexValue(Solis.TODAY_REGEX, html)
        total = Solis._extractRegexValue(Solis.TOTAL_REGEX, html)
        return SolisModel.create(power, today, total)

    @staticmethod
    def _extractRegexValue(regex, html):
        match = regex.search(html)
        if match:
            return match.group(1)
        return 0

class SolisModel:
    @classmethod
    def unreachable(cls):
        return cls("Host unreachable", False, True, 0, 0, 0)
    
    @classmethod
    def create(cls, power, today, total):
        return cls("OK", True, False, power, today, total)

    @classmethod
    def connectionError(cls):
        return cls("Connection error", False, True, 0, 0, 0)

    @classmethod
    def httpError(cls, statusCode):
        return cls(statusCode, True, True, 0, 0, 0)

    def __init__(self, status, reachable, error, power, today, total):
        self.reachable = reachable
        self.error = error
        self.current_power = power
        self.current_power_kw = float(power) / 1000
        self.yield_tody = today
        self.yield_total = total
        self.status = status
