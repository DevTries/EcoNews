import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import csv
import os

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1381377183016030238/uGrQBLCiK_AouYVJ_gMMUzq69KNFglXy4e4aNJ6PVWWKSaoNvtDxeMtyQydR5nQjSoxc"

def fetch_events():
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.find_all("tr", class_="calendar__row")

    events = []
    for row in rows:
        impact_cell = row.select_one(".impact span")
        if not impact_cell:
            continue

        impact_classes = impact_cell.get("class", [])
        if "medium" not in impact_classes and "high" not in impact_classes:
            continue

        time_cell = row.select_one(".time")
        event_cell = row.select_one(".event")
        currency_cell = row.select_one(".currency")

        if not (time_cell and event_cell and currency_cell):
            continue

        event_time = time_cell.get_text(strip=True)
        event_name = event_cell.get_text(strip=True)
        currency = currency_cell.get_text(strip=True)

        events.append({
            "time": event_time,
            "event": event_name,
            "currency": currency,
            "impact": "high" if "high" in impact_classes else "medium"
        })

    return events

def save_to_csv(events, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "event", "currency", "impact"])
        writer.writeheader()
        for e in events:
            writer.writerow(e)

def format_message(events):
    tz = pytz.timezone("Europe/Berlin")
    today_str = datetime.now(tz).strftime("%A, %d. %B %Y")
    if not events:
        return f"📅 **Wirtschaftstermine für {today_str}**\n\n✅ Keine relevanten Termine für heute.\n🔗 https://www.forexfactory.com/calendar"

    flag_map = {
        "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
        "AUD": "🇦🇺", "CAD": "🇨🇦", "CHF": "🇨🇭", "NZD": "🇳🇿",
        "CNY": "🇨🇳", "DE": "🇩🇪"
    }

    stars_map = {"high": "⭐⭐⭐", "medium": "⭐⭐"}

    lines = [f"📅 **Wirtschaftstermine für {today_str}**\n"]
    for e in events:
        flag = flag_map.get(e["currency"], "🌍")
        stars = stars_map.get(e["impact"], "")
        lines.append(f"– {flag} {e['event']} ({e['currency']}) – {e['time']} Uhr {stars}")

    lines.append("\n🔗 https://www.forexfactory.com/calendar")
    return "\n".join(lines)

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def main():
    events = fetch_events()
    csv_path = "data/economic_calendar.csv"
    save_to_csv(events, csv_path)
    message = format_message(events)
    send_to_discord(message)

if __name__ == "__main__":
    main()
