import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1381377183016030238/uGrQBLCiK_AouYVJ_gMMUzq69KNFglXy4e4aNJ6PVWWKSaoNvtDxeMtyQydR5nQjSoxc"

def get_today_events():
    url = "https://www.investing.com/economic-calendar/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    today = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%A, %d. %B %Y")
    msg = [f"📊 **Wirtschaftskalender für {today}**\n"]

    for row in soup.select("tr.js-event-item"):
        impact = row.get("data-impact")
        if impact not in ("2", "3"):
            continue  # nur 2- und 3-Sterne

        try:
            title = row.get("data-event-title")
            country = row.get("data-country")
            currency = row.get("data-event-currency")
            time = row.get("data-event-datetime")
            actual = row.select_one(".actualColumn").get_text(strip=True)
            forecast = row.select_one(".forecastColumn").get_text(strip=True)
            previous = row.select_one(".previousColumn").get_text(strip=True)

            event_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            time_str = event_time.strftime("%H:%M")

            flag = {
                "Germany": "🇩🇪", "United States": "🇺🇸", "Euro Zone": "🇪🇺",
                "United Kingdom": "🇬🇧", "Japan": "🇯🇵", "China": "🇨🇳",
                "Canada": "🇨🇦", "Switzerland": "🇨🇭", "Australia": "🇦🇺"
            }.get(country, "🌍")

            msg.append(
                f"**{time_str} {flag} {currency} – {title}**\n"
                f"📈 Erwartet: {forecast or '–'} | Vorher: {previous or '–'} | Aktuell: {actual or '–'}\n"
            )
        except Exception as e:
            continue

    if len(msg) == 1:
        msg.append("✅ Heute stehen keine relevanten Termine an.")

    msg.append("🔗 Quelle: https://de.investing.com/economic-calendar/")
    return "\n".join(msg)

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

send_to_discord(get_today_events())
