import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/DEIN-WEBHOOK-HIER"

def get_today_events():
    url = "https://www.investing.com/economic-calendar/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    today = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%A, %d. %B %Y")
    events = [f"📆 **Wirtschaftstermine für {today}**\n"]

    for row in soup.select("tr.js-event-item"):
        title = row.get("data-event-title")
        country = row.get("data-country")
        time = row.get("data-event-datetime")
        impact = row.get("data-impact")
        if impact in ("2", "3"):
            try:
                event_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                time_str = event_time.strftime("%H:%M")
                stars = "⭐⭐⭐" if impact == "3" else "⭐⭐"
                flag = {
                    "Germany": "🇩🇪", "United States": "🇺🇸", "Euro Zone": "🇪🇺",
                    "United Kingdom": "🇬🇧", "Japan": "🇯🇵", "China": "🇨🇳",
                    "Canada": "🇨🇦", "Switzerland": "🇨🇭"
                }.get(country, "🌍")
                events.append(f"– {flag} {title} – {time_str} Uhr {stars}")
            except:
                continue

    if len(events) == 1:
        events.append("✅ Heute stehen keine relevanten Termine an.")
    events.append("🔗 https://de.investing.com/economic-calendar/")
    return "\n".join(events)

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

send_to_discord(get_today_events())