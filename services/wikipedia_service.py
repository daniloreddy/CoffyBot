import aiohttp
from utils.localization import t


async def search_wikipedia(term):
    """
    Search for a summary of a term on Italian Wikipedia.

    Args:
        term (str): The search term.

    Returns:
        tuple: (title, extract, link, image_url) if found,
               or (None, error_message, "", None) on failure.
    """

    url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{term.replace(' ', '_')}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    title = data.get("title", "Unknown")
                    extract = data.get("extract", "No description found.")
                    link = (
                        data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    )
                    image = data.get("thumbnail", {}).get("source")
                    return title, extract, link, image
                else:
                    return None, t("wiki_no_entry"), "", None
    except Exception as e:
        return None, t("wiki_error", error=e), "", None
