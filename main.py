import os
print("Running from:", os.getcwd())

import requests
from datetime import datetime, timedelta
import pytz
import tkinter as tk
from tkinter import ttk
import csv
import json
from playsound import playsound
from dasha_engine import get_current_dasha

# --- Configuration ---
LAT = -36.8485
LNG = 174.7633
TIMEZONE = 'Pacific/Auckland'
DATE_FORMAT = '%Y-%m-%d %I:%M %p'

# --- Load Sound Alerts ---
with open('alerts.json') as f:
    ALERTS = json.load(f)

# --- Dasha Overlay ---
dasha_stack = get_current_dasha()  # Example: ['Venus', 'Sun', 'Saturn']
dasha_text = f"🔭 Dasha: {dasha_stack[0]} → {dasha_stack[1]} → {dasha_stack[2]}"
# --- Panchanga Stub (placeholder; replace with real API or logic later) ---
def get_daily_panchanga():
    return {
        "tithi": "Krishna Ashtami",
        "nakshatra": "Uttara Bhadrapada",
        "masam": "Ashadha",
        "ruthu": "Varsha",
        "ayana": "Dakshinayana",
        "chandramana_masam": "Ashadha"
    }

# --- Fetch Sunrise/Sunset/Solar Noon ---
def get_sun_data():
    url = f"https://api.sunrise-sunset.org/json?lat={LAT}&lng={LNG}&formatted=0"
    response = requests.get(url)
    data = response.json()['results']
    local_tz = pytz.timezone(TIMEZONE)
    sunrise = datetime.fromisoformat(data['sunrise']).astimezone(local_tz)
    sunset = datetime.fromisoformat(data['sunset']).astimezone(local_tz)
    solar_noon = datetime.fromisoformat(data['solar_noon']).astimezone(local_tz)
    return sunrise, sunset, solar_noon

# --- Inauspicious Muhurtas: Rahu, Yama, Gulika ---
def get_inauspicious_muhurthas(sunrise):
    weekday = sunrise.weekday()  # Monday = 0
    rahu_segments = [7, 1, 6, 4, 5, 3, 2]
    yama_segments = [5, 3, 2, 1, 0, 6, 4]
    gulika_segments = [6, 5, 4, 3, 2, 1, 0]
    segment = timedelta(minutes=90)

    rahu = sunrise + segment * rahu_segments[weekday]
    yama = sunrise + segment * yama_segments[weekday]
    gulika = sunrise + segment * gulika_segments[weekday]

    return [
        {"Type": "Inauspicious", "Name": "Rahu Kalam", "Start": rahu, "End": rahu + segment, "Purpose/Notes": "Avoid major undertakings"},
        {"Type": "Inauspicious", "Name": "Yama Ghantaka", "Start": yama, "End": yama + segment, "Purpose/Notes": "Accident-prone, avoid risky activities"},
        {"Type": "Inauspicious", "Name": "Gulika Kalam", "Start": gulika, "End": gulika + segment, "Purpose/Notes": "Causes looping karma"}
    ]
# --- Vedic Muhurtas ---
def get_vedic_muhurtas(sunrise):
    names = [
        "Rudra", "Āhi", "Mitra", "Pitṛ", "Vasu", "Varāha", "Viśvedevā", "Vidhi", "Sutamukhī", "Puruhūta",
        "Vāhinī", "Naktanakarā", "Varuṇa", "Aryaman", "Bhaga", "Girīśa", "Ajapāda", "Ahirbudhnya", "Puṣya", "Aśvinī",
        "Yama", "Agni", "Vidhātṛ", "Kaṇḍa", "Aditi", "Jaya", "Indra", "Sūrya", "Bhaga (2)", "Brahma"
    ]
    return [{
        'Type': 'Vedic',
        'Name': names[i],
        'Start': sunrise + timedelta(minutes=48 * i),
        'End': sunrise + timedelta(minutes=48 * (i + 1)),
        'Purpose/Notes': ''
    } for i in range(30)]

