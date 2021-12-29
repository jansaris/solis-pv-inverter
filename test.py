import solis
import asyncio
import json

#x = solis.Solis("http://Zonnepanelen.local/", "user", "password")
x = solis.Solis("http://localhost:8000/", "user", "password")

loop = asyncio.get_event_loop()
result = loop.run_until_complete(x.retrieve())
print(json.dumps(result.__dict__))