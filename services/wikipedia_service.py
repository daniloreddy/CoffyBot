import requests

from utils.localization import t


# --- Wikipedia ---
def search_wikipedia(term):
    try:
        url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{term.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown")
            extract = data.get("extract", "No description found.")
            link = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            image = data.get("thumbnail", {}).get("source")
            return title, extract, link, image
        else:
            return None, t("wiki_no_entry"), "", None
    except Exception as e:
        return None, t("wiki_error", error=e), "", None