# --- Spiritual Muhurtas ---
def get_spiritual_muhurthas(sunrise, sunset, solar_noon):
    return [
        {'Type': 'Spiritual', 'Name': 'Arunodaya', 'Start': sunrise - timedelta(hours=2), 'End': sunrise - timedelta(hours=1, minutes=36), 'Purpose/Notes': 'Awakening subtle light'},
        {'Type': 'Spiritual', 'Name': 'Brahma Muhurta', 'Start': sunrise - timedelta(hours=1, minutes=36), 'End': sunrise - timedelta(minutes=48), 'Purpose/Notes': 'Ideal for Japa, Meditation'},
        {'Type': 'Spiritual', 'Name': 'Parata Sandhya', 'Start': sunrise - timedelta(minutes=30), 'End': sunrise - timedelta(minutes=10), 'Purpose/Notes': 'Pre-dawn reflection'},
        {'Type': 'Spiritual', 'Name': 'Sandhya Kala (Morning)', 'Start': sunrise - timedelta(minutes=20), 'End': sunrise + timedelta(minutes=10), 'Purpose/Notes': 'Gayatri Invocation'},
        {'Type': 'Spiritual', 'Name': 'Madhyahna Sandhya', 'Start': solar_noon - timedelta(minutes=10), 'End': solar_noon + timedelta(minutes=10), 'Purpose/Notes': 'Midday Offering'},
        {'Type': 'Spiritual', 'Name': 'Abhijit Muhurta', 'Start': solar_noon - timedelta(minutes=24), 'End': solar_noon + timedelta(minutes=24), 'Purpose/Notes': 'Victory & Initiation'},
        {'Type': 'Spiritual', 'Name': 'Sayam Sandhya', 'Start': sunset - timedelta(minutes=20), 'End': sunset + timedelta(minutes=10), 'Purpose/Notes': 'Evening Vedic Prayer'},
        {'Type': 'Spiritual', 'Name': 'Pradosha Kala', 'Start': sunset - timedelta(hours=1, minutes=30), 'End': sunset, 'Purpose/Notes': 'Shiva Worship'},
        {'Type': 'Spiritual', 'Name': 'Nishita Kala', 'Start': sunset + timedelta(hours=6), 'End': sunset + timedelta(hours=6, minutes=48), 'Purpose/Notes': 'Deep mantra practice'}
    ]

# --- CSV Export ---
def export_csv(muhurtas, filename='muhurtha_log.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Type', 'Name', 'Start', 'End', 'Purpose/Notes'])
        writer.writeheader()
        for m in muhurtas:
            writer.writerow({
                'Type': m['Type'],
                'Name': m['Name'],
                'Start': m['Start'].strftime(DATE_FORMAT),
                'End': m['End'].strftime(DATE_FORMAT),
                'Purpose/Notes': m.get('Purpose/Notes', '')
            })
            # --- Play Sound ---
def play_muhurtha_alert(name):
    tone = ALERTS.get(name)
    if tone:
        try:
            playsound(tone)
        except:
            print(f"⚠️ Could not play tone for {name}: {tone}")

# --- Build GUI ---
def build_gui(muhurtas):
    root = tk.Tk()
    root.title("🕉 Muhurtha Pulse")
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    now = datetime.now(pytz.timezone(TIMEZONE))
    panchanga = get_daily_panchanga()

    # --- Panchanga & Dasha Header ---
    tk.Label(frame, text=f"🗓 {now.strftime('%A, %d %B %Y')}", font=("Segoe UI", 11, "bold")).pack()
    tk.Label(frame, text=f"Tithi: {panchanga['tithi']} | Nakshatra: {panchanga['nakshatra']}", font=("Segoe UI", 10)).pack()
    tk.Label(frame, text=f"Masam: {panchanga['masam']} | Ruthu: {panchanga['ruthu']} | Ayana: {panchanga['ayana']}", font=("Segoe UI", 10)).pack()
    tk.Label(frame, text=f"Chandramana Masam: {panchanga['chandramana_masam']}", font=("Segoe UI", 10)).pack()
    tk.Label(frame, text=dasha_text, font=("Segoe UI", 11, "bold")).pack(pady=(10, 10))

    # --- Muhurtha Table ---
    columns = ['Type', 'Name', 'Start', 'End', 'Purpose/Notes']
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=30)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=160)

    for m in sorted(muhurtas, key=lambda x: x['Start']):
        values = [
            m['Type'],
            m['Name'],
            m['Start'].strftime('%I:%M %p'),
            m['End'].strftime('%I:%M %p'),
            m.get('Purpose/Notes', '')
        ]
        row_id = tree.insert('', tk.END, values=values)

        if m['Start'] <= now <= m['End']:
            tree.item(row_id, tags=('current',))
            if m['Name'] in ALERTS:
                play_muhurtha_alert(m['Name'])

    tree.tag_configure('current', background='#e6f7ff')
    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    root.mainloop()
    # --- Main Execution ---
if __name__ == "__main__":
    sunrise, sunset, solar_noon = get_sun_data()
    vedic = get_vedic_muhurtas(sunrise)
    spiritual = get_spiritual_muhurthas(sunrise, sunset, solar_noon)
    inauspicious = get_inauspicious_muhurthas(sunrise)

    all_muhurtas = vedic + spiritual + inauspicious
    export_csv(all_muhurtas)
    build_gui(all_muhurtas)