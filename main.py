from src.tools.tools import web_search, scrape_url

r = web_search.invoke("Who is the president of italy?")
s = scrape_url.invoke("https://www.facebook.com/ItalyInUs.org/videos/italian-prime-minister-giorgia-meloni-at-the-white-house/529456946884592")
print(s)