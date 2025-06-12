
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1381377183016030238/uGrQBLCiK_AouYVJ_gMMUzq69KNFglXy4e4aNJ6PVWWKSaoNvtDxeMtyQydR5nQjSoxc"

def get_events():
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    tz = pytz.timezone("Europe/Berlin")
    now = datetime.now(tz)
    today_str = now.strftime("%A, %d. %B %Y")
    message = [f"📅 **Wirtschaftstermine für {today_str}**\n"]

    rows = soup.find_all("tr", class_="calendar__row")
    for row in rows:
        impact_cell = row.select_one(".impact span")
        if not impact_cell:
            continue

        impact_class = impact_cell.get("class", [])
        #if "medium" not in impact_class and "high" not in impact_class:
           # continue

        time_cell = row.select_one(".time")
        event_cell = row.select_one(".event")
        currency_cell = row.select_one(".currency")

        if not (time_cell and event_cell and currency_cell):
            continue

        time_text = time_cell.get_text(strip=True)
        event = event_cell.get_text(strip=True)
        currency = currency_cell.get_text(strip=True)
        flag = {
            "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
            "AUD": "🇦🇺", "CAD": "🇨🇦", "CHF": "🇨🇭", "NZD": "🇳🇿",
            "CNY": "🇨🇳", "DE": "🇩🇪"
        }.get(currency, "🌍")

        stars = "⭐⭐⭐" if "high" in impact_class else "⭐⭐"
        message.append(f"– {flag} {event} ({currency}) – {time_text} Uhr {stars}")

    if len(message) == 1:
        message.append("✅ Keine relevanten Termine für heute.")
    message.append("🔗 https://www.forexfactory.com/calendar")
    return "\n".join(message)

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

send_to_discord(get_events())
