import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import csv
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1381377183016030238/uGrQBLCiK_AouYVJ_gMMUzq69KNFglXy4e4aNJ6PVWWKSaoNvtDxeMtyQydR5nQjSoxc"
CSV_FILENAME = f"news_{datetime.now().strftime('%Y-%m-%d')}.csv"

def get_forex_factory_data():
    tz = pytz.timezone("Europe/Berlin")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    url = f"https://www.forexfactory.com/calendar?day={today}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr", class_="calendar__row")
    data = []

    for row in rows:
        time = row.select_one(".time")
        currency = row.select_one(".currency")
        event = row.select_one(".event")
        impact = row.select_one(".impact span")

        if not (time and currency and event and impact):
            continue

        impact_class = impact.get("class", [])
        if not any(x in impact_class for x in ("high", "medium")):
            continue

        impact_level = "High" if "high" in impact_class else "Medium"
        data.append({
            "Time": time.text.strip(),
            "Currency": currency.text.strip(),
            "Event": event.text.strip(),
            "Impact": impact_level
        })

    return data

def save_to_csv(data):
    with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Time", "Currency", "Event", "Impact"])
        writer.writeheader()
        writer.writerows(data)

def format_for_discord(data):
    if not data:
        return f"📅 **Wirtschaftstermine für heute**\n✅ Keine relevanten Termine.\n🔗 https://www.forexfactory.com/calendar"

    flag_map = {
        "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
        "AUD": "🇦🇺", "CAD": "🇨🇦", "CHF": "🇨🇭", "NZD": "🇳🇿",
        "CNY": "🇨🇳", "DE": "🇩🇪"
    }

    msg = [f"📅 **Wirtschaftstermine für {datetime.now().strftime('%A, %d. %B %Y')}**\n"]
    for entry in data:
        flag = flag_map.get(entry["Currency"], "🌍")
        stars = "⭐⭐⭐" if entry["Impact"] == "High" else "⭐⭐"
        msg.append(f"– {flag} {entry['Event']} – {entry['Time']} Uhr {stars}")
    msg.append("🔗 https://www.forexfactory.com/calendar")
    return "\n".join(msg)

def send_to_discord(message):
    requests.post(WEBHOOK_URL, json={"content": message})

if __name__ == "__main__":
    events = get_forex_factory_data()
    save_to_csv(events)
    discord_message = format_for_discord(events)
    send_to_discord(discord_message)
