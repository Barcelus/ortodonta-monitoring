import os
import requests
from bs4 import BeautifulSoup

URL = "https://lucynaszymczak.pl/lista-oczekujacych/"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

STATE_FILE = "last_position.txt"


# --------------------------------------------------
# Pobierz aktualną listę
# --------------------------------------------------

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


# Znajdź właściwą tabelę
target_table = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)

    if "Pozycja" in text and "Imię" in text and "Telefon" in text:
        target_table = table
        break

if target_table is None:
    raise RuntimeError("Nie znaleziono tabeli listy oczekujących.")


# --------------------------------------------------
# Odczytaj ostatni wiersz
# --------------------------------------------------

rows = []

for row in target_table.find_all("tr"):
    cells = row.find_all("td")

    if len(cells) >= 3:
        rows.append([
            cell.get_text(" ", strip=True)
            for cell in cells[:3]
        ])

if not rows:
    raise RuntimeError("Tabela nie zawiera żadnych pozycji.")

position, name, phone = rows[-1]

print("Aktualny ostatni wpis:")
print(f"Pozycja: {position}")
print(f"Imię: {name}")
print(f"Telefon: {phone}")


# --------------------------------------------------
# Odczytaj poprzednią pozycję
# --------------------------------------------------

with open(STATE_FILE, "r", encoding="utf-8") as file:
    previous_position = file.read().strip()

print(f"Poprzednia pozycja: {previous_position}")


# --------------------------------------------------
# Sprawdź, czy zwolniło się miejsce
# --------------------------------------------------

if previous_position == "30" and position != "30":

    message = (
        "🚨 ZWOLNIŁO SIĘ MIEJSCE NA LIŚCIE!\n\n"
        f"Poprzednia ostatnia pozycja: 30\n"
        f"Obecna ostatnia pozycja: {position}\n"
        f"Osoba na pozycji {position}: {name}\n\n"
        f"Sprawdź listę:\n{URL}"
    )

    discord_response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )

    discord_response.raise_for_status()

    print("ALERT: wiadomość wysłana na Discorda.")

else:
    print("Brak zwolnienia miejsca.")


# --------------------------------------------------
# Zapisz aktualną pozycję
# --------------------------------------------------

with open(STATE_FILE, "w", encoding="utf-8") as file:
    file.write(position)

print(f"Zapisano nową pozycję: {position}")
