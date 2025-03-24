import aiohttp
from utils.localization import translate
from utils.logger import service_logger, error_logger


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
                    service_logger.info("Wikipedia entry found: %s", title)
                    return title, extract, link, image
                else:
                    service_logger.warning("Wikipedia no entry for term: %s", term)
                    return None, translate("wiki_no_entry"), "", None
    except Exception as e:
        error_logger.error("Wikipedia search error: %s", str(e))
        return None, translate("wiki_error", error=e), "", None
