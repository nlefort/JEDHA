import asyncio
import urllib.parse
import pandas as pd
import aiohttp
from playwright.async_api import async_playwright

villes = ["Paris", "Lyon", "Nice"]  # inclure les villes souhaitées


# Fonction de géocodage avec Nominatim (OpenStreetMap)
async def geocode_address(session, hotel):
    if hotel["adresse"] == "N/A":
        hotel["latitude"] = "N/A"
        hotel["longitude"] = "N/A"
        return

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": hotel["adresse"],
        "format": "json",
        "limit": 1
    }

    try:
        async with session.get(url, params=params, headers={"User-Agent": "HotelScraper/1.0"}) as resp:
            data = await resp.json()
            if data:
                hotel["latitude"] = data[0]["lat"]
                hotel["longitude"] = data[0]["lon"]
            else:
                hotel["latitude"] = "N/A"
                hotel["longitude"] = "N/A"
    except:
        hotel["latitude"] = "N/A"
        hotel["longitude"] = "N/A"


# Regroupe tous les appels de géocodage
async def geocode_all(hotels):
    async with aiohttp.ClientSession() as session:
        tasks = [geocode_address(session, h) for h in hotels]
        await asyncio.gather(*tasks)


# Scraping principal avec Playwright
async def scrape_booking():
    all_hotels = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = await context.new_page()

        for ville in villes:
            print(f"\n🔍 Scraping hôtels à {ville}...")
            ville_encoded = urllib.parse.quote_plus(ville)
            url = f"https://www.booking.com/searchresults.fr.html?ss={ville_encoded}"
            await page.goto(url)
            await page.wait_for_timeout(5000)

            hotels = await page.locator('[data-testid="property-card"]').all()
            for hotel in hotels[:5]:  # Limite à 5 hôtels par ville
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

                # Page de l’hôtel
                description = "N/A"
                address = "N/A"
                if url != "N/A":
                    hotel_page = await context.new_page()
                    await hotel_page.goto(url)
                    await hotel_page.wait_for_timeout(3000)

                    try:
                        description = await hotel_page.locator('[data-testid="property-description"]').inner_text()
                    except:
                        description = "N/A"

                    try:
                        address = await hotel_page.locator('[data-testid="address"]').inner_text()
                    except:
                        address = "N/A"

                    await hotel_page.close()

                all_hotels.append({
                    "ville": ville,
                    "nom": name,
                    "url": url,
                    "note": rating,
                    "adresse": address,
                    "description": description
                })

        await browser.close()

    # Géocodage des adresses (asynchrone)
    print("\n🌍 Géocodage des adresses...")
    await geocode_all(all_hotels)

    # Sauvegarde
    df = pd.DataFrame(all_hotels)
# Enregistrement des données dans un fichier CSV
    chemin_fichier = "D:/Profils/NLefort/Desktop/JEDHA/PROJETS/03. Data_collection_and_management"
    df.to_csv(chemin_fichier + "/all_hotels.csv", index=False)  # Enregistrer le DataFrame dans un fichier CSV
    print("Fichier 'all_hotels.csv' exporté avec les coordonnées et la météo.")


# Lancement
if __name__ == "__main__":
    asyncio.run(scrape_booking())

