import aiohttp
from django.conf import settings


async def fetch_weather(latitude, longitude):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "temperature": data.get("main", {}).get("temp"),
                    "feels_like": data.get("main", {}).get("feels_like"),
                    "description": data.get("weather", [{}])[0].get("description"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                }
            return {"error": f"Weather API error: {response.status}"}
