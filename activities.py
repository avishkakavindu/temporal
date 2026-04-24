from temporalio import activity


@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello {name}, welcome to Temporal!"


@activity.defn
async def fetch_cat_images(limit: int) -> list:
    import httpx

    url = f"https://api.thecatapi.com/v1/images/search?limit={limit}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # Check for errors
        data = response.json()

        # Return just a list of URLs for simplicity
        return [item["url"] for item in data]
