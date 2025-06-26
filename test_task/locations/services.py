import asyncio
import json
from datetime import timedelta

import aiohttp
from asgiref.sync import sync_to_async
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils import timezone

from test_task.core.cloudflare_r2_client import s3_client


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


async def get_weather_from_redis(redis_client, redis_key):
    cached = await redis_client.get(redis_key)
    if cached:
        return json.loads(cached)
    return None


async def get_weather_from_s3(s3_key):
    try:
        obj = await sync_to_async(s3_client.get_object)(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key
        )
        body = await sync_to_async(obj["Body"].read)()
        metadata = obj["LastModified"]
        if metadata > timezone.now() - timedelta(minutes=5):
            return json.loads(body)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise
    return None


async def save_weather_in_s3(filename, weather_data):
    await sync_to_async(s3_client.put_object)(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=filename,
        Body=json.dumps(weather_data),
        ContentType="application/json",
    )


async def set_weather_in_redis(redis_client, redis_key, weather):
    await redis_client.setex(redis_key, settings.CACHE_TTL, json.dumps(weather))


async def cache_weather(redis_client, redis_key, s3_filename, weather):
    await asyncio.gather(
        save_weather_in_s3(s3_filename, weather),
        set_weather_in_redis(redis_client, redis_key, weather),
    )
