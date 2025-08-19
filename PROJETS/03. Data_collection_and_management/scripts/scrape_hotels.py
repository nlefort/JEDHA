import pandas as pd
import uuid
import urllib.parse
import asyncio
from playwright.async_api import async_playwright

# Charger ton fichier de géocodage
cities = pd.read_csv("data/geocode_villes.csv")

async def scrape_booking():
    all_hotels = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = await context.new_page()

        for _, row in cities.iterrows():
            city_id = row["id_ville"]
            city_name = row["ville"]
            lat = row["latitude"]
            lon = row["longitude"]

            print(f"\nScraping hôtels à {city_name}...")

            ville_encoded = urllib.parse.quote_plus(city_name)
            url = f"https://www.booking.com/searchresults.fr.html?ss={ville_encoded}"
            await page.goto(url)
            await page.wait_for_timeout(5000)

            hotels = await page.locator('[data-testid="property-card"]').all()

            for hotel in hotels[:3]:  # Limiter à 3 hôtels par ville
                try:
                    name = await hotel.locator('[data-testid="title"]').inner_text()
                except:
                    name = "N/A"
                try:
                    url = await hotel.locator("a").first.get_attribute("href")
                    if not url.startswith("http"):
                        url = "https://www.booking.com" + url
                except:
                    url = "N/A"
                try:
                    rating = await hotel.locator('[data-testid="review-score"]').inner_text()
                except:
                    rating = "N/A"

                all_hotels.append({
                    "id": str(uuid.uuid4()),  
                    "id_ville": city_id,
                    "ville": city_name,
                    "nom": name,
                    "url": url,
                    "note": rating,
                    "latitude": lat,
                    "longitude": lon
                })

        await browser.close()

    # Sauvegarde CSV
    df = pd.DataFrame(all_hotels)
    df.to_csv("data/hotels.csv", index=False)
    print("Fichier 'hotels.csv' exporté avec les hôtels.")

# Lancement
if __name__ == "__main__":
    asyncio.run(scrape_booking())
